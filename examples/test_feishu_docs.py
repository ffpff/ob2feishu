#!/usr/bin/env python3
"""
飞书文档API测试脚本

用于测试基本的飞书文档操作功能
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ob2feishu.feishu_client import create_feishu_client, FeishuAPIError
from ob2feishu.config import get_config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    print("📄 飞书文档API测试工具")
    print("=" * 50)
    
    # 加载配置
    try:
        config = get_config()
        feishu_config = config.get('feishu', {})
        
        app_id = feishu_config.get('app_id')
        app_secret = feishu_config.get('app_secret')
        
        if not app_id or not app_secret:
            print("❌ 错误: 未找到飞书应用配置")
            return 1
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 创建飞书客户端
    try:
        print(f"🔧 创建飞书客户端...")
        client = create_feishu_client(app_id, app_secret)
        
        # 首先测试认证
        if not client.test_connection():
            print("❌ 认证失败！请先配置正确的应用凭据。")
            return 1
            
    except Exception as e:
        print(f"❌ 创建客户端失败: {e}")
        return 1
    
    # 测试创建一个简单的文档
    try:
        print("\n📝 测试创建飞书文档...")
        
        # 创建文档的请求数据
        doc_data = {
            "title": "🧪 Ob2Feishu 测试文档",
            "folder_token": ""  # 空字符串表示根目录
        }
        
        # 调用创建文档API
        endpoint = "/open-apis/docx/v1/documents"
        result = client.post(endpoint, data=doc_data)
        
        if result.get("code") == 0:
            doc_info = result.get("data", {}).get("document", {})
            doc_id = doc_info.get("document_id")
            doc_title = doc_info.get("title")
            doc_url = doc_info.get("url")
            
            print("✅ 文档创建成功！")
            print(f"   📄 文档标题: {doc_title}")
            print(f"   🆔 文档ID: {doc_id}")
            print(f"   🔗 访问链接: {doc_url}")
            
            # 测试添加内容到文档
            try:
                print("\n📝 测试向文档添加内容...")
                
                # 添加段落内容
                content_data = {
                    "children": [
                        {
                            "block_type": 2,  # 文本段落
                            "text": {
                                "elements": [
                                    {
                                        "text_run": {
                                            "content": "这是一个由 Ob2Feishu 工具创建的测试文档。\n\n"
                                        }
                                    },
                                    {
                                        "text_run": {
                                            "content": "✅ 飞书API认证成功\n",
                                            "text_element_style": {
                                                "bold": True
                                            }
                                        }
                                    },
                                    {
                                        "text_run": {
                                            "content": "🚀 文档创建功能正常\n",
                                            "text_element_style": {
                                                "bold": True
                                            }
                                        }
                                    },
                                    {
                                        "text_run": {
                                            "content": "📝 内容添加功能正常\n",
                                            "text_element_style": {
                                                "bold": True
                                            }
                                        }
                                    },
                                    {
                                        "text_run": {
                                            "content": "\n现在可以开始同步 Obsidian 笔记到飞书知识库了！"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
                
                # 添加内容到文档
                content_endpoint = f"/open-apis/docx/v1/documents/{doc_id}/blocks/children"
                content_result = client.post(content_endpoint, data=content_data)
                
                if content_result.get("code") == 0:
                    print("✅ 内容添加成功！")
                else:
                    print(f"⚠️  内容添加失败: {content_result.get('msg', '未知错误')}")
                    
            except FeishuAPIError as e:
                print(f"⚠️  内容添加失败: {e}")
            
            print(f"\n🎉 飞书文档API测试完成！")
            print(f"   您可以在飞书中查看创建的测试文档: {doc_url}")
            return 0
            
        else:
            print(f"❌ 文档创建失败: {result.get('msg', '未知错误')}")
            print(f"   错误代码: {result.get('code')}")
            return 1
            
    except FeishuAPIError as e:
        print(f"❌ 飞书API错误: {e}")
        if e.code:
            print(f"   错误代码: {e.code}")
        
        # 提供一些常见错误的解决建议
        if e.code == 1040001:
            print("💡 建议: 请检查应用是否有创建文档的权限")
        elif e.code == 1040002:
            print("💡 建议: 请检查folder_token是否有效")
        elif e.code == 230001:
            print("💡 建议: 请检查应用权限配置")
            
        return 1
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 