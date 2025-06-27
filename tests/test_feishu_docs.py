#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书知识库操作模块单元测试
"""

import pytest
import unittest.mock as mock
from typing import Dict, Any

from src.ob2feishu.feishu_docs import (
    FeishuDocument,
    FeishuBlock,
    FeishuDocsClient,
    create_feishu_docs_client
)
from src.ob2feishu.feishu_client import FeishuClient, FeishuAPIError, FeishuConfig


class TestFeishuDocument:
    """测试FeishuDocument数据类"""
    
    def test_create_from_api_response(self):
        """测试从API响应创建文档对象"""
        api_data = {
            "document_id": "doc123",
            "title": "测试文档",
            "revision_id": 5,
            "url": "https://example.feishu.cn/doc/doc123",
            "folder_token": "folder456",
            "created_time": "2024-01-01T00:00:00Z",
            "updated_time": "2024-01-02T00:00:00Z"
        }
        
        doc = FeishuDocument.from_api_response(api_data)
        
        assert doc.document_id == "doc123"
        assert doc.title == "测试文档"
        assert doc.revision_id == 5
        assert doc.url == "https://example.feishu.cn/doc/doc123"
        assert doc.folder_token == "folder456"
        assert doc.created_time == "2024-01-01T00:00:00Z"
        assert doc.updated_time == "2024-01-02T00:00:00Z"
    
    def test_create_from_minimal_response(self):
        """测试从最小API响应创建文档对象"""
        api_data = {
            "document_id": "doc123",
            "title": "测试文档",
            "revision_id": 1
        }
        
        doc = FeishuDocument.from_api_response(api_data)
        
        assert doc.document_id == "doc123"
        assert doc.title == "测试文档"
        assert doc.revision_id == 1
        assert doc.url is None
        assert doc.folder_token is None


class TestFeishuBlock:
    """测试FeishuBlock数据类"""
    
    def test_create_from_api_response(self):
        """测试从API响应创建块对象"""
        api_data = {
            "block_id": "block123",
            "block_type": 2,
            "parent_id": "parent456",
            "children": ["child1", "child2"]
        }
        
        block = FeishuBlock.from_api_response(api_data)
        
        assert block.block_id == "block123"
        assert block.block_type == 2
        assert block.parent_id == "parent456"
        assert block.children == ["child1", "child2"]
    
    def test_create_from_minimal_response(self):
        """测试从最小API响应创建块对象"""
        api_data = {
            "block_id": "block123",
            "block_type": 2
        }
        
        block = FeishuBlock.from_api_response(api_data)
        
        assert block.block_id == "block123"
        assert block.block_type == 2
        assert block.parent_id is None
        assert block.children == []


class TestFeishuDocsClient:
    """测试FeishuDocsClient类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建模拟的配置
        self.config = FeishuConfig(
            app_id="test_app_id",
            app_secret="test_app_secret"
        )
        
        # 创建模拟的飞书客户端
        self.mock_feishu_client = mock.MagicMock(spec=FeishuClient)
        self.mock_feishu_client.config = self.config
        
        # 创建飞书文档客户端
        self.docs_client = FeishuDocsClient(self.mock_feishu_client)
    
    def test_init(self):
        """测试初始化"""
        assert self.docs_client.client == self.mock_feishu_client
        assert self.docs_client.logger is not None
    
    def test_create_document_success(self):
        """测试创建文档成功"""
        # 模拟API响应
        mock_response = {
            "code": 0,
            "msg": "success",
            "data": {
                "document": {
                    "document_id": "doc123",
                    "title": "Untitled",
                    "revision_id": 1,
                    "url": "https://example.feishu.cn/doc/doc123"
                }
            }
        }
        
        self.mock_feishu_client.post.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.create_document()
        
        # 验证结果
        assert isinstance(result, FeishuDocument)
        assert result.document_id == "doc123"
        assert result.title == "Untitled"
        assert result.revision_id == 1
        
        # 验证API调用
        self.mock_feishu_client.post.assert_called_once_with("/open-apis/docx/v1/documents")
    
    def test_create_document_with_folder(self):
        """测试在指定文件夹创建文档"""
        mock_response = {
            "code": 0,
            "data": {
                "document": {
                    "document_id": "doc123",
                    "title": "Untitled",
                    "revision_id": 1
                }
            }
        }
        
        self.mock_feishu_client.post.return_value = mock_response
        
        # 调用方法
        self.docs_client.create_document(folder_token="folder456")
        
        # 验证API调用包含文件夹参数
        expected_endpoint = "/open-apis/docx/v1/documents?folder_token=folder456"
        self.mock_feishu_client.post.assert_called_once_with(expected_endpoint)
    
    def test_create_document_with_title(self):
        """测试创建带标题的文档"""
        mock_response = {
            "code": 0,
            "data": {
                "document": {
                    "document_id": "doc123",
                    "title": "Untitled",
                    "revision_id": 1
                }
            }
        }
        
        # 模拟标题更新成功
        mock_update_response = {"code": 0}
        
        self.mock_feishu_client.post.return_value = mock_response
        self.mock_feishu_client.patch.return_value = mock_update_response
        
        # 调用方法
        result = self.docs_client.create_document(title="我的文档")
        
        # 验证结果
        assert result.title == "我的文档"
        
        # 验证API调用
        self.mock_feishu_client.post.assert_called_once()
        self.mock_feishu_client.patch.assert_called_once()
    
    def test_create_document_api_error(self):
        """测试创建文档API错误"""
        mock_response = {
            "code": 1001,
            "msg": "权限不足"
        }
        
        self.mock_feishu_client.post.return_value = mock_response
        
        # 验证抛出异常
        with pytest.raises(FeishuAPIError) as exc_info:
            self.docs_client.create_document()
        
        assert "文档创建失败" in str(exc_info.value)
        assert exc_info.value.code == 1001
    
    def test_get_document_info_success(self):
        """测试获取文档信息成功"""
        mock_response = {
            "code": 0,
            "data": {
                "document": {
                    "document_id": "doc123",
                    "title": "测试文档",
                    "revision_id": 5
                }
            }
        }
        
        self.mock_feishu_client.get.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.get_document_info("doc123")
        
        # 验证结果
        assert isinstance(result, FeishuDocument)
        assert result.document_id == "doc123"
        assert result.title == "测试文档"
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123"
        self.mock_feishu_client.get.assert_called_once_with(expected_endpoint)
    
    def test_get_document_blocks_success(self):
        """测试获取文档块成功"""
        mock_response = {
            "code": 0,
            "data": {
                "items": [
                    {"block_id": "block1", "block_type": 2},
                    {"block_id": "block2", "block_type": 3}
                ],
                "has_more": False
            }
        }
        
        self.mock_feishu_client.get.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.get_document_blocks("doc123")
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["block_id"] == "block1"
        assert result[1]["block_id"] == "block2"
        
        # 验证API调用
        self.mock_feishu_client.get.assert_called_once()
        call_args = self.mock_feishu_client.get.call_args[0][0]
        assert "/open-apis/docx/v1/documents/doc123/blocks" in call_args
        assert "page_size=500" in call_args
    
    def test_get_document_blocks_pagination(self):
        """测试获取文档块分页"""
        # 第一页响应
        mock_response_1 = {
            "code": 0,
            "data": {
                "items": [{"block_id": "block1", "block_type": 2}],
                "has_more": True,
                "page_token": "token123"
            }
        }
        
        # 第二页响应
        mock_response_2 = {
            "code": 0,
            "data": {
                "items": [{"block_id": "block2", "block_type": 3}],
                "has_more": False
            }
        }
        
        self.mock_feishu_client.get.side_effect = [mock_response_1, mock_response_2]
        
        # 调用方法
        result = self.docs_client.get_document_blocks("doc123")
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["block_id"] == "block1"
        assert result[1]["block_id"] == "block2"
        
        # 验证API调用了两次
        assert self.mock_feishu_client.get.call_count == 2
    
    def test_create_blocks_success(self):
        """测试创建块成功"""
        blocks_to_create = [
            {"block_type": 2, "text": {"elements": [{"text": "测试内容"}]}}
        ]
        
        mock_response = {
            "code": 0,
            "data": {
                "children": [
                    {"block_id": "new_block_1"}
                ]
            }
        }
        
        self.mock_feishu_client.post.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.create_blocks("doc123", blocks_to_create)
        
        # 验证结果
        assert result == ["new_block_1"]
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/children"
        expected_data = {
            "children": blocks_to_create,
            "index": 0
        }
        self.mock_feishu_client.post.assert_called_once_with(expected_endpoint, data=expected_data)
    
    def test_create_blocks_with_parent(self):
        """测试在父块下创建子块"""
        blocks_to_create = [{"block_type": 2}]
        
        mock_response = {
            "code": 0,
            "data": {"children": [{"block_id": "child_block_1"}]}
        }
        
        self.mock_feishu_client.post.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.create_blocks(
            "doc123", 
            blocks_to_create, 
            parent_block_id="parent_block"
        )
        
        # 验证结果
        assert result == ["child_block_1"]
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/parent_block/children"
        self.mock_feishu_client.post.assert_called_once_with(expected_endpoint, data=mock.ANY)
    
    def test_create_blocks_empty_list(self):
        """测试创建空块列表"""
        result = self.docs_client.create_blocks("doc123", [])
        
        assert result == []
        self.mock_feishu_client.post.assert_not_called()
    
    def test_update_block_success(self):
        """测试更新块成功"""
        mock_response = {"code": 0}
        self.mock_feishu_client.patch.return_value = mock_response
        
        block_data = {"text": {"elements": [{"text": "更新的内容"}]}}
        
        # 调用方法
        result = self.docs_client.update_block("doc123", "block456", block_data)
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/block456"
        self.mock_feishu_client.patch.assert_called_once_with(expected_endpoint, data=block_data)
    
    def test_batch_update_blocks_success(self):
        """测试批量更新块成功"""
        mock_response = {"code": 0}
        self.mock_feishu_client.patch.return_value = mock_response
        
        updates = [
            {"block_id": "block1", "text": {"elements": [{"text": "内容1"}]}},
            {"block_id": "block2", "text": {"elements": [{"text": "内容2"}]}}
        ]
        
        # 调用方法
        result = self.docs_client.batch_update_blocks("doc123", updates)
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/batch_update"
        expected_data = {"requests": updates}
        self.mock_feishu_client.patch.assert_called_once_with(expected_endpoint, data=expected_data)
    
    def test_batch_update_blocks_empty_list(self):
        """测试批量更新空列表"""
        result = self.docs_client.batch_update_blocks("doc123", [])
        
        assert result is True
        self.mock_feishu_client.patch.assert_not_called()
    
    def test_delete_blocks_success(self):
        """测试删除块成功"""
        mock_response = {"code": 0}
        self.mock_feishu_client.delete.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.delete_blocks("doc123", 0, 5)
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/children/batch_delete"
        expected_data = {"start_index": 0, "end_index": 5}
        self.mock_feishu_client.delete.assert_called_once_with(expected_endpoint, data=expected_data)
    
    def test_delete_blocks_with_parent(self):
        """测试删除父块下的子块"""
        mock_response = {"code": 0}
        self.mock_feishu_client.delete.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.delete_blocks("doc123", 0, 3, parent_block_id="parent_block")
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123/blocks/parent_block/children/batch_delete"
        self.mock_feishu_client.delete.assert_called_once_with(expected_endpoint, data=mock.ANY)
    
    def test_clear_document_success(self):
        """测试清空文档成功"""
        # 模拟获取文档块
        mock_blocks = [
            {"block_id": "block1"},
            {"block_id": "block2"}
        ]
        
        # 模拟删除响应
        mock_delete_response = {"code": 0}
        
        self.mock_feishu_client.get.return_value = {
            "code": 0,
            "data": {"items": mock_blocks, "has_more": False}
        }
        self.mock_feishu_client.delete.return_value = mock_delete_response
        
        # 调用方法
        result = self.docs_client.clear_document("doc123")
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        self.mock_feishu_client.get.assert_called_once()
        self.mock_feishu_client.delete.assert_called_once()
    
    def test_clear_document_already_empty(self):
        """测试清空已空的文档"""
        # 模拟空文档
        self.mock_feishu_client.get.return_value = {
            "code": 0,
            "data": {"items": [], "has_more": False}
        }
        
        # 调用方法
        result = self.docs_client.clear_document("doc123")
        
        # 验证结果
        assert result is True
        
        # 验证不调用删除API
        self.mock_feishu_client.delete.assert_not_called()
    
    def test_update_document_title_success(self):
        """测试更新文档标题成功"""
        mock_response = {"code": 0}
        self.mock_feishu_client.patch.return_value = mock_response
        
        # 调用方法
        result = self.docs_client.update_document_title("doc123", "新标题")
        
        # 验证结果
        assert result is True
        
        # 验证API调用
        expected_endpoint = "/open-apis/docx/v1/documents/doc123"
        expected_data = {"title": "新标题"}
        self.mock_feishu_client.patch.assert_called_once_with(expected_endpoint, data=expected_data)
    
    def test_replace_document_content_success(self):
        """测试替换文档内容成功"""
        new_blocks = [
            {"block_type": 2, "text": {"elements": [{"text": "新内容"}]}}
        ]
        
        # 模拟清空文档
        self.mock_feishu_client.get.return_value = {
            "code": 0,
            "data": {"items": [{"block_id": "old_block"}], "has_more": False}
        }
        self.mock_feishu_client.delete.return_value = {"code": 0}
        
        # 模拟创建新块
        self.mock_feishu_client.post.return_value = {
            "code": 0,
            "data": {"children": [{"block_id": "new_block_1"}]}
        }
        
        # 调用方法
        result = self.docs_client.replace_document_content("doc123", new_blocks)
        
        # 验证结果
        assert result == ["new_block_1"]
        
        # 验证API调用次序
        self.mock_feishu_client.get.assert_called_once()  # 获取现有块
        self.mock_feishu_client.delete.assert_called_once()  # 删除现有块
        self.mock_feishu_client.post.assert_called_once()  # 创建新块
    
    def test_replace_document_content_empty_blocks(self):
        """测试替换为空内容"""
        # 模拟清空文档
        self.mock_feishu_client.get.return_value = {
            "code": 0,
            "data": {"items": [{"block_id": "old_block"}], "has_more": False}
        }
        self.mock_feishu_client.delete.return_value = {"code": 0}
        
        # 调用方法
        result = self.docs_client.replace_document_content("doc123", [])
        
        # 验证结果
        assert result == []
        
        # 验证只调用了清空，没有创建新块
        self.mock_feishu_client.get.assert_called_once()
        self.mock_feishu_client.delete.assert_called_once()
        self.mock_feishu_client.post.assert_not_called()


class TestCreateFeishuDocsClient:
    """测试便捷函数"""
    
    def test_create_feishu_docs_client(self):
        """测试创建飞书文档客户端"""
        mock_feishu_client = mock.MagicMock(spec=FeishuClient)
        
        result = create_feishu_docs_client(mock_feishu_client)
        
        assert isinstance(result, FeishuDocsClient)
        assert result.client == mock_feishu_client 