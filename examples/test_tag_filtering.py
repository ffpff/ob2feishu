#!/usr/bin/env python3
"""
标签过滤功能演示脚本

演示如何通过添加"飞书知识库"标签来实现笔记过滤和同步
"""

import os
import sys
import tempfile
import shutil
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


def create_demo_vault_with_tags():
    """创建包含飞书知识库标签的演示库"""
    temp_dir = Path(tempfile.mkdtemp(prefix="demo_obsidian_"))
    
    print(f"📁 创建演示Obsidian库: {temp_dir}")
    
    # 创建包含不同标签的测试笔记
    demo_notes = [
        {
            "filename": "有飞书标签的笔记.md",
            "content": """---
title: 有飞书标签的笔记
tags: ["飞书知识库", "重要笔记"]
---

# 有飞书标签的笔记

这个笔记包含 **飞书知识库** 标签，应该被同步。

## 内容特点

- 包含重要信息
- 需要在飞书中分享
- 团队协作相关

#工作流程 #团队协作
"""
        },
        {
            "filename": "另一个飞书笔记.md",
            "content": """---
tags: "飞书知识库, AI编程, 工作经验"
---

# AI编程经验分享

这也是一个需要同步到飞书的笔记。

## 核心经验

1. 使用AI提升编程效率
2. 最佳实践总结
3. 工具推荐

#AI编程 #经验分享
"""
        },
        {
            "filename": "私人笔记.md",
            "content": """# 私人笔记

这个笔记没有飞书知识库标签，不应该被同步。

包含个人信息：
- 个人计划
- 私人想法
- 密码记录等

#个人 #私密
"""
        },
        {
            "filename": "混合标签笔记.md",
            "content": """---
title: 混合标签笔记
tags: ["工作", "学习"]
---

# 学习笔记

这个笔记虽然有标签，但没有"飞书知识库"标签。

## 学习内容

- Python编程
- 数据分析
- 机器学习

会被解析但不会被同步。

#学习计划 #飞书知识库
"""
        }
    ]
    
    # 创建测试文件
    for note in demo_notes:
        file_path = temp_dir / note["filename"]
        file_path.write_text(note["content"], encoding='utf-8')
        print(f"  📄 创建文件: {note['filename']}")
    
    print(f"✅ 演示库创建完成，包含 {len(demo_notes)} 个文件")
    return temp_dir


