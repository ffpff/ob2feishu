"""
Markdown到飞书格式转换器模块
将Obsidian的Markdown内容转换为飞书文档的Block结构
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeishuBlockType(Enum):
    """飞书块类型枚举"""
    PAGE = 1            # 页面
    TEXT = 2            # 文本  
    HEADING1 = 3        # 标题1
    HEADING2 = 4        # 标题2
    HEADING3 = 5        # 标题3
    HEADING4 = 6        # 标题4
    HEADING5 = 7        # 标题5
    HEADING6 = 8        # 标题6
    BULLET_LIST = 9     # 无序列表
    ORDERED_LIST = 10   # 有序列表
    CODE_BLOCK = 11     # 代码块
    QUOTE = 12          # 引用
    EQUATION = 13       # 公式
    TODO = 14           # 待办事项
    BITABLE = 15        # 多维表格
    CALLOUT = 16        # 高亮块
    CHAT_CARD = 17      # 群聊卡片
    DIAGRAM = 18        # 流程图
    DIVIDER = 19        # 分割线
    FILE = 20           # 文件
    GRID = 21           # 分栏
    GRID_COLUMN = 22    # 分栏列
    IFRAME = 23         # 内嵌
    IMAGE = 24          # 图片
    ISV = 25            # ISV
    MINDNOTE = 26       # 思维导图
    SHEET = 27          # 电子表格
    TABLE = 28          # 表格
    TABLE_CELL = 29     # 表格单元格
    VIEW = 30           # 视图
    QUOTE_CONTAINER = 31 # 引用容器


@dataclass
class FeishuTextElement:
    """飞书文本元素"""
    text: str
    style: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        element = {"text": self.text}
        if self.style:
            element["style"] = self.style
        return element


@dataclass
class FeishuBlock:
    """飞书文档块"""
    block_type: FeishuBlockType
    text_elements: List[FeishuTextElement] = None
    children: List['FeishuBlock'] = None
    extra: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.text_elements is None:
            self.text_elements = []
        if self.children is None:
            self.children = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为飞书API所需的字典格式"""
        block_data = {
            "block_type": self.block_type.value
        }
        
        # 添加文本内容
        if self.text_elements:
            block_data["text"] = {
                "elements": [element.to_dict() for element in self.text_elements],
                "style": {}
            }
        
        # 添加子块
        if self.children:
            block_data["children"] = [child.to_dict() for child in self.children]
        
        # 添加额外属性
        if self.extra:
            block_data.update(self.extra)
            
        return block_data


