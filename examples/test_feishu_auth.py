#!/usr/bin/env python3
"""
飞书API认证测试脚本

使用说明:
1. 在.env文件中设置FEISHU_APP_ID和FEISHU_APP_SECRET
2. 运行: python examples/test_feishu_auth.py
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
    print("🚀 飞书API认证测试工具")
    print("=" * 50)
    
    # 加载配置
    try:
        config = get_config()
        feishu_config = config.get('feishu', {})
        
        app_id = feishu_config.get('app_id')
        app_secret = feishu_config.get('app_secret')
        
        if not app_id or not app_secret:
            print("❌ 错误: 未找到飞书应用配置")
            print("\n请在以下位置之一配置飞书应用信息:")
            print("1. config/config.yaml 文件中的 feishu.app_id 和 feishu.app_secret")
            print("2. 环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
            print("3. .env 文件")
            return 1
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 创建飞书客户端
    try:
        print(f"🔧 创建飞书客户端...")
        print(f"   App ID: {app_id[:8]}..." if len(app_id) > 8 else f"   App ID: {app_id}")
        
        client = create_feishu_client(app_id, app_secret)
        
    except Exception as e:
        print(f"❌ 创建客户端失败: {e}")
        return 1
    
    # 测试认证和连接
    try:
        print("\n🔐 测试飞书API认证...")
        
        if client.test_connection():
            print("✅ 认证成功！")
            
            # 获取应用信息
            try:
                app_info = client.get_app_info()
                print(f"\n📱 应用信息:")
                print(f"   应用名称: {app_info.get('app_name', '未知')}")
                print(f"   应用ID: {app_info.get('app_id', '未知')}")
                print(f"   应用状态: {app_info.get('status', '未知')}")
                
                # 显示可用权限（如果有）
                if 'permissions' in app_info:
                    print(f"   权限范围: {len(app_info['permissions'])} 个权限")
                
            except Exception as e:
                print(f"⚠️  获取应用信息失败（但认证成功）: {e}")
            
            print("\n🎉 飞书API认证配置完成！可以开始使用飞书API功能。")
            return 0
            
        else:
            print("❌ 认证失败！请检查应用ID和密钥是否正确。")
            return 1
            
    except FeishuAPIError as e:
        print(f"❌ 飞书API错误: {e}")
        if e.code:
            print(f"   错误代码: {e.code}")
        return 1
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 