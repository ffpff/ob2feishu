#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书知识库操作模块演示脚本

展示如何使用FeishuDocsClient进行各种文档操作：
- 创建文档
- 获取文档信息
- 创建和更新内容块
- 批量操作
- 文档内容替换
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.config import get_config
from src.ob2feishu.feishu_client import FeishuClient
from src.ob2feishu.feishu_docs import FeishuDocsClient, create_feishu_docs_client
from src.ob2feishu.format_adapter import adapt_blocks_for_feishu_api


def test_basic_document_operations():
    """测试基本文档操作"""
    print("=" * 60)
    print("测试飞书知识库基本操作")
    print("=" * 60)
    
    try:
        # 1. 加载配置
        config = get_config()
        print("✓ 配置加载成功")
        
        # 2. 创建飞书客户端
        feishu_client = FeishuClient(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        print("✓ 飞书客户端创建成功")
        
        # 3. 测试连接
        if not feishu_client.test_connection():
            print("❌ 飞书API连接失败")
            return False
        print("✓ 飞书API连接成功")
        
        # 4. 创建文档操作客户端
        docs_client = create_feishu_docs_client(feishu_client)
        print("✓ 文档操作客户端创建成功")
        
        # 5. 创建测试文档
        print("\n📝 创建测试文档...")
        document = docs_client.create_document(title="🧪 Ob2Feishu 知识库操作测试")
        print(f"✅ 文档创建成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 文档标题: {document.title}")
        print(f"   🔢 版本号: {document.revision_id}")
        if document.url:
            print(f"   🔗 访问链接: {document.url}")
        
        # 6. 获取文档信息验证
        print("\n📋 验证文档信息...")
        doc_info = docs_client.get_document_info(document.document_id)
        print(f"✅ 文档信息获取成功:")
        print(f"   📄 标题: {doc_info.title}")
        print(f"   🔢 版本: {doc_info.revision_id}")
        
        # 7. 创建示例内容块
        print("\n📝 添加内容块...")
        sample_blocks = [
            {
                "block_type": 3,  # 标题2
                "heading2": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "🚀 功能测试报告",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 2,  # 文本段落
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "本文档用于测试 Ob2Feishu 工具的飞书知识库操作功能。以下是各项功能的测试结果：\n\n",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 9,  # 无序列表
                "bullet": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "✅ 文档创建功能正常",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 9,  # 无序列表
                "bullet": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "✅ 文档信息获取正常",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 9,  # 无序列表
                "bullet": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "✅ 内容块添加功能正常",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            }
        ]
        
        # 创建内容块
        block_ids = docs_client.create_blocks(document.document_id, sample_blocks)
        print(f"✅ 内容块创建成功: 共创建 {len(block_ids)} 个块")
        
        # 8. 获取文档内容验证
        print("\n📋 验证文档内容...")
        blocks = docs_client.get_document_blocks(document.document_id)
        print(f"✅ 文档内容获取成功: 共 {len(blocks)} 个块")
        
        # 9. 更新文档标题
        print("\n📝 更新文档标题...")
        new_title = "🎉 Ob2Feishu 知识库操作测试 - 已完成"
        docs_client.update_document_title(document.document_id, new_title)
        print(f"✅ 标题更新成功: {new_title}")
        
        print(f"\n🎉 所有基本操作测试完成！")
        print(f"📄 测试文档ID: {document.document_id}")
        if document.url:
            print(f"🔗 请在飞书中查看: {document.url}")
        
        return document.document_id
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_content_replacement(document_id: str):
    """测试内容替换功能"""
    print("\n" + "=" * 60)
    print("测试文档内容替换")
    print("=" * 60)
    
    try:
        # 1. 创建客户端
        config = get_config()
        feishu_client = FeishuClient(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 2. 准备新的内容
        print("📝 准备新内容...")
        new_content = [
            {
                "block_type": 3,  # 标题2
                "heading2": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "🔄 内容替换测试",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 2,  # 文本段落
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是替换后的新内容。原有内容已被完全替换。\n\n",
                                "text_element_style": {}
                            }
                        },
                        {
                            "text_run": {
                                "content": "替换时间: ",
                                "text_element_style": {}
                            }
                        },
                        {
                            "text_run": {
                                "content": f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "text_element_style": {
                                    "bold": True
                                }
                            }
                        }
                    ]
                }
            },
            {
                "block_type": 10,  # 代码块
                "code": {
                    "language": "python",
                    "elements": [
                        {
                            "text_run": {
                                "content": "# 这是一个代码块示例\nprint('内容替换功能测试成功！')\n\n# 支持多种编程语言\ndef hello_world():\n    return 'Hello, Feishu!'",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            }
        ]
        
        # 3. 执行内容替换
        print("🔄 执行内容替换...")
        new_block_ids = docs_client.replace_document_content(document_id, new_content)
        print(f"✅ 内容替换成功: 创建了 {len(new_block_ids)} 个新块")
        
        # 4. 验证替换结果
        print("📋 验证替换结果...")
        blocks = docs_client.get_document_blocks(document_id)
        print(f"✅ 验证成功: 文档现在包含 {len(blocks)} 个块")
        
        print("🎉 内容替换测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 内容替换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_markdown_integration(document_id: str):
    """测试与Markdown转换器的集成"""
    print("\n" + "=" * 60)
    print("测试Markdown集成")
    print("=" * 60)
    
    try:
        # 1. 创建客户端
        config = get_config()
        feishu_client = FeishuClient(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 2. 准备Markdown内容
        markdown_content = """# Markdown集成测试

这是一个**Markdown**格式的文档，将被转换为飞书格式。

## 功能特性

- 支持各种*标题*级别
- 支持**粗体**和*斜体*文本
- 支持列表项目

### 代码示例

```python
def convert_and_sync():
    # 1. 转换Markdown
    blocks = convert_markdown_to_feishu(markdown_content)
    
    # 2. 适配飞书格式
    feishu_blocks = adapt_blocks_for_feishu_api(blocks)
    
    # 3. 同步到飞书
    docs_client.replace_document_content(doc_id, feishu_blocks)
    
    return "同步完成！"
```

### 表格支持

| 功能 | 状态 | 说明 |
|------|------|------|
| 标题转换 | ✅ | 支持H1-H6 |
| 文本格式 | ✅ | 粗体、斜体 |
| 列表 | ✅ | 有序、无序 |
| 代码块 | ✅ | 语法高亮 |
| 表格 | ✅ | 基础表格 |

> 这是一个引用块，用于展示引用格式的转换效果。

---

**测试完成时间**: """ + f"{__import__('datetime').datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
        
        # 3. 导入转换器模块
        from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
        
        # 4. 转换Markdown
        print("🔄 转换Markdown内容...")
        internal_blocks = convert_markdown_to_feishu(markdown_content)
        print(f"✓ Markdown转换完成: 生成 {len(internal_blocks)} 个内部格式块")
        
        # 5. 适配飞书API格式
        print("🔧 适配飞书API格式...")
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 格式适配完成: 适配 {len(feishu_blocks)} 个飞书格式块")
        
        # 6. 同步到飞书
        print("☁️  同步到飞书知识库...")
        block_ids = docs_client.replace_document_content(document_id, feishu_blocks)
        print(f"✅ 同步完成: 创建了 {len(block_ids)} 个块")
        
        # 7. 更新文档标题
        new_title = "📝 Markdown集成测试 - 完整流程验证"
        docs_client.update_document_title(document_id, new_title)
        print(f"✓ 标题更新: {new_title}")
        
        print("🎉 Markdown集成测试完成！")
        print("🔗 请在飞书中查看转换效果")
        
        return True
        
    except Exception as e:
        print(f"❌ Markdown集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始飞书知识库操作测试")
    
    # 1. 测试基本操作
    document_id = test_basic_document_operations()
    if not document_id:
        print("❌ 基本操作测试失败，停止后续测试")
        return 1
    
    # 2. 测试内容替换
    if not test_content_replacement(document_id):
        print("⚠️  内容替换测试失败")
    
    # 3. 测试Markdown集成
    if not test_markdown_integration(document_id):
        print("⚠️  Markdown集成测试失败")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print(f"📄 测试文档ID: {document_id}")
    print("💡 请在飞书知识库中查看测试结果")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main()) 