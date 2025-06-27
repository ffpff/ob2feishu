"""
飞书API客户端测试模块
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests

from ob2feishu.feishu_client import (
    FeishuClient, 
    FeishuConfig, 
    FeishuAPIError,
    create_feishu_client
)


class TestFeishuConfig:
    """测试飞书配置类"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = FeishuConfig(
            app_id="test_app_id",
            app_secret="test_app_secret"
        )
        
        assert config.app_id == "test_app_id"
        assert config.app_secret == "test_app_secret"
        assert config.base_url == "https://open.feishu.cn"
        assert config.timeout == 30
    
    def test_config_custom_values(self):
        """测试自定义配置值"""
        config = FeishuConfig(
            app_id="test_app_id",
            app_secret="test_app_secret",
            base_url="https://custom.feishu.cn",
            timeout=60
        )
        
        assert config.base_url == "https://custom.feishu.cn"
        assert config.timeout == 60


class TestFeishuAPIError:
    """测试飞书API异常类"""
    
    def test_basic_error(self):
        """测试基础异常"""
        error = FeishuAPIError("测试错误")
        assert str(error) == "测试错误"
        assert error.code is None
        assert error.response is None
    
    def test_error_with_code(self):
        """测试带错误码的异常"""
        error = FeishuAPIError("测试错误", code=400)
        assert error.code == 400
    
    def test_error_with_response(self):
        """测试带响应数据的异常"""
        response = {"msg": "详细错误信息"}
        error = FeishuAPIError("测试错误", response=response)
        assert error.response == response


