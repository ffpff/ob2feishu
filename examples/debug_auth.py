#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书认证调试脚本

用于调试飞书API认证问题
"""

import sys
import os
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.config import get_config
from src.ob2feishu.feishu_client import create_feishu_client, FeishuConfig, FeishuClient


def test_direct_auth():
    """直接测试飞书认证API"""
    print("🔍 直接测试飞书认证API")
    print("=" * 50)
    
    # 从环境变量获取配置
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("❌ 环境变量未设置")
        print(f"FEISHU_APP_ID: {app_id}")
        print(f"FEISHU_APP_SECRET: {'***' if app_secret else None}")
        return False
    
    print(f"📱 应用ID: {app_id}")
    print(f"🔐 应用密钥: {app_secret[:8]}***{app_secret[-4:]}")
    
    # 直接调用认证API
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    try:
        print("\n🌐 发起认证请求...")
        print(f"URL: {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\n📊 响应状态: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {data}")
            
            if data.get("code") == 0:
                print("✅ 认证成功！")
                token = data.get("tenant_access_token")
                print(f"🎫 访问令牌: {token[:20]}...{token[-10:] if token else ''}")
                return True
            else:
                print(f"❌ 认证失败: {data.get('msg', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def test_client_auth():
    """测试客户端认证"""
    print("\n🔍 测试客户端认证")
    print("=" * 50)
    
    try:
        config = get_config()
        print(f"📋 配置信息:")
        print(f"   应用ID: {config.feishu.app_id}")
        print(f"   应用密钥: {config.feishu.app_secret[:8]}***{config.feishu.app_secret[-4:]}")
        
        # 创建客户端
        client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        
        # 测试连接
        result = client.test_connection()
        
        if result:
            print("✅ 客户端认证成功！")
            
            # 获取应用信息
            app_info = client.get_app_info()
            print(f"🏢 应用信息: {app_info}")
            
            return True
        else:
            print("❌ 客户端认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 客户端认证异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 飞书认证调试工具")
    print("用于诊断飞书API认证问题")
    print()
    
    # 检查环境变量
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    
    print("🔧 环境变量检查:")
    print(f"   FEISHU_APP_ID: {app_id or '❌ 未设置'}")
    print(f"   FEISHU_APP_SECRET: {'✅ 已设置' if app_secret else '❌ 未设置'}")
    print()
    
    # 测试1: 直接API调用
    success1 = test_direct_auth()
    
    # 测试2: 客户端认证
    success2 = test_client_auth()
    
    print("\n" + "=" * 60)
    print("🏁 调试结果总结")
    print(f"   直接API认证: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   客户端认证: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有认证测试通过！可以进行同步测试。")
        return 0
    else:
        print("\n💡 建议:")
        print("   1. 检查飞书应用ID和密钥是否正确")
        print("   2. 确认应用是否已启用")
        print("   3. 检查应用权限设置")
        print("   4. 查看飞书开放平台控制台是否有错误信息")
        return 1


if __name__ == "__main__":
    exit(main()) 