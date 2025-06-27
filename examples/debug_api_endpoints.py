#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API端点调试脚本

用于调试具体的API端点问题
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


def test_document_creation():
    """测试文档创建"""
    print("🔍 测试文档创建")
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
        
        # 测试文档创建
        print("📄 创建测试文档...")
        document_title = f"🔍 API测试文档 - {datetime.now().strftime('%m%d_%H%M%S')}"
        
        # 尝试不指定文件夹创建
        print(f"   标题: {document_title}")
        document = docs_client.create_document(title=document_title)
        
        print(f"✅ 文档创建成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   🔄 版本: {document.revision_id}")
        if document.url:
            print(f"   🔗 链接: {document.url}")
        
        return document
        
    except Exception as e:
        print(f"❌ 文档创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_simple_content_addition(document):
    """测试简单内容添加"""
    print("\n🔍 测试简单内容添加")
    print("=" * 50)
    
    if not document:
        print("❌ 没有有效的文档")
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
        
        # 首先获取文档的块结构，找到根块ID
        print(f"📋 获取文档块结构...")
        blocks_info = docs_client.get_document_blocks(document.document_id)
        
        if not blocks_info:
            print("❌ 文档中没有块")
            return False
        
        # 文档的第一个块通常是根块（页面块）
        root_block = blocks_info[0]
        root_block_id = root_block.get('block_id')
        print(f"📦 根块ID: {root_block_id}")
        print(f"📦 根块类型: {root_block.get('block_type')}")
        
        # 创建一个简单的文本块
        simple_blocks = [
            {
                "block_type": 2,  # 文本块
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是一个简单的测试文本。",
                                "text_element_style": {}
                            }
                        }
                    ]
                }
            }
        ]
        
        print(f"📝 添加简单文本到文档 {document.document_id}")
        print(f"   父块ID: {root_block_id}")
        print(f"   内容: {json.dumps(simple_blocks, ensure_ascii=False, indent=2)}")
        
        # 尝试添加内容到根块
        block_ids = docs_client.create_blocks(
            document.document_id, 
            simple_blocks,
            parent_block_id=root_block_id
        )
        
        print(f"✅ 内容添加成功:")
        print(f"   📦 创建的块ID: {block_ids}")
        
        return True
        
    except Exception as e:
        print(f"❌ 内容添加失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_info_retrieval(document):
    """测试文档信息获取"""
    print("\n🔍 测试文档信息获取")
    print("=" * 50)
    
    if not document:
        print("❌ 没有有效的文档")
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
        
        # 获取文档信息
        print(f"📋 获取文档信息: {document.document_id}")
        doc_info = docs_client.get_document_info(document.document_id)
        
        print(f"✅ 文档信息获取成功:")
        print(f"   📄 文档ID: {doc_info.document_id}")
        print(f"   📝 标题: {doc_info.title}")
        print(f"   🔄 版本: {doc_info.revision_id}")
        if doc_info.url:
            print(f"   🔗 链接: {doc_info.url}")
        
        # 获取文档块信息
        print(f"\n📦 获取文档块信息...")
        blocks = docs_client.get_document_blocks(document.document_id)
        
        print(f"✅ 文档块信息获取成功:")
        print(f"   📦 块数量: {len(blocks)}")
        
        for i, block in enumerate(blocks[:3]):  # 显示前3个块
            print(f"   [{i+1}] 块ID: {block.get('block_id', 'N/A')}")
            print(f"       类型: {block.get('block_type', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文档信息获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 飞书API端点调试工具")
    print("用于诊断具体的API调用问题")
    print()
    
    # 测试1: 文档创建
    document = test_document_creation()
    if not document:
        print("\n❌ 文档创建失败，无法继续后续测试")
        return 1
    
    # 测试2: 文档信息获取
    info_success = test_document_info_retrieval(document)
    
    # 测试3: 简单内容添加
    content_success = test_simple_content_addition(document)
    
    print("\n" + "=" * 60)
    print("🏁 调试结果总结")
    print(f"   文档创建: {'✅ 成功' if document else '❌ 失败'}")
    print(f"   信息获取: {'✅ 成功' if info_success else '❌ 失败'}")
    print(f"   内容添加: {'✅ 成功' if content_success else '❌ 失败'}")
    
    if document and info_success and content_success:
        print(f"\n🎉 所有API测试通过！")
        print(f"📄 测试文档ID: {document.document_id}")
        if document.url:
            print(f"🔗 请在飞书中查看: {document.url}")
        return 0
    else:
        print(f"\n💡 有API调用失败，请检查具体错误信息")
        return 1


if __name__ == "__main__":
    exit(main()) 