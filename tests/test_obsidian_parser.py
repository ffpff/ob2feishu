"""
Obsidian解析器测试模块
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open

from ob2feishu.obsidian_parser import (
    ObsidianNote,
    ObsidianParserConfig,
    ObsidianParser,
    create_obsidian_parser
)


class TestObsidianNote:
    """测试ObsidianNote类"""
    
    def test_note_creation(self):
        """测试笔记对象创建"""
        # 创建临时文件用于测试
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Note\n\nContent here")
            temp_path = Path(f.name)
        
        try:
            note = ObsidianNote(
                file_path=temp_path,
                title="Test Note",
                content="# Test Note\n\nContent here",
                tags=["test", "example"]
            )
            
            assert note.title == "Test Note"
            assert note.content == "# Test Note\n\nContent here"
            assert note.tags == ["test", "example"]
            assert note.created_time is not None
            assert note.modified_time is not None
            assert note.file_size > 0
            
        finally:
            temp_path.unlink()
    
    def test_note_properties(self):
        """测试笔记属性"""
        note = ObsidianNote(
            file_path=Path("/fake/path.md"),
            title="Test",
            content="Content"
        )
        
        # 测试未同步状态
        assert not note.is_synced_to_feishu
        assert note.needs_sync
        
        # 设置同步信息
        note.feishu_document_id = "doc123"
        note.feishu_last_sync = datetime.now()
        
        assert note.is_synced_to_feishu
        # 由于没有真实文件，modified_time为None，应该仍需要同步
        assert note.needs_sync
    
    def test_content_hash(self):
        """测试内容哈希计算"""
        note = ObsidianNote(
            file_path=Path("/fake/path.md"),
            title="Test Title",
            content="Test Content"
        )
        
        hash1 = note.calculate_content_hash()
        assert hash1 == note.content_hash
        assert len(hash1) == 32  # MD5哈希长度
        
        # 修改内容后哈希应该不同
        note.content = "Modified Content"
        hash2 = note.calculate_content_hash()
        assert hash2 != hash1


class TestObsidianParserConfig:
    """测试ObsidianParserConfig类"""
    
    def test_config_creation(self):
        """测试配置创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ObsidianParserConfig(
                vault_path=temp_dir,
                sync_tags=["test"]
            )
            
            assert config.vault_path == temp_dir
            assert config.sync_tags == ["test"]
            assert ".obsidian" in config.exclude_folders
            assert config.include_subdirs is True
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试不存在的路径
        with pytest.raises(ValueError, match="Obsidian库路径不存在"):
            ObsidianParserConfig(vault_path="/non/existent/path")
        
        # 测试文件路径（而非目录）
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValueError, match="Obsidian库路径不是目录"):
                ObsidianParserConfig(vault_path=temp_file.name)


