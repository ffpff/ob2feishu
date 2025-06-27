#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的Obsidian到飞书知识库同步测试

演示如何将Obsidian笔记完整同步到飞书知识库
支持指定目标文件夹和标签过滤
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.config import reload_config
from dotenv import load_dotenv
from src.ob2feishu.feishu_client import create_feishu_client, FeishuAPIError
from src.ob2feishu.feishu_docs import create_feishu_docs_client
from src.ob2feishu.obsidian_parser import ObsidianParser
from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
from src.ob2feishu.format_adapter import adapt_blocks_for_feishu_api


def test_sync_single_note():
    """测试同步单个笔记"""
    print("=" * 60)
    print("🚀 测试同步单个Obsidian笔记到飞书")
    print("=" * 60)
    
    try:
        # 1. 强制重新加载配置
        load_dotenv(override=True)
        config = reload_config()
        print("✓ 配置加载成功")
        
        # 2. 创建飞书客户端
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        
        if not feishu_client.test_connection():
            print("❌ 飞书API连接失败")
            return False
        print("✓ 飞书API连接成功")
        
        # 3. 创建文档操作客户端
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 4. 创建测试笔记内容
        test_note_content = f"""---
tags:
  - 飞书知识库
  - 测试
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 🧪 Obsidian同步测试笔记

这是一个测试笔记，用于验证Obsidian到飞书知识库的完整同步功能。

## 📝 功能测试清单

### 基础格式测试
- **粗体文本**和*斜体文本*
- `行内代码`和普通文本混合

### 列表测试
1. 有序列表项目1
2. 有序列表项目2
   - 嵌套无序列表
   - 另一个嵌套项目

### 代码块测试
```python
def sync_obsidian_to_feishu():
    \"\"\"同步Obsidian笔记到飞书知识库\"\"\"
    print("🚀 开始同步...")
    
    # 1. 解析笔记
    notes = parser.scan_notes()
    
    # 2. 转换格式
    blocks = convert_markdown_to_feishu(content)
    
    # 3. 同步到飞书
    docs_client.create_document(title=title)
    
    return "✅ 同步完成！"
```

### 表格测试
| 功能模块 | 状态 | 测试结果 |
|----------|------|----------|
| 飞书API客户端 | ✅ | 测试通过 |
| Obsidian解析器 | ✅ | 测试通过 |
| Markdown转换器 | ✅ | 测试通过 |
| 格式适配器 | ✅ | 测试通过 |
| 文档操作客户端 | ✅ | 测试通过 |

### 引用测试
> 这是一个引用块，用于测试引用格式的转换效果。
> 
> 支持多行引用内容。

---

**测试时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**测试状态**: 🧪 正在进行同步测试
"""
        
        print("\n📝 准备测试笔记内容...")
        print(f"内容长度: {len(test_note_content)} 字符")
        
        # 5. 转换Markdown
        print("\n🔄 转换Markdown格式...")
        internal_blocks = convert_markdown_to_feishu(test_note_content)
        print(f"✓ Markdown转换完成: 生成 {len(internal_blocks)} 个内部格式块")
        
        # 6. 适配飞书API格式
        print("🔧 适配飞书API格式...")
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 格式适配完成: 适配 {len(feishu_blocks)} 个飞书格式块")
        
        # 7. 创建飞书文档
        print("\n📄 创建飞书文档...")
        document_title = f"🧪 Obsidian同步测试 - {datetime.now().strftime('%m%d_%H%M')}"
        document = docs_client.create_document(title=document_title)
        print(f"✅ 文档创建成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        if document.url:
            print(f"   🔗 访问链接: {document.url}")
        
        # 8. 获取文档根块ID
        print("\n📋 获取文档结构...")
        blocks_info = docs_client.get_document_blocks(document.document_id)
        if not blocks_info:
            raise Exception("文档中没有块")
        
        root_block_id = blocks_info[0].get('block_id')
        print(f"📦 根块ID: {root_block_id}")
        
        # 9. 同步内容到飞书
        print("\n☁️  同步内容到飞书...")
        block_ids = docs_client.create_blocks(
            document.document_id, 
            feishu_blocks,
            parent_block_id=root_block_id
        )
        print(f"✅ 内容同步成功: 创建了 {len(block_ids)} 个内容块")
        
        print("\n🎉 单个笔记同步测试完成！")
        print(f"📄 测试文档ID: {document.document_id}")
        if document.url:
            print(f"🔗 请在飞书中查看: {document.url}")
        
        return document.document_id
        
    except Exception as e:
        print(f"❌ 同步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_sync_with_target_folder(folder_token: str = None):
    """测试同步到指定文件夹"""
    print("\n" + "=" * 60)
    print("📁 测试同步到指定知识库文件夹")
    print("=" * 60)
    
    try:
        # 1. 创建客户端
        load_dotenv(override=True)
        config = reload_config()
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 2. 准备文件夹测试内容
        folder_test_content = f"""# 📁 文件夹同步测试

这个文档测试同步到指定的飞书知识库文件夹。

## 配置信息
- **目标文件夹Token**: `{folder_token or '未指定'}`
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 功能验证
✅ 如果你在指定的文件夹中看到这个文档，说明文件夹同步功能正常！
"""
        
        # 3. 转换和适配
        print("🔄 转换内容...")
        internal_blocks = convert_markdown_to_feishu(folder_test_content)
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        
        # 4. 创建文档到指定文件夹
        print(f"📁 创建文档到文件夹: {folder_token or '根目录'}")
        document_title = f"📁 文件夹同步测试 - {datetime.now().strftime('%m%d_%H%M')}"
        
        if folder_token:
            document = docs_client.create_document(
                title=document_title,
                folder_token=folder_token
            )
        else:
            document = docs_client.create_document(title=document_title)
        
        # 5. 获取文档根块ID并添加内容
        blocks_info = docs_client.get_document_blocks(document.document_id)
        if blocks_info:
            root_block_id = blocks_info[0].get('block_id')
            block_ids = docs_client.create_blocks(
                document.document_id, 
                feishu_blocks,
                parent_block_id=root_block_id
            )
        else:
            print("⚠️  无法获取文档块结构")
            block_ids = []
        
        print(f"✅ 文件夹同步成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📁 文件夹: {folder_token or '根目录'}")
        if document.url:
            print(f"   🔗 访问链接: {document.url}")
        
        return document.document_id
        
    except Exception as e:
        print(f"❌ 文件夹同步测试失败: {e}")
        return None


def test_sync_real_obsidian_notes():
    """测试同步真实的Obsidian笔记"""
    print("\n" + "=" * 60)
    print("📚 测试同步真实Obsidian笔记")
    print("=" * 60)
    
    try:
        # 1. 创建客户端
        load_dotenv(override=True)
        config = reload_config()
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 2. 解析Obsidian笔记
        print(f"📂 扫描Obsidian库: {config.obsidian.vault_path}")
        parser = ObsidianParser(config.obsidian.vault_path)
        
        if not os.path.exists(config.obsidian.vault_path):
            print("❌ Obsidian库路径不存在")
            return False
        
        notes = parser.scan_notes()
        print(f"✓ 找到 {len(notes)} 个笔记文件")
        
        # 3. 过滤带有"飞书知识库"标签的笔记
        target_notes = []
        for note in notes:
            if "飞书知识库" in note.tags:
                target_notes.append(note)
        
        if not target_notes:
            print("⚠️  未找到包含'飞书知识库'标签的笔记")
            print("💡 建议: 在你的Obsidian笔记中添加以下标签来测试同步:")
            print("   tags:")
            print("     - 飞书知识库")
            print()
            print("或者我可以同步前几个笔记作为演示...")
            target_notes = notes[:2]  # 取前2个作为演示
        
        print(f"🎯 将同步 {len(target_notes)} 个笔记")
        
        # 4. 同步每个笔记
        synced_docs = []
        for i, note in enumerate(target_notes, 1):
            print(f"\n📝 [{i}/{len(target_notes)}] 同步笔记: {note.title}")
            print(f"   📂 文件: {note.file_path}")
            print(f"   🏷️  标签: {', '.join(note.tags)}")
            print(f"   📏 大小: {len(note.content)} 字符")
            
            try:
                # 转换内容
                internal_blocks = convert_markdown_to_feishu(note.content)
                feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
                
                # 创建文档
                doc_title = f"📚 {note.title} - {datetime.now().strftime('%m%d')}"
                document = docs_client.create_document(title=doc_title)
                
                # 添加内容
                if feishu_blocks:
                    # 获取根块ID
                    blocks_info = docs_client.get_document_blocks(document.document_id)
                    if blocks_info:
                        root_block_id = blocks_info[0].get('block_id')
                        block_ids = docs_client.create_blocks(
                            document.document_id, 
                            feishu_blocks,
                            parent_block_id=root_block_id
                        )
                        print(f"   ✅ 同步成功: {len(block_ids)} 个内容块")
                    else:
                        print(f"   ⚠️  无法获取文档块结构")
                        block_ids = []
                else:
                    print(f"   ⚠️  笔记内容为空，仅创建文档")
                    block_ids = []
                
                synced_docs.append({
                    'note': note,
                    'document': document,
                    'blocks': len(feishu_blocks) if feishu_blocks else 0
                })
                
            except Exception as e:
                print(f"   ❌ 同步失败: {e}")
        
        # 5. 总结结果
        print(f"\n🎉 真实笔记同步完成!")
        print(f"✅ 成功同步: {len(synced_docs)} 个笔记")
        print(f"📊 同步统计:")
        
        total_blocks = sum(doc['blocks'] for doc in synced_docs)
        for doc in synced_docs:
            print(f"   📄 {doc['document'].title}")
            print(f"      🆔 ID: {doc['document'].document_id}")
            print(f"      📦 块数: {doc['blocks']}")
            if doc['document'].url:
                print(f"      🔗 链接: {doc['document'].url}")
        
        print(f"\n📈 总计: {total_blocks} 个内容块")
        
        return synced_docs
        
    except Exception as e:
        print(f"❌ 真实笔记同步失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("🚀 Obsidian到飞书知识库完整同步测试")
    print("支持指定目标文件夹和标签过滤")
    print()
    
    # 检查配置
    try:
        load_dotenv(override=True)
        config = reload_config()
        print("📋 当前配置:")
        print(f"   🏢 飞书应用ID: {config.feishu.app_id}")
        print(f"   📂 Obsidian库: {config.obsidian.vault_path}")
        print(f"   🏷️  同步标签: {config.obsidian.sync_tags}")
        print()
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 测试1: 单个笔记同步
    doc1 = test_sync_single_note()
    if not doc1:
        print("❌ 基础同步测试失败，停止后续测试")
        return 1
    
    # 测试2: 指定文件夹同步（如果提供了folder_token）
    folder_token = input("\n💡 如果你想测试同步到指定文件夹，请输入folder_token（直接回车跳过）: ").strip()
    if folder_token:
        test_sync_with_target_folder(folder_token)
    else:
        print("⏭️  跳过文件夹同步测试")
    
    # 测试3: 真实笔记同步
    user_confirm = input("\n💡 是否同步真实的Obsidian笔记？(y/N): ").strip().lower()
    if user_confirm in ['y', 'yes']:
        test_sync_real_obsidian_notes()
    else:
        print("⏭️  跳过真实笔记同步测试")
    
    print("\n" + "=" * 60)
    print("🎉 所有同步测试完成！")
    print("💡 请在飞书知识库中查看同步结果")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main()) 