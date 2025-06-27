#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书块格式调试脚本

调试具体的块格式问题
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.ob2feishu.config import reload_config
from src.ob2feishu.feishu_client import create_feishu_client
from src.ob2feishu.feishu_docs import create_feishu_docs_client
from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
from src.ob2feishu.format_adapter import adapt_blocks_for_feishu_api


def test_simple_text_block():
    """测试最简单的文本块"""
    print("🔍 测试最简单的文本块")
    print("=" * 50)
    
    try:
        # 加载配置
        load_dotenv(override=True)
        config = reload_config()
        
        # 创建客户端
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 创建测试文档
        document_title = f"🔍 块格式测试 - {datetime.now().strftime('%m%d_%H%M%S')}"
        document = docs_client.create_document(title=document_title)
        
        # 获取根块ID
        blocks_info = docs_client.get_document_blocks(document.document_id)
        root_block_id = blocks_info[0].get('block_id')
        
        print(f"✅ 文档创建成功: {document.document_id}")
        print(f"📦 根块ID: {root_block_id}")
        
        # 测试1: 最简单的文本块（按照官方文档格式）
        simple_text_block = {
            "block_type": 2,  # 文本块
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是最简单的测试文本",
                            "text_element_style": {}
                        }
                    }
                ]
            }
        }
        
        print(f"\n📝 测试简单文本块:")
        print(f"   格式: {json.dumps(simple_text_block, ensure_ascii=False, indent=2)}")
        
        block_ids = docs_client.create_blocks(
            document.document_id,
            [simple_text_block],
            parent_block_id=root_block_id
        )
        
        print(f"✅ 简单文本块成功: {block_ids}")
        
        return document, root_block_id
        
    except Exception as e:
        print(f"❌ 简单文本块失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_markdown_conversion():
    """测试Markdown转换过程"""
    print("\n🔍 测试Markdown转换过程")
    print("=" * 50)
    
    # 简单的测试内容
    test_markdown = """# 标题1

这是一段普通文本。

## 标题2

- 列表项1
- 列表项2

**粗体文本**

这是另一段文本。
"""
    
    print(f"📝 原始Markdown:")
    print(test_markdown)
    print("-" * 30)
    
    try:
        # 转换为内部格式
        print("🔄 转换为内部格式...")
        internal_blocks = convert_markdown_to_feishu(test_markdown)
        
        print(f"✅ 内部格式生成: {len(internal_blocks)} 个块")
        for i, block in enumerate(internal_blocks):
            print(f"   [{i+1}] 类型 {block.get('block_type')}: {str(block)[:80]}...")
        
        # 这些块已经是飞书API格式了，不需要再适配
        print(f"\n📋 完整飞书格式:")
        print(json.dumps(internal_blocks, ensure_ascii=False, indent=2))
        
        return internal_blocks
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_feishu_blocks_with_real_content(document, root_block_id, feishu_blocks):
    """使用真实转换的内容测试飞书块"""
    print("\n🔍 测试转换后的飞书块")
    print("=" * 50)
    
    if not document or not feishu_blocks:
        print("❌ 缺少必要的参数")
        return False
    
    try:
        # 加载配置
        load_dotenv(override=True)
        config = reload_config()
        
        # 创建客户端
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        print(f"📄 文档: {document.document_id}")
        print(f"📦 根块: {root_block_id}")
        print(f"🧱 块数量: {len(feishu_blocks)}")
        
        # 逐个测试块
        success_count = 0
        for i, block in enumerate(feishu_blocks):
            print(f"\n📝 测试块 [{i+1}/{len(feishu_blocks)}]:")
            print(f"   类型: {block.get('block_type')}")
            print(f"   内容: {str(block)[:100]}...")
            
            try:
                block_ids = docs_client.create_blocks(
                    document.document_id,
                    [block],  # 一次只测试一个块
                    parent_block_id=root_block_id
                )
                
                print(f"   ✅ 成功: 块ID {block_ids}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                print(f"   📋 块详情: {json.dumps(block, ensure_ascii=False, indent=4)}")
        
        print(f"\n📊 测试结果: {success_count}/{len(feishu_blocks)} 个块成功")
        return success_count == len(feishu_blocks)
        
    except Exception as e:
        print(f"❌ 批量测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 飞书块格式调试工具")
    print("逐步分析块格式问题")
    print()
    
    # 测试1: 简单文本块
    document, root_block_id = test_simple_text_block()
    if not document:
        print("\n❌ 简单文本块测试失败，停止后续测试")
        return 1
    
    # 测试2: Markdown转换
    feishu_blocks = test_markdown_conversion()
    if not feishu_blocks:
        print("\n❌ Markdown转换失败，停止后续测试")
        return 1
    
    # 测试3: 真实内容测试
    success = test_feishu_blocks_with_real_content(document, root_block_id, feishu_blocks)
    
    print("\n" + "=" * 60)
    print("🏁 调试结果总结")
    print(f"   简单文本块: {'✅ 成功' if document else '❌ 失败'}")
    print(f"   Markdown转换: {'✅ 成功' if feishu_blocks else '❌ 失败'}")
    print(f"   真实内容测试: {'✅ 成功' if success else '❌ 失败'}")
    
    if document and feishu_blocks and success:
        print(f"\n🎉 所有测试通过！")
        print(f"📄 测试文档ID: {document.document_id}")
        if document.url:
            print(f"🔗 请在飞书中查看: {document.url}")
        return 0
    else:
        print(f"\n💡 有测试失败，请检查具体错误信息")
        return 1


if __name__ == "__main__":
    exit(main()) 