class MarkdownConverter:
    """Markdown到飞书格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.reset()
    
    def reset(self):
        """重置转换器状态"""
        self.blocks = []
        self.current_list_stack = []  # 用于处理嵌套列表
        self.in_code_block = False
        self.code_block_content = []
        self.code_block_language = ""
        
    def convert(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        将Markdown内容转换为飞书块结构
        
        Args:
            markdown_content: Markdown文本内容
            
        Returns:
            飞书块结构的字典列表
        """
        self.reset()
        
        # 预处理：移除YAML front-matter
        processed_content = self._remove_frontmatter(markdown_content)
        
        lines = processed_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            i += self._process_line(line, lines, i)
            
        # 处理未完成的代码块
        if self.in_code_block:
            self._finish_code_block()
            
        # 处理未完成的列表
        self._finish_all_lists()
        
        return [block.to_dict() for block in self.blocks]
    
    def _remove_frontmatter(self, content: str) -> str:
        """
        移除YAML front-matter
        
        Args:
            content: 原始Markdown内容
            
        Returns:
            移除front-matter后的内容
        """
        lines = content.split('\n')
        
        # 检查是否以---开头（YAML front-matter标识）
        if not lines or lines[0].strip() != '---':
            return content
        
        # 查找结束的---
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            # 没有找到结束标记，返回原内容
            return content
        
        # 返回去除front-matter的内容
        return '\n'.join(lines[end_index + 1:])
    
    
    def _process_line(self, line: str, lines: List[str], line_index: int) -> int:
        """
        处理单行内容
        
        Args:
            line: 当前行内容
            lines: 所有行
            line_index: 当前行索引
            
        Returns:
            跳过的行数（通常为1）
        """
        # 处理代码块
        if line.strip().startswith('```'):
            if self.in_code_block:
                self._finish_code_block()
                return 1
            else:
                self._start_code_block(line.strip())
                return 1
        
        if self.in_code_block:
            self.code_block_content.append(line)
            return 1
        
        # 处理标题
        if line.startswith('#'):
            self._finish_all_lists()
            self._process_heading(line)
            return 1
        
        # 处理分割线
        if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', line.strip()):
            self._finish_all_lists()
            self._add_divider()
            return 1
        
        # 处理列表
        list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
        if list_match:
            return self._process_list_item(list_match, line)
        
        # 处理引用
        if line.strip().startswith('>'):
            self._finish_all_lists()
            self._process_quote(line)
            return 1
        
        # 处理空行
        if not line.strip():
            self._finish_all_lists()
            return 1
        
        # 处理表格
        if '|' in line and line.strip().startswith('|'):
            table_lines = self._collect_table_lines(lines, line_index)
            if len(table_lines) >= 2:  # 至少要有标题行和分隔行
                self._finish_all_lists()
                self._process_table(table_lines)
                return len(table_lines)
        
        # 处理普通段落
        self._finish_all_lists()
        self._process_paragraph(line)
        return 1
    
    def _process_heading(self, line: str):
        """处理标题行"""
        # 计算标题级别
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break
        
        # 提取标题文本
        title_text = line[level:].strip()
        
        # 确定飞书标题类型
        if level == 1:
            block_type = FeishuBlockType.HEADING1
        elif level == 2:
            block_type = FeishuBlockType.HEADING2
        elif level == 3:
            block_type = FeishuBlockType.HEADING3
        elif level == 4:
            block_type = FeishuBlockType.HEADING4
        elif level == 5:
            block_type = FeishuBlockType.HEADING5
        else:  # level >= 6
            block_type = FeishuBlockType.HEADING6
        
        # 处理标题中的内联格式
        text_elements = self._parse_inline_formatting(title_text)
        
        # 创建标题块
        heading_block = FeishuBlock(
            block_type=block_type,
            text_elements=text_elements
        )
        
        self.blocks.append(heading_block)
        logger.debug(f"添加标题: {title_text} (级别 {level})")
    
    def _process_paragraph(self, line: str):
        """处理段落"""
        if not line.strip():
            return
            
        # 处理内联格式
        text_elements = self._parse_inline_formatting(line.strip())
        
        # 创建文本块
        text_block = FeishuBlock(
            block_type=FeishuBlockType.TEXT,
            text_elements=text_elements
        )
        
        self.blocks.append(text_block)
        logger.debug(f"添加段落: {line.strip()[:50]}...")
    
    def _process_list_item(self, match, line: str) -> int:
        """处理列表项"""
        indent = len(match.group(1))
        marker = match.group(2)
        content = match.group(3)
        
        # 判断列表类型
        is_ordered = marker.endswith('.')
        
        # 处理列表层级
        self._handle_list_nesting(indent, is_ordered)
        
        # 处理内联格式
        text_elements = self._parse_inline_formatting(content)
        
        # 创建列表项块
        list_item_block = FeishuBlock(
            block_type=FeishuBlockType.TEXT,
            text_elements=text_elements
        )
        
        # 添加到当前列表
        if self.current_list_stack:
            current_list = self.current_list_stack[-1]
            current_list.children.append(list_item_block)
        
        logger.debug(f"添加列表项: {content} (缩进 {indent})")
        return 1
    
    def _handle_list_nesting(self, indent: int, is_ordered: bool):
        """处理列表嵌套"""
        # 简化的嵌套处理：目前只支持一级列表
        if not self.current_list_stack:
            # 创建新列表
            list_type = FeishuBlockType.ORDERED_LIST if is_ordered else FeishuBlockType.BULLET_LIST
            list_block = FeishuBlock(block_type=list_type)
            self.blocks.append(list_block)
            self.current_list_stack.append(list_block)
    
    def _finish_all_lists(self):
        """完成所有未完成的列表"""
        self.current_list_stack.clear()
    
    def _process_quote(self, line: str):
        """处理引用"""
        # 移除引用标记
        quote_text = line.strip()[1:].strip()
        
        # 处理内联格式
        text_elements = self._parse_inline_formatting(quote_text)
        
        # 创建引用块
        quote_block = FeishuBlock(
            block_type=FeishuBlockType.QUOTE,
            text_elements=text_elements
        )
        
        self.blocks.append(quote_block)
        logger.debug(f"添加引用: {quote_text}")
    
    def _start_code_block(self, line: str):
        """开始代码块"""
        self.in_code_block = True
        self.code_block_content = []
        
        # 提取语言标识
        lang_match = re.match(r'^```(\w+)?', line)
        if lang_match and lang_match.group(1):
            self.code_block_language = lang_match.group(1)
        else:
            self.code_block_language = ""
    
    def _finish_code_block(self):
        """完成代码块"""
        self.in_code_block = False
        
        # 合并代码内容
        code_content = '\n'.join(self.code_block_content)
        
        # 创建代码块
        code_block = FeishuBlock(
            block_type=FeishuBlockType.CODE_BLOCK,
            text_elements=[FeishuTextElement(text=code_content)],
            extra={
                "code": {
                    "language": self.code_block_language or "plain"
                }
            }
        )
        
        self.blocks.append(code_block)
        logger.debug(f"添加代码块: {self.code_block_language} ({len(code_content)} 字符)")
        
        # 重置状态
        self.code_block_content = []
        self.code_block_language = ""
    
    def _add_divider(self):
        """添加分割线"""
        divider_block = FeishuBlock(block_type=FeishuBlockType.DIVIDER)
        self.blocks.append(divider_block)
        logger.debug("添加分割线")
    
    def _collect_table_lines(self, lines: List[str], start_index: int) -> List[str]:
        """收集表格行"""
        table_lines = []
        i = start_index
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('|') and line.endswith('|'):
                table_lines.append(line)
                i += 1
            else:
                break
        
        return table_lines
    
    def _process_table(self, table_lines: List[str]):
        """处理表格"""
        if len(table_lines) < 2:
            return
        
        # 解析表头
        header_row = self._parse_table_row(table_lines[0])
        
        # 跳过分隔行
        data_rows = []
        for line in table_lines[2:]:
            row = self._parse_table_row(line)
            if row:
                data_rows.append(row)
        
        # 创建表格块
        table_block = FeishuBlock(
            block_type=FeishuBlockType.TABLE,
            extra={
                "table": {
                    "header": header_row,
                    "rows": data_rows
                }
            }
        )
        
        self.blocks.append(table_block)
        logger.debug(f"添加表格: {len(header_row)} 列, {len(data_rows)} 行")
    
    def _parse_table_row(self, line: str) -> List[str]:
        """解析表格行"""
        # 移除首尾的 |
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        
        # 分割单元格
        cells = [cell.strip() for cell in line.split('|')]
        return cells
    
    def _parse_inline_formatting(self, text: str) -> List[FeishuTextElement]:
        """
        解析内联格式（粗体、斜体、代码等）
        
        Args:
            text: 待解析的文本
            
        Returns:
            飞书文本元素列表
        """
        elements = []
        
        # 简化版本：首先处理基本情况
        if not text:
            return elements
        
        # 使用正则表达式匹配各种格式
        patterns = [
            (r'\*\*(.+?)\*\*', {'bold': True}),           # 粗体
            (r'__(.+?)__', {'bold': True}),               # 粗体（下划线）
            (r'\*(.+?)\*', {'italic': True}),             # 斜体
            (r'_(.+?)_', {'italic': True}),               # 斜体（下划线）
            (r'`(.+?)`', {'code': True}),                 # 行内代码
            (r'\[(.+?)\]\((.+?)\)', None),                # 链接 [text](url)
        ]
        
        # 简化处理：如果没有特殊格式，直接返回纯文本
        has_formatting = any(re.search(pattern, text) for pattern, _ in patterns)
        
        if not has_formatting:
            elements.append(FeishuTextElement(text=text))
            return elements
        
        # 复杂格式处理（当前简化版本）
        # TODO: 实现完整的内联格式解析
        # 暂时作为纯文本处理，后续可以增强
        elements.append(FeishuTextElement(text=text))
        
        return elements


def create_markdown_converter() -> MarkdownConverter:
    """创建Markdown转换器的便捷函数"""
    return MarkdownConverter()


def convert_markdown_to_feishu(markdown_content: str) -> List[Dict[str, Any]]:
    """
    将Markdown内容转换为飞书块结构的便捷函数
    
    Args:
        markdown_content: Markdown文本内容
        
    Returns:
        飞书块结构的字典列表
    """
    converter = create_markdown_converter()
    return converter.convert(markdown_content) 