def demo_tag_filtering():
    """演示标签过滤功能"""
    print("🧪 飞书知识库标签过滤演示")
    print("=" * 60)
    
    # 创建演示库
    demo_vault = create_demo_vault_with_tags()
    
    try:
        # 创建解析器
        parser = create_obsidian_parser(
            vault_path=str(demo_vault),
            sync_tags=["飞书知识库"],
            exclude_folders=[".obsidian"],
            exclude_patterns=["*.tmp"]
        )
        
        print(f"\n📂 演示库路径: {demo_vault}")
        print(f"🏷️  同步标签: ['飞书知识库']")
        
        # 1. 扫描所有文件
        print(f"\n📋 扫描所有Markdown文件...")
        scanned_files = list(parser.scan_vault())
        print(f"找到 {len(scanned_files)} 个文件:")
        for file_path in scanned_files:
            print(f"  📄 {file_path.name}")
        
        # 2. 解析所有笔记
        print(f"\n📝 解析所有笔记...")
        all_notes = []
        for file_path in scanned_files:
            note = parser.parse_note(file_path)
            if note:
                all_notes.append(note)
                print(f"  ✅ {note.title}")
                print(f"     标签: {note.tags}")
                print(f"     包含'飞书知识库': {'✓' if '飞书知识库' in note.tags else '✗'}")
        
        print(f"\n总共解析了 {len(all_notes)} 个笔记")
        
        # 3. 应用标签过滤
        print(f"\n🏷️  应用标签过滤（匹配'飞书知识库'）...")
        filtered_notes = parser.filter_notes_by_tags(all_notes)
        
        print(f"过滤结果: {len(filtered_notes)}/{len(all_notes)} 个笔记匹配")
        print(f"\n匹配的笔记:")
        for note in filtered_notes:
            matching_tags = [tag for tag in note.tags if tag in ["飞书知识库"]]
            print(f"  🚀 {note.title}")
            print(f"     匹配标签: {matching_tags}")
            print(f"     所有标签: {note.tags}")
            print(f"     文件大小: {note.file_size} 字节")
        
        # 4. 获取需要同步的笔记
        print(f"\n🔄 获取需要同步的笔记...")
        sync_notes = parser.get_notes_for_sync()
        print(f"需要同步: {len(sync_notes)} 个笔记")
        
        for note in sync_notes:
            print(f"  📤 {note.title}")
            print(f"     文件: {note.file_path.name}")
            print(f"     需要同步原因: {'首次同步' if not note.feishu_document_id else '内容已更新'}")
        
        # 5. 模拟同步过程
        if sync_notes:
            print(f"\n📝 模拟同步过程...")
            first_note = sync_notes[0]
            print(f"模拟同步笔记: {first_note.title}")
            
            # 模拟同步成功，更新元数据
            success = parser.update_sync_metadata(first_note, "demo_doc_123")
            if success:
                print(f"✅ 同步元数据更新成功")
                print(f"   飞书文档ID: {first_note.feishu_document_id}")
                print(f"   同步时间: {first_note.feishu_last_sync}")
                
                # 重新检查同步状态
                updated_note = parser.parse_note(first_note.file_path)
                print(f"   文件更新验证: {'✓' if updated_note.feishu_document_id else '✗'}")
        
        # 6. 统计分析
        print(f"\n📊 标签统计分析...")
        all_tags = set()
        tag_counts = {}
        
        for note in all_notes:
            for tag in note.tags:
                all_tags.add(tag)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print(f"发现的所有标签 ({len(all_tags)} 个):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            indicator = "🎯" if tag == "飞书知识库" else "📝"
            print(f"  {indicator} {tag}: {count} 次")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理演示文件
        print(f"\n🧹 清理演示文件...")
        shutil.rmtree(demo_vault)
        print("✅ 清理完成")


def demo_real_vault_with_tag_addition():
    """演示如何在真实库中添加标签"""
    print("\n💡 在真实Obsidian库中使用飞书同步的方法:")
    print("=" * 60)
    
    print("1️⃣ **在笔记开头添加YAML front-matter:**")
    print("""
```yaml
---
title: 笔记标题
tags: ["飞书知识库", "其他标签"]
---
```
""")
    
    print("2️⃣ **或者在内容中添加hashtag:**")
    print("""
在笔记内容中任意位置添加: #飞书知识库
""")
    
    print("3️⃣ **推荐的标签组合:**")
    recommendations = [
        "飞书知识库 + 工作流程",
        "飞书知识库 + 团队分享", 
        "飞书知识库 + 项目文档",
        "飞书知识库 + 学习笔记",
        "飞书知识库 + 会议记录"
    ]
    
    for rec in recommendations:
        print(f"  • {rec}")
    
    print("\n4️⃣ **验证标签是否生效:**")
    print("使用命令检查: python3 examples/test_real_obsidian.py")


def main():
    """主函数"""
    print("🎯 Obsidian标签过滤功能完整演示")
    print("=" * 60)
    
    # 运行演示
    success = demo_tag_filtering()
    
    if success:
        # 提供使用指导
        demo_real_vault_with_tag_addition()
        
        print(f"\n🎉 演示完成！")
        print(f"\n📋 演示要点总结:")
        print(f"  ✅ 标签解析：支持YAML metadata和内容中的#标签")
        print(f"  ✅ 智能过滤：只同步包含'飞书知识库'标签的笔记") 
        print(f"  ✅ 状态管理：跟踪同步状态，避免重复同步")
        print(f"  ✅ 元数据更新：自动在文件中记录同步信息")
        print(f"  ✅ 中文支持：完美处理中文标签和文件名")
        
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 