class TestFeishuClient:
    """测试飞书客户端"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = FeishuConfig(
            app_id="test_app_id",
            app_secret="test_app_secret"
        )
        self.client = FeishuClient(self.config)
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        assert self.client.config == self.config
        assert self.client._access_token is None
        assert self.client._token_expires_at is None
        assert self.client.session is not None
        
        # 检查默认headers
        assert 'Content-Type' in self.client.session.headers
        assert 'User-Agent' in self.client.session.headers
    
    @patch('requests.Session.post')
    def test_get_access_token_success(self, mock_post):
        """测试获取访问令牌成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "test_token_123",
            "expire": 7200
        }
        mock_post.return_value = mock_response
        
        token = self.client._get_access_token()
        
        assert token == "test_token_123"
        assert self.client._access_token == "test_token_123"
        assert self.client._token_expires_at is not None
        
        # 验证请求参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['app_id'] == "test_app_id"
        assert call_args[1]['json']['app_secret'] == "test_app_secret"
    
    @patch('requests.Session.post')
    def test_get_access_token_api_error(self, mock_post):
        """测试获取访问令牌API错误"""
        # 模拟API错误响应
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "code": 99991663,
            "msg": "应用不存在"
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(FeishuAPIError) as exc_info:
            self.client._get_access_token()
        
        assert "获取访问令牌失败" in str(exc_info.value)
        assert exc_info.value.code == 99991663
    
    @patch('requests.Session.post')
    def test_get_access_token_network_error(self, mock_post):
        """测试获取访问令牌网络错误"""
        # 模拟网络错误
        mock_post.side_effect = requests.RequestException("网络连接失败")
        
        with pytest.raises(FeishuAPIError) as exc_info:
            self.client._get_access_token()
        
        assert "网络请求失败" in str(exc_info.value)
    
    def test_token_cache(self):
        """测试令牌缓存机制"""
        # 设置一个有效的令牌
        self.client._access_token = "cached_token"
        self.client._token_expires_at = time.time() + 3600  # 1小时后过期
        
        # 不应该发起新的请求
        with patch('requests.Session.post') as mock_post:
            token = self.client._get_access_token()
            assert token == "cached_token"
            mock_post.assert_not_called()
    
    def test_token_refresh(self):
        """测试令牌自动刷新"""
        # 设置一个即将过期的令牌（剩余时间少于5分钟）
        self.client._access_token = "old_token"
        self.client._token_expires_at = time.time() + 200  # 3分钟后过期
        
        with patch('requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "code": 0,
                "tenant_access_token": "new_token",
                "expire": 7200
            }
            mock_post.return_value = mock_response
            
            token = self.client._get_access_token()
            assert token == "new_token"
            mock_post.assert_called_once()
    
    @patch.object(FeishuClient, '_get_access_token')
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request, mock_get_token):
        """测试成功的API请求"""
        # 模拟令牌获取
        mock_get_token.return_value = "test_token"
        
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {"test": "data"}
        }
        mock_request.return_value = mock_response
        
        result, response = self.client._make_request("GET", "/test/endpoint")
        
        assert result["code"] == 0
        assert result["data"]["test"] == "data"
        assert response == mock_response
        
        # 验证请求参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['headers']['Authorization'] == "Bearer test_token"
    
    @patch('requests.Session.request')
    def test_make_request_401_retry(self, mock_request):
        """测试401错误重试机制"""
        # 第一次请求返回401，第二次成功
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_401.json.return_value = {"msg": "token无效"}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"code": 0, "data": {}}
        
        mock_request.side_effect = [mock_response_401, mock_response_success]
        
        # 模拟token获取的过程
        with patch.object(self.client, '_get_access_token') as mock_get_token:
            mock_get_token.return_value = "test_token"
            
            result, _ = self.client._make_request("GET", "/test/endpoint")
            
            assert result["code"] == 0
            assert mock_request.call_count == 2
            # 在401重试逻辑中，第一次获取token，清除后再次获取token
            assert mock_get_token.call_count >= 1
    
    @patch.object(FeishuClient, '_get_access_token')
    @patch('requests.Session.request')
    def test_make_request_api_error(self, mock_request, mock_get_token):
        """测试API业务错误"""
        mock_get_token.return_value = "test_token"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 400,
            "msg": "参数错误"
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(FeishuAPIError) as exc_info:
            self.client._make_request("GET", "/test/endpoint")
        
        assert "API调用失败" in str(exc_info.value)
        assert exc_info.value.code == 400
    
    def test_http_methods(self):
        """测试HTTP方法封装"""
        with patch.object(self.client, '_make_request') as mock_make_request:
            mock_make_request.return_value = ({"code": 0}, Mock())
            
            # 测试GET
            self.client.get("/test", params={"key": "value"})
            mock_make_request.assert_called_with("GET", "/test", params={"key": "value"})
            
            # 测试POST
            self.client.post("/test", data={"key": "value"})
            mock_make_request.assert_called_with("POST", "/test", data={"key": "value"})
            
            # 测试PATCH
            self.client.patch("/test", data={"key": "value"})
            mock_make_request.assert_called_with("PATCH", "/test", data={"key": "value"})
            
            # 测试DELETE
            self.client.delete("/test", data={"key": "value"})
            mock_make_request.assert_called_with("DELETE", "/test", data={"key": "value"})
    
    @patch.object(FeishuClient, 'get')
    def test_test_connection_success(self, mock_get):
        """测试连接测试成功"""
        mock_get.return_value = {
            "code": 0,
            "data": {
                "app": {
                    "app_name": "测试应用"
                }
            }
        }
        
        with patch.object(self.client, '_get_access_token', return_value="test_token"):
            result = self.client.test_connection()
            assert result is True
    
    def test_test_connection_failure(self):
        """测试连接测试失败"""
        with patch.object(self.client, '_get_access_token', side_effect=FeishuAPIError("认证失败")):
            result = self.client.test_connection()
            assert result is False
    
    def test_get_app_info(self):
        """测试获取应用信息"""
        expected_app_info = {
            "app_id": "test_app_id",
            "app_name": "飞书应用",
            "status": "已认证"
        }
        
        app_info = self.client.get_app_info()
        assert app_info["app_id"] == "test_app_id"
        assert app_info["app_name"] == "飞书应用"
        assert app_info["status"] == "已认证"


class TestCreateFeishuClient:
    """测试便捷函数"""
    
    def test_create_feishu_client_default(self):
        """测试默认参数创建客户端"""
        client = create_feishu_client("test_app_id", "test_secret")
        
        assert isinstance(client, FeishuClient)
        assert client.config.app_id == "test_app_id"
        assert client.config.app_secret == "test_secret"
        assert client.config.base_url == "https://open.feishu.cn"
    
    def test_create_feishu_client_custom_url(self):
        """测试自定义URL创建客户端"""
        client = create_feishu_client(
            "test_app_id", 
            "test_secret", 
            "https://custom.feishu.cn"
        )
        
        assert client.config.base_url == "https://custom.feishu.cn" 