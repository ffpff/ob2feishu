#!/usr/bin/env python3
"""
Obsidian解析器测试脚本

用于测试Obsidian文件解析、标签过滤等功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ob2feishu.obsidian_parser import create_obsidian_parser, ObsidianNote
from ob2feishu.config import get_config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_test_vault():
    """创建测试用的Obsidian库"""
    temp_dir = Path(tempfile.mkdtemp(prefix="obsidian_test_"))
    
    print(f"📁 创建测试Obsidian库: {temp_dir}")
    
    # 创建测试笔记
    test_notes = [
        {
            "filename": "note1.md",
            "content": """---
title: 飞书知识库测试笔记
tags: ["飞书知识库", "测试"]
---

# 飞书知识库测试笔记

这是一个包含飞书知识库标签的测试笔记。

## 内容

- 支持 **粗体** 和 *斜体*
- 支持代码块：`print("Hello World")`
- 支持列表

#内容标签 #测试
"""
        },
        {
            "filename": "note2.md", 
            "content": """# 另一个测试笔记

这个笔记包含不同的标签 #其他标签 #example

没有飞书知识库标签，应该被过滤掉。
"""
        },
        {
            "filename": "subdir/note3.md",
            "content": """---
tags: "飞书知识库,工作笔记"
---

# 子目录中的笔记

这个笔记在子目录中，也包含飞书知识库标签。

内容包含中文标签 #工作 #项目管理
"""
        },
        {
            "filename": ".obsidian/config.json",
            "content": '{"version": "1.0"}'
        },
        {
            "filename": "templates/template.md",
            "content": "# 模板文件\n这是模板，应该被排除"
        },
        {
            "filename": "draft-test.md",
            "content": "# 草稿文件\n这是草稿，应该被排除"
        }
    ]
    
    # 创建测试文件
    for note in test_notes:
        file_path = temp_dir / note["filename"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(note["content"], encoding='utf-8')
        print(f"  📄 创建文件: {note['filename']}")
    
    print(f"✅ 测试库创建完成，包含 {len(test_notes)} 个文件")
    return temp_dir


def test_obsidian_parser(vault_path: Path):
    """测试Obsidian解析器功能"""
    print("\n🔍 测试Obsidian解析器功能")
    print("=" * 50)
    
    # 创建解析器
    parser = create_obsidian_parser(
        vault_path=str(vault_path),
        sync_tags=["飞书知识库"],
        exclude_folders=[".obsidian", "templates"],
        exclude_patterns=["*.tmp", "draft-*"]
    )
    
    print(f"📂 Obsidian库路径: {parser.vault_path}")
    print(f"🏷️  同步标签: {parser.config.sync_tags}")
    
    # 1. 测试库扫描
    print("\n📋 扫描Obsidian库...")
    scanned_files = list(parser.scan_vault())
    print(f"找到 {len(scanned_files)} 个Markdown文件:")
    for file_path in scanned_files:
        try:
            relative_path = file_path.relative_to(vault_path)
            print(f"  📄 {relative_path}")
        except ValueError:
            print(f"  📄 {file_path}")
    
    # 2. 测试笔记解析
    print("\n📝 解析笔记内容...")
    all_notes = []
    for file_path in scanned_files:
        note = parser.parse_note(file_path)
        if note:
            all_notes.append(note)
            print(f"✅ {note.title}")
            print(f"   标签: {note.tags}")
            print(f"   内容长度: {len(note.content)} 字符")
            print(f"   是否需要同步: {'是' if note.needs_sync else '否'}")
        else:
            print(f"❌ 解析失败: {file_path}")
    
    print(f"\n总共解析了 {len(all_notes)} 个笔记")
    
    # 3. 测试标签过滤
    print("\n🏷️  测试标签过滤...")
    filtered_notes = parser.filter_notes_by_tags(all_notes)
    print(f"匹配同步标签的笔记: {len(filtered_notes)} 个")
    
    for note in filtered_notes:
        print(f"  ✅ {note.title}")
        print(f"     匹配标签: {[tag for tag in note.tags if tag in parser.config.sync_tags]}")
    
    # 4. 测试获取需要同步的笔记
    print("\n🔄 获取需要同步的笔记...")
    sync_notes = parser.get_notes_for_sync()
    print(f"需要同步的笔记: {len(sync_notes)} 个")
    
    for note in sync_notes:
        print(f"  🚀 {note.title}")
        print(f"     文件: {note.file_path.name}")
        print(f"     大小: {note.file_size} 字节")
        print(f"     修改时间: {note.modified_time}")
        print(f"     内容哈希: {note.content_hash[:8]}...")
    
    # 5. 测试同步元数据更新
    if sync_notes:
        print("\n📝 测试同步元数据更新...")
        test_note = sync_notes[0]
        print(f"测试笔记: {test_note.title}")
        
        # 模拟同步
        success = parser.update_sync_metadata(test_note, "test_doc_123")
        if success:
            print("✅ 同步元数据更新成功")
            print(f"   飞书文档ID: {test_note.feishu_document_id}")
            print(f"   同步时间: {test_note.feishu_last_sync}")
            print(f"   同步版本: {test_note.feishu_sync_version}")
            
            # 重新解析验证
            updated_note = parser.parse_note(test_note.file_path)
            if updated_note and updated_note.feishu_document_id:
                print("✅ 文件元数据验证成功")
            else:
                print("❌ 文件元数据验证失败")
        else:
            print("❌ 同步元数据更新失败")
    
    return sync_notes


def main():
    """主函数"""
    print("🧪 Obsidian解析器功能测试")
    print("=" * 50)
    
    # 创建测试库
    vault_path = create_test_vault()
    
    try:
        # 测试解析器功能
        sync_notes = test_obsidian_parser(vault_path)
        
        print(f"\n🎉 测试完成！")
        print(f"📊 统计信息:")
        print(f"   - 扫描的笔记数量: {len(list(vault_path.glob('**/*.md')))}")
        print(f"   - 解析成功的笔记: 取决于过滤条件")
        print(f"   - 需要同步的笔记: {len(sync_notes)}")
        
        print(f"\n💡 测试要点:")
        print(f"   ✅ 文件扫描和过滤")
        print(f"   ✅ YAML front-matter解析")
        print(f"   ✅ 标签提取（metadata + 内容)")
        print(f"   ✅ 标题提取（优先级：metadata > H1 > 文件名）")
        print(f"   ✅ 按标签过滤笔记")
        print(f"   ✅ 同步状态检测")
        print(f"   ✅ 同步元数据更新")
        
        return 0
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return 1
        
    finally:
        # 清理测试文件
        print(f"\n🧹 清理测试文件...")
        import shutil
        shutil.rmtree(vault_path)
        print("✅ 清理完成")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 