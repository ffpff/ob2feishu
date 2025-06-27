#!/usr/bin/env python3
"""
调试API请求问题
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ob2feishu.config import get_config
from ob2feishu.feishu_client import FeishuClient, FeishuConfig
from ob2feishu.feishu_docs import FeishuDocsClient
from ob2feishu.markdown_converter import convert_markdown_to_feishu
from ob2feishu.format_adapter import FeishuFormatAdapter
import json
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

def debug_simple_api_request():
    """调试简单的API请求"""
    
    print("🔍 调试API请求问题")
    print("=" * 50)
    
    # 1. 加载配置
    config = get_config()
    
    # 创建FeishuConfig对象
    feishu_config = FeishuConfig(
        app_id=config.feishu.app_id,
        app_secret=config.feishu.app_secret,
        base_url=config.feishu.api_base_url,
        timeout=config.feishu.api_timeout
    )
    
    client = FeishuClient(feishu_config)
    docs_client = FeishuDocsClient(client)
    
    # 2. 测试连接
    print("1. 测试连接...")
    if not client.test_connection():
        print("❌ 连接失败")
        return
    print("✓ 连接成功")
    
    # 3. 创建一个简单的文档测试
    print("\n2. 创建文档...")
    try:
        doc = docs_client.create_document("API调试测试文档")
        doc_id = doc.document_id
        print(f"✓ 文档创建成功: {doc_id}")
    except Exception as e:
        print(f"❌ 文档创建失败: {e}")
        return
    
    # 4. 创建最简单的块
    print("\n3. 创建简单文本块...")
    simple_blocks = [
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是一个简单的测试文本",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {}
            }
        }
    ]
    
    print("请求数据:")
    print(json.dumps(simple_blocks, ensure_ascii=False, indent=2))
    
    try:
        block_ids = docs_client.create_blocks(doc_id, simple_blocks, parent_block_id=doc_id)
        print(f"✓ 简单块创建成功: {block_ids}")
    except Exception as e:
        print(f"❌ 简单块创建失败: {e}")
        
        # 如果失败，尝试创建更简单的块
        print("\n4. 尝试更简单的块...")
        minimal_blocks = [
            {
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "测试",
                                "text_element_style": {}
                            }
                        }
                    ],
                    "style": {}
                }
            }
        ]
        
        try:
            block_ids = docs_client.create_blocks(doc_id, minimal_blocks, parent_block_id=doc_id)
            print(f"✓ 最简块创建成功: {block_ids}")
        except Exception as e2:
            print(f"❌ 最简块也失败: {e2}")
            return
    
    # 5. 测试代码块
    print("\n5. 测试代码块...")
    code_blocks = [
        {
            "block_type": 10,
            "code": {
                "language": "python",
                "elements": [
                    {
                        "text_run": {
                            "content": "print('hello')"
                        }
                    }
                ]
            }
        }
    ]
    
    print("代码块请求数据:")
    print(json.dumps(code_blocks, ensure_ascii=False, indent=2))
    
    try:
        block_ids = docs_client.create_blocks(doc_id, code_blocks, parent_block_id=doc_id)
        print(f"✓ 代码块创建成功: {block_ids}")
    except Exception as e:
        print(f"❌ 代码块创建失败: {e}")
    
    print(f"\n📄 测试文档ID: {doc_id}")
    print("你可以在飞书中查看这个文档")

if __name__ == "__main__":
    debug_simple_api_request() 