class TestObsidianParser:
    """测试ObsidianParser类"""
    
    def setup_method(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config = ObsidianParserConfig(
            vault_path=str(self.temp_dir),
            sync_tags=["飞书知识库", "test"],
            exclude_folders=[".obsidian", "templates"],
            exclude_patterns=["*.tmp", "draft-*"]
        )
        self.parser = ObsidianParser(self.config)
    
    def teardown_method(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """创建测试文件"""
        file_path = self.temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_parser_initialization(self):
        """测试解析器初始化"""
        assert self.parser.vault_path == self.temp_dir.resolve()
        assert self.parser.config.sync_tags == ["飞书知识库", "test"]
        assert len(self.parser._exclude_patterns) == 2
    
    def test_should_exclude_path(self):
        """测试路径排除逻辑"""
        # 创建测试文件
        normal_file = self.temp_dir / "normal.md"
        obsidian_file = self.temp_dir / ".obsidian" / "config.json"
        template_file = self.temp_dir / "templates" / "template.md"
        tmp_file = self.temp_dir / "test.tmp"
        draft_file = self.temp_dir / "draft-test.md"
        
        # 创建目录
        obsidian_file.parent.mkdir(exist_ok=True)
        template_file.parent.mkdir(exist_ok=True)
        
        assert not self.parser._should_exclude_path(normal_file)
        assert self.parser._should_exclude_path(obsidian_file)
        assert self.parser._should_exclude_path(template_file)
        assert self.parser._should_exclude_path(tmp_file)
        assert self.parser._should_exclude_path(draft_file)
    
    def test_should_include_extension(self):
        """测试文件扩展名检查"""
        md_file = Path("test.md")
        markdown_file = Path("test.markdown")
        txt_file = Path("test.txt")
        
        assert self.parser._should_include_extension(md_file)
        assert self.parser._should_include_extension(markdown_file)
        assert not self.parser._should_include_extension(txt_file)
    
    def test_scan_vault(self):
        """测试库扫描功能"""
        # 创建测试文件
        self.create_test_file("note1.md", "# Note 1")
        self.create_test_file("note2.markdown", "# Note 2")
        self.create_test_file("subdir/note3.md", "# Note 3")
        self.create_test_file(".obsidian/config.json", "{}")
        self.create_test_file("draft-test.md", "# Draft")
        self.create_test_file("test.txt", "Not markdown")
        
        files = list(self.parser.scan_vault())
        file_names = [f.name for f in files]
        
        assert "note1.md" in file_names
        assert "note2.markdown" in file_names
        assert "note3.md" in file_names
        assert "config.json" not in file_names
        assert "draft-test.md" not in file_names
        assert "test.txt" not in file_names
    
    def test_extract_title(self):
        """测试标题提取"""
        # 测试从metadata提取
        title1 = self.parser._extract_title(
            "Content here",
            {"title": "Metadata Title"},
            Path("test.md")
        )
        assert title1 == "Metadata Title"
        
        # 测试从H1标题提取
        title2 = self.parser._extract_title(
            "# H1 Title\nContent here",
            {},
            Path("test.md")
        )
        assert title2 == "H1 Title"
        
        # 测试从文件名提取
        title3 = self.parser._extract_title(
            "Content without title",
            {},
            Path("filename-title.md")
        )
        assert title3 == "filename-title"
    
    def test_extract_tags(self):
        """测试标签提取"""
        # 测试从metadata提取（列表格式）
        tags1 = self.parser._extract_tags(
            {"tags": ["tag1", "tag2"]},
            "Content here"
        )
        assert set(tags1) == {"tag1", "tag2"}
        
        # 测试从metadata提取（字符串格式）
        tags2 = self.parser._extract_tags(
            {"tags": "tag1, tag2, tag3"},
            "Content here"
        )
        assert set(tags2) == {"tag1", "tag2", "tag3"}
        
        # 测试从内容提取
        tags3 = self.parser._extract_tags(
            {},
            "Content with #tag1 and #tag2 hashtags"
        )
        assert set(tags3) == {"tag1", "tag2"}
        
        # 测试中文标签
        tags4 = self.parser._extract_tags(
            {},
            "Content with #中文标签 and #English"
        )
        assert set(tags4) == {"中文标签", "English"}
    
    def test_parse_note_with_frontmatter(self):
        """测试解析带frontmatter的笔记"""
        content = """---
title: Test Note
tags: ["飞书知识库", "test"]
feishu_document_id: doc123
feishu_last_sync: "2024-01-01T10:00:00Z"
feishu_sync_version: 1
---

# Test Note

This is test content with #hashtag."""
        
        file_path = self.create_test_file("test.md", content)
        note = self.parser.parse_note(file_path)
        
        assert note is not None
        assert note.title == "Test Note"
        assert set(note.tags) == {"飞书知识库", "test", "hashtag"}
        assert note.feishu_document_id == "doc123"
        assert note.feishu_sync_version == 1
        assert note.feishu_last_sync is not None
    
    def test_parse_note_without_frontmatter(self):
        """测试解析无frontmatter的笔记"""
        content = """# Simple Note

This is a simple note with #tag1 and #tag2."""
        
        file_path = self.create_test_file("simple.md", content)
        note = self.parser.parse_note(file_path)
        
        assert note is not None
        assert note.title == "Simple Note"
        assert set(note.tags) == {"tag1", "tag2"}
        assert note.feishu_document_id is None
        assert note.feishu_sync_version == 0
    
    def test_filter_notes_by_tags(self):
        """测试按标签过滤笔记"""
        notes = [
            ObsidianNote(
                file_path=Path("note1.md"),
                title="Note 1",
                content="Content",
                tags=["飞书知识库", "other"]
            ),
            ObsidianNote(
                file_path=Path("note2.md"),
                title="Note 2", 
                content="Content",
                tags=["test", "example"]
            ),
            ObsidianNote(
                file_path=Path("note3.md"),
                title="Note 3",
                content="Content",
                tags=["unrelated"]
            )
        ]
        
        filtered = self.parser.filter_notes_by_tags(notes)
        
        # 应该匹配包含"飞书知识库"或"test"标签的笔记
        assert len(filtered) == 2
        titles = [note.title for note in filtered]
        assert "Note 1" in titles
        assert "Note 2" in titles
        assert "Note 3" not in titles
    
    def test_update_sync_metadata(self):
        """测试更新同步元数据"""
        # 创建测试文件
        original_content = """---
title: Test Note
tags: ["test"]
---

# Test Note

Content here."""
        
        file_path = self.create_test_file("test.md", original_content)
        note = self.parser.parse_note(file_path)
        
        # 更新同步元数据
        success = self.parser.update_sync_metadata(note, "doc123")
        assert success
        
        # 验证文件内容已更新
        updated_content = file_path.read_text(encoding='utf-8')
        assert "feishu_document_id: doc123" in updated_content
        assert "feishu_last_sync:" in updated_content
        assert "feishu_sync_version: 1" in updated_content
        
        # 验证笔记对象已更新
        assert note.feishu_document_id == "doc123"
        assert note.feishu_last_sync is not None
        assert note.feishu_sync_version == 1


class TestCreateObsidianParser:
    """测试便捷函数"""
    
    def test_create_obsidian_parser(self):
        """测试创建解析器的便捷函数"""
        with tempfile.TemporaryDirectory() as temp_dir:
            parser = create_obsidian_parser(
                vault_path=temp_dir,
                sync_tags=["test"],
                exclude_folders=["custom"]
            )
            
            assert isinstance(parser, ObsidianParser)
            assert parser.config.vault_path == temp_dir
            assert parser.config.sync_tags == ["test"]
            assert "custom" in parser.config.exclude_folders 