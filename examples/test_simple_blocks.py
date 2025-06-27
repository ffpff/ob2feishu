#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正确的飞书块格式

使用飞书API官方文档中的格式
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


def test_official_formats():
    """测试飞书官方文档中的格式"""
    print("🔍 测试飞书官方文档格式")
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
        document_title = f"🔍 官方格式测试 - {datetime.now().strftime('%m%d_%H%M%S')}"
        document = docs_client.create_document(title=document_title)
        
        # 获取根块ID
        blocks_info = docs_client.get_document_blocks(document.document_id)
        root_block_id = blocks_info[0].get('block_id')
        
        print(f"✅ 文档创建成功: {document.document_id}")
        print(f"📦 根块ID: {root_block_id}")
        
        # 测试各种块格式
        test_cases = [
            {
                "name": "普通文本",
                "block": {
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": "这是一段普通文本",
                                    "text_element_style": {}
                                }
                            }
                        ],
                        "style": {}
                    }
                }
            },
            {
                "name": "粗体文本",
                "block": {
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": "这是粗体文本",
                                    "text_element_style": {
                                        "bold": True
                                    }
                                }
                            }
                        ],
                        "style": {}
                    }
                }
            },
            {
                "name": "模拟标题（大号粗体文本）",
                "block": {
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": "标题：测试文档",
                                    "text_element_style": {
                                        "bold": True
                                    }
                                }
                            }
                        ],
                        "style": {}
                    }
                }
            },
            {
                "name": "混合格式文本",
                "block": {
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": "这里有 ",
                                    "text_element_style": {}
                                }
                            },
                            {
                                "text_run": {
                                    "content": "粗体",
                                    "text_element_style": {
                                        "bold": True
                                    }
                                }
                            },
                            {
                                "text_run": {
                                    "content": " 和 ",
                                    "text_element_style": {}
                                }
                            },
                            {
                                "text_run": {
                                    "content": "斜体",
                                    "text_element_style": {
                                        "italic": True
                                    }
                                }
                            },
                            {
                                "text_run": {
                                    "content": " 文本",
                                    "text_element_style": {}
                                }
                            }
                        ],
                        "style": {}
                    }
                }
            }
        ]
        
        # 逐个测试
        success_count = 0
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试块 [{i}/{len(test_cases)}]: {test_case['name']}")
            try:
                block_ids = docs_client.create_blocks(
                    document.document_id,
                    [test_case['block']],
                    parent_block_id=root_block_id
                )
                
                print(f"   ✅ 成功: 块ID {block_ids}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                print(f"   📋 块详情: {json.dumps(test_case['block'], ensure_ascii=False, indent=4)}")
        
        print(f"\n📊 测试结果: {success_count}/{len(test_cases)} 个块成功")
        
        if success_count == len(test_cases):
            print(f"\n🎉 所有测试通过！")
            print(f"📄 测试文档ID: {document.document_id}")
            if document.url:
                print(f"🔗 请在飞书中查看: {document.url}")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 飞书官方格式测试工具")
    print("验证正确的块格式")
    print()
    
    success = test_official_formats()
    
    if success:
        print(f"\n🎯 下一步: 基于成功的格式重写转换器")
        return 0
    else:
        print(f"\n💡 需要进一步调试格式问题")
        return 1


if __name__ == "__main__":
    exit(main()) 