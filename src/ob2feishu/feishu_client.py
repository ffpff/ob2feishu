"""
飞书API客户端模块
提供飞书开放平台API的认证和通用请求功能
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class FeishuConfig:
    """飞书API配置"""
    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn"
    timeout: int = 30


class FeishuAPIError(Exception):
    """飞书API异常"""
    def __init__(self, message: str, code: int = None, response: Dict = None):
        super().__init__(message)
        self.code = code
        self.response = response


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self, config: FeishuConfig):
        """
        初始化飞书客户端
        
        Args:
            config: 飞书API配置
        """
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self.session = requests.Session()
        
        # 设置默认headers
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Ob2Feishu/1.0.0'
        })
    
    def _get_access_token(self) -> str:
        """
        获取访问令牌（tenant_access_token）
        
        Returns:
            访问令牌
            
        Raises:
            FeishuAPIError: 获取令牌失败
        """
        # 检查令牌是否有效
        if (self._access_token and 
            self._token_expires_at and 
            time.time() < self._token_expires_at - 300):  # 提前5分钟刷新
            return self._access_token
        
        logger.info("正在获取飞书访问令牌...")
        
        # 构造令牌获取URL
        if self.config.base_url.endswith('/open-apis'):
            # 如果base_url已经包含/open-apis
            url = f"{self.config.base_url}/auth/v3/tenant_access_token/internal"
        else:
            # 如果base_url是基础URL
            url = f"{self.config.base_url}/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 0:
                raise FeishuAPIError(
                    f"获取访问令牌失败: {data.get('msg', '未知错误')}",
                    code=data.get("code"),
                    response=data
                )
            
            self._access_token = data["tenant_access_token"]
            # 令牌有效期通常为2小时(7200秒)
            self._token_expires_at = time.time() + data.get("expire", 7200)
            
            logger.info("飞书访问令牌获取成功")
            return self._access_token
            
        except requests.RequestException as e:
            raise FeishuAPIError(f"网络请求失败: {str(e)}")
        except (KeyError, ValueError) as e:
            raise FeishuAPIError(f"响应数据解析失败: {str(e)}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retry_count: int = 3
    ) -> Tuple[Dict[str, Any], requests.Response]:
        """
        发起API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点（不包含base_url）
            data: 请求数据
            params: URL参数
            retry_count: 重试次数
            
        Returns:
            (响应数据, 响应对象)
            
        Raises:
            FeishuAPIError: API请求失败
        """
        # 构造完整URL，确保路径正确
        if endpoint.startswith('/open-apis'):
            # 如果endpoint已经包含/open-apis，直接拼接到主域名
            url = f"https://open.feishu.cn{endpoint}"
        elif self.config.base_url.endswith('/open-apis'):
            # 如果base_url已经包含/open-apis，直接拼接endpoint
            url = f"{self.config.base_url}{endpoint}"
        else:
            # 如果base_url是基础URL，需要添加/open-apis
            url = f"{self.config.base_url}/open-apis{endpoint}"
        
        # 获取访问令牌并设置Authorization header
        access_token = self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        
        for attempt in range(retry_count + 1):
            try:
                logger.debug(f"发起API请求: {method} {endpoint} (尝试 {attempt + 1}/{retry_count + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout
                )
                
                # 记录请求详情用于调试
                logger.debug(f"请求URL: {response.url}")
                logger.debug(f"响应状态: {response.status_code}")
                
                # 处理HTTP错误
                if response.status_code >= 400:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f": {error_data.get('msg', '未知错误')}"
                    except:
                        error_msg += f": {response.text}"
                    
                    # 如果是401错误且还有重试次数，清除token重试
                    if response.status_code == 401 and attempt < retry_count:
                        logger.warning("访问令牌可能已过期，清除缓存后重试")
                        self._access_token = None
                        self._token_expires_at = None
                        time.sleep(1)  # 短暂延迟
                        continue
                    
                    raise FeishuAPIError(error_msg, code=response.status_code)
                
                # 解析响应数据
                try:
                    result = response.json()
                except ValueError as e:
                    raise FeishuAPIError(f"响应JSON解析失败: {str(e)}")
                
                # 检查API业务状态码
                if result.get("code") != 0:
                    error_msg = result.get("msg", "未知错误")
                    
                    # 特定错误码的重试逻辑
                    if result.get("code") in [99991663, 99991664] and attempt < retry_count:  # 令牌相关错误
                        logger.warning(f"令牌错误，清除缓存后重试: {error_msg}")
                        self._access_token = None
                        self._token_expires_at = None
                        time.sleep(1)
                        continue
                    
                    raise FeishuAPIError(
                        f"API调用失败: {error_msg}",
                        code=result.get("code"),
                        response=result
                    )
                
                logger.debug("API请求成功")
                return result, response
                
            except requests.RequestException as e:
                if attempt < retry_count:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"网络请求失败，{wait_time}秒后重试: {str(e)}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise FeishuAPIError(f"网络请求失败: {str(e)}")
        
        # 不应该到达这里
        raise FeishuAPIError("请求失败，已达到最大重试次数")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        result, _ = self._make_request("GET", endpoint, params=params)
        return result
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        result, _ = self._make_request("POST", endpoint, data=data)
        return result
    
    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PATCH请求"""
        result, _ = self._make_request("PATCH", endpoint, data=data)
        return result
    
    def delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """DELETE请求"""
        result, _ = self._make_request("DELETE", endpoint, data=data)
        return result
    
    def test_connection(self) -> bool:
        """
        测试连接和认证是否正常
        
        Returns:
            连接是否成功
        """
        try:
            logger.info("正在测试飞书API连接...")
            
            # 尝试获取访问令牌
            token = self._get_access_token()
            
            if not token:
                logger.error("无法获取访问令牌")
                return False
            
            logger.info("✅ 飞书访问令牌获取成功！")
            logger.info("🎉 飞书API认证配置正确，可以开始使用飞书API功能。")
            return True
            
        except Exception as e:
            logger.error(f"连接测试异常: {str(e)}")
            return False
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        获取应用信息（简化版本）
        
        Returns:
            应用信息字典
        """
        # 简化版本：只返回基础信息，不调用API
        return {
            "app_id": self.config.app_id,
            "app_name": "飞书应用",
            "status": "已认证"
        }


def create_feishu_client(app_id: str, app_secret: str, base_url: str = None) -> FeishuClient:
    """
    创建飞书客户端的便捷函数
    
    Args:
        app_id: 应用ID
        app_secret: 应用密钥
        base_url: API基础URL，默认为官方地址
        
    Returns:
        配置好的飞书客户端
    """
    config = FeishuConfig(
        app_id=app_id,
        app_secret=app_secret,
        base_url=base_url or "https://open.feishu.cn"
    )
    return FeishuClient(config) 