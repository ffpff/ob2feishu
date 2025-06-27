"""
Obsidian文件解析器模块
处理Obsidian笔记的扫描、解析和过滤功能
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Generator
from dataclasses import dataclass, field
from datetime import datetime

import frontmatter
import logging

logger = logging.getLogger(__name__)


@dataclass
class ObsidianNote:
    """Obsidian笔记数据结构"""
    file_path: Path
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None
    file_size: int = 0
    content_hash: str = ""
    
    # 飞书同步相关字段
    feishu_document_id: Optional[str] = None
    feishu_last_sync: Optional[datetime] = None
    feishu_sync_version: int = 0
    
    def __post_init__(self):
        """初始化后处理"""
        if self.file_path and self.file_path.exists():
            stat = self.file_path.stat()
            self.created_time = datetime.fromtimestamp(stat.st_ctime)
            self.modified_time = datetime.fromtimestamp(stat.st_mtime)
            self.file_size = stat.st_size
            
    @property
    def relative_path(self) -> str:
        """获取相对路径字符串"""
        return str(self.file_path)
    
    @property
    def is_synced_to_feishu(self) -> bool:
        """检查是否已同步到飞书"""
        return bool(self.feishu_document_id)
    
    @property
    def needs_sync(self) -> bool:
        """检查是否需要同步"""
        if not self.is_synced_to_feishu:
            return True
        
        if not self.feishu_last_sync:
            return True
        
        # 如果没有文件修改时间，默认需要同步
        if not self.modified_time:
            return True
            
        # 比较文件修改时间和最后同步时间
        return self.modified_time > self.feishu_last_sync
    
    def calculate_content_hash(self) -> str:
        """计算内容哈希"""
        content_for_hash = f"{self.title}\n{self.content}".encode('utf-8')
        self.content_hash = hashlib.md5(content_for_hash).hexdigest()
        return self.content_hash


@dataclass 
class ObsidianParserConfig:
    """Obsidian解析器配置"""
    vault_path: str
    sync_tags: List[str] = field(default_factory=list)
    exclude_folders: List[str] = field(default_factory=lambda: [".obsidian", ".trash", "templates"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.tmp", "draft-*"])
    include_subdirs: bool = True
    file_extensions: List[str] = field(default_factory=lambda: [".md", ".markdown"])
    
    def __post_init__(self):
        """验证配置"""
        vault_path = Path(self.vault_path)
        if not vault_path.exists():
            raise ValueError(f"Obsidian库路径不存在: {self.vault_path}")
        if not vault_path.is_dir():
            raise ValueError(f"Obsidian库路径不是目录: {self.vault_path}")


class ObsidianParser:
    """Obsidian文件解析器"""
    
    def __init__(self, config: ObsidianParserConfig):
        """
        初始化解析器
        
        Args:
            config: 解析器配置
        """
        self.config = config
        self.vault_path = Path(config.vault_path).resolve()
        
        # 编译排除模式的正则表达式
        self._exclude_patterns = []
        for pattern in config.exclude_patterns:
            # 将通配符模式转换为正则表达式
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            self._exclude_patterns.append(re.compile(regex_pattern))
        
        logger.info(f"初始化Obsidian解析器: {self.vault_path}")
        logger.info(f"同步标签: {config.sync_tags}")
        logger.info(f"排除文件夹: {config.exclude_folders}")
        logger.info(f"排除模式: {config.exclude_patterns}")
    
    def _should_exclude_path(self, path: Path) -> bool:
        """
        检查路径是否应该被排除
        
        Args:
            path: 文件路径
            
        Returns:
            是否排除
        """
        # 检查是否在排除文件夹中
        try:
            # 先解析路径以处理符号链接和相对路径
            resolved_path = path.resolve()
            resolved_vault_path = self.vault_path.resolve()
            
            relative_path = resolved_path.relative_to(resolved_vault_path)
            path_parts = relative_path.parts
            
            # 检查任何父目录是否在排除列表中
            for folder in self.config.exclude_folders:
                if folder in path_parts:
                    return True
            
            # 检查文件名是否匹配排除模式
            filename = path.name
            for pattern in self._exclude_patterns:
                if pattern.match(filename):
                    return True
                    
            return False
            
        except ValueError:
            # 路径不在vault_path下，排除
            return True
    
    def _should_include_extension(self, path: Path) -> bool:
        """
        检查文件扩展名是否应该包含
        
        Args:
            path: 文件路径
            
        Returns:
            是否包含
        """
        return path.suffix.lower() in self.config.file_extensions
    
    def scan_vault(self) -> Generator[Path, None, None]:
        """
        扫描Obsidian库中的所有Markdown文件
        
        Yields:
            符合条件的文件路径
        """
        logger.info(f"开始扫描Obsidian库: {self.vault_path}")
        
        file_count = 0
        excluded_count = 0
        
        # 使用rglob或glob根据配置决定是否包含子目录
        if self.config.include_subdirs:
            pattern = "**/*"
        else:
            pattern = "*"
            
        for path in self.vault_path.glob(pattern):
            if not path.is_file():
                continue
                
            # 检查文件扩展名
            if not self._should_include_extension(path):
                continue
                
            # 检查是否应该排除
            if self._should_exclude_path(path):
                excluded_count += 1
                logger.debug(f"排除文件: {path.relative_to(self.vault_path)}")
                continue
            
            file_count += 1
            logger.debug(f"找到文件: {path.relative_to(self.vault_path)}")
            yield path
        
        logger.info(f"扫描完成: 找到 {file_count} 个文件，排除 {excluded_count} 个文件")
    
    def parse_note(self, file_path: Path) -> Optional[ObsidianNote]:
        """
        解析单个笔记文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的笔记对象，失败返回None
        """
        try:
            # 安全地获取相对路径用于日志
            try:
                relative_path = file_path.relative_to(self.vault_path)
                logger.debug(f"解析笔记: {relative_path}")
            except ValueError:
                logger.debug(f"解析笔记: {file_path}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 使用frontmatter解析YAML front-matter
            post = frontmatter.loads(file_content)
            content = post.content
            metadata = post.metadata
            
            # 提取标题
            title = self._extract_title(content, metadata, file_path)
            
            # 提取标签
            tags = self._extract_tags(metadata, content)
            
            # 创建笔记对象
            note = ObsidianNote(
                file_path=file_path,
                title=title,
                content=content,
                metadata=metadata,
                tags=tags
            )
            
            # 从metadata中提取飞书同步信息
            self._extract_feishu_sync_info(note)
            
            # 计算内容哈希
            note.calculate_content_hash()
            
            logger.debug(f"笔记解析成功: {title}, 标签: {tags}")
            return note
            
        except Exception as e:
            logger.error(f"解析笔记失败 {file_path}: {str(e)}")
            return None
    
    def _extract_title(self, content: str, metadata: Dict[str, Any], file_path: Path) -> str:
        """
        提取笔记标题
        
        优先级：metadata.title > 第一个H1标题 > 文件名
        """
        # 1. 检查metadata中的title
        if 'title' in metadata and metadata['title']:
            return str(metadata['title']).strip()
        
        # 2. 检查内容中的第一个H1标题
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                if title:
                    return title
        
        # 3. 使用文件名（去掉扩展名）
        return file_path.stem
    
    def _extract_tags(self, metadata: Dict[str, Any], content: str) -> List[str]:
        """
        提取标签
        
        支持多种标签格式：
        - YAML front-matter: tags: [tag1, tag2] 或 tags: "tag1, tag2"
        - 内容中的标签: #tag1 #tag2
        """
        tags = set()
        
        # 1. 从metadata中提取标签
        if 'tags' in metadata:
            meta_tags = metadata['tags']
            
            if isinstance(meta_tags, list):
                tags.update(str(tag).strip() for tag in meta_tags)
            elif isinstance(meta_tags, str):
                # 支持逗号分隔的字符串
                tag_list = [tag.strip() for tag in meta_tags.split(',')]
                tags.update(tag for tag in tag_list if tag)
        
        # 2. 从内容中提取标签（#tag格式）
        tag_pattern = r'#([a-zA-Z0-9\u4e00-\u9fff_-]+)'
        content_tags = re.findall(tag_pattern, content)
        tags.update(content_tags)
        
        # 转换为列表并排序
        return sorted(list(tags))
    
    def _extract_feishu_sync_info(self, note: ObsidianNote) -> None:
        """
        从metadata中提取飞书同步信息
        
        Args:
            note: 笔记对象
        """
        metadata = note.metadata
        
        # 提取飞书文档ID
        if 'feishu_document_id' in metadata:
            note.feishu_document_id = metadata['feishu_document_id']
        
        # 提取最后同步时间
        if 'feishu_last_sync' in metadata:
            sync_time = metadata['feishu_last_sync']
            if isinstance(sync_time, str):
                try:
                    note.feishu_last_sync = datetime.fromisoformat(sync_time.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"无法解析同步时间: {sync_time}")
            elif isinstance(sync_time, datetime):
                note.feishu_last_sync = sync_time
        
        # 提取同步版本
        if 'feishu_sync_version' in metadata:
            try:
                note.feishu_sync_version = int(metadata['feishu_sync_version'])
            except (ValueError, TypeError):
                note.feishu_sync_version = 0
    
    def filter_notes_by_tags(self, notes: List[ObsidianNote]) -> List[ObsidianNote]:
        """
        根据配置的标签过滤笔记
        
        Args:
            notes: 笔记列表
            
        Returns:
            过滤后的笔记列表
        """
        if not self.config.sync_tags:
            # 如果没有配置同步标签，返回所有笔记
            return notes
        
        filtered_notes = []
        sync_tags_set = set(self.config.sync_tags)
        
        for note in notes:
            note_tags_set = set(note.tags)
            
            # 检查是否有交集
            if sync_tags_set.intersection(note_tags_set):
                filtered_notes.append(note)
                logger.debug(f"笔记匹配同步标签: {note.title}")
            else:
                logger.debug(f"笔记不匹配同步标签: {note.title}, 笔记标签: {note.tags}")
        
        logger.info(f"标签过滤完成: {len(filtered_notes)}/{len(notes)} 个笔记匹配")
        return filtered_notes
    
    def get_notes_for_sync(self) -> List[ObsidianNote]:
        """
        获取需要同步的笔记
        
        Returns:
            需要同步的笔记列表
        """
        logger.info("开始获取需要同步的笔记")
        
        # 1. 扫描所有文件
        all_notes = []
        for file_path in self.scan_vault():
            note = self.parse_note(file_path)
            if note:
                all_notes.append(note)
        
        logger.info(f"总共解析了 {len(all_notes)} 个笔记")
        
        # 2. 根据标签过滤
        filtered_notes = self.filter_notes_by_tags(all_notes)
        
        # 3. 进一步过滤需要同步的笔记
        sync_notes = []
        for note in filtered_notes:
            if note.needs_sync:
                sync_notes.append(note)
                logger.debug(f"需要同步: {note.title}")
            else:
                logger.debug(f"无需同步: {note.title}")
        
        logger.info(f"最终需要同步的笔记: {len(sync_notes)} 个")
        return sync_notes
    
    def update_sync_metadata(self, note: ObsidianNote, document_id: str) -> bool:
        """
        更新笔记的同步元数据
        
        Args:
            note: 笔记对象
            document_id: 飞书文档ID
            
        Returns:
            更新是否成功
        """
        try:
            # 读取原始文件
            with open(note.file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 解析frontmatter
            post = frontmatter.loads(file_content)
            
            # 更新同步信息
            post.metadata['feishu_document_id'] = document_id
            post.metadata['feishu_last_sync'] = datetime.now().isoformat() + 'Z'
            post.metadata['feishu_sync_version'] = note.feishu_sync_version + 1
            
            # 写回文件
            updated_content = frontmatter.dumps(post)
            with open(note.file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # 更新笔记对象
            note.feishu_document_id = document_id
            note.feishu_last_sync = datetime.now()
            note.feishu_sync_version += 1
            
            logger.info(f"更新同步元数据成功: {note.title}")
            return True
            
        except Exception as e:
            note_title = note.title if note else "未知笔记"
            logger.error(f"更新同步元数据失败 {note_title}: {str(e)}")
            return False


def create_obsidian_parser(vault_path: str, sync_tags: List[str] = None, **kwargs) -> ObsidianParser:
    """
    创建Obsidian解析器的便捷函数
    
    Args:
        vault_path: Obsidian库路径
        sync_tags: 同步标签列表
        **kwargs: 其他配置参数
        
    Returns:
        配置好的Obsidian解析器
    """
    config = ObsidianParserConfig(
        vault_path=vault_path,
        sync_tags=sync_tags or [],
        **kwargs
    )
    return ObsidianParser(config) 