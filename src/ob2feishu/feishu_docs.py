#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书知识库操作模块

提供飞书文档的创建、更新、获取、删除等操作功能
包含完整的错误处理和重试机制
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from .feishu_client import FeishuClient, FeishuAPIError

logger = logging.getLogger(__name__)


@dataclass
class FeishuDocument:
    """飞书文档信息"""
    document_id: str
    title: str
    revision_id: int
    url: Optional[str] = None
    folder_token: Optional[str] = None
    created_time: Optional[str] = None
    updated_time: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FeishuDocument':
        """从API响应创建文档对象"""
        return cls(
            document_id=data.get("document_id", ""),
            title=data.get("title", ""),
            revision_id=data.get("revision_id", 0),
            url=data.get("url"),
            folder_token=data.get("folder_token"),
            created_time=data.get("created_time"),
            updated_time=data.get("updated_time")
        )


@dataclass
class FeishuBlock:
    """飞书文档块信息"""
    block_id: str
    block_type: int
    parent_id: Optional[str] = None
    children: Optional[List[str]] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FeishuBlock':
        """从API响应创建块对象"""
        return cls(
            block_id=data.get("block_id", ""),
            block_type=data.get("block_type", 0),
            parent_id=data.get("parent_id"),
            children=data.get("children", [])
        )


class FeishuDocsClient:
    """
    飞书文档操作客户端
    
    提供飞书文档的完整操作功能：
    - 文档创建、更新、删除
    - 文档内容获取和修改
    - 批量操作支持
    - 错误处理和重试机制
    """
    
    def __init__(self, feishu_client: FeishuClient):
        """
        初始化飞书文档客户端
        
        Args:
            feishu_client: 飞书API客户端实例
        """
        self.client = feishu_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_document(
        self, 
        title: Optional[str] = None,
        folder_token: Optional[str] = None
    ) -> FeishuDocument:
        """
        创建新的飞书文档
        
        Args:
            title: 文档标题，如果不提供则使用默认标题
            folder_token: 目标文件夹token，不提供则创建在根目录
            
        Returns:
            创建的文档信息
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.info(f"正在创建飞书文档: title={title}, folder_token={folder_token}")
        
        # 构建API端点
        endpoint = "/open-apis/docx/v1/documents"
        if folder_token:
            endpoint += f"?folder_token={folder_token}"
        
        try:
            # 调用创建文档API
            response = self.client.post(endpoint)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"文档创建失败: {error_msg}")
                raise FeishuAPIError(f"文档创建失败: {error_msg}", response.get("code"))
            
            # 解析响应数据
            doc_data = response.get("data", {}).get("document", {})
            document = FeishuDocument.from_api_response(doc_data)
            
            self.logger.info(f"✅ 文档创建成功: ID={document.document_id}, title={document.title}")
            
            # 如果提供了标题且与默认标题不同，更新文档标题
            if title and title != document.title:
                try:
                    self.update_document_title(document.document_id, title)
                    document.title = title
                    self.logger.info(f"✅ 文档标题已更新: {title}")
                except Exception as e:
                    self.logger.warning(f"文档标题更新失败: {e}")
            
            return document
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"文档创建异常: {e}")
            raise FeishuAPIError(f"文档创建异常: {e}")
    
    def get_document_info(self, document_id: str) -> FeishuDocument:
        """
        获取文档基本信息
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档信息
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.debug(f"获取文档信息: {document_id}")
        
        endpoint = f"/open-apis/docx/v1/documents/{document_id}"
        
        try:
            response = self.client.get(endpoint)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"获取文档信息失败: {error_msg}")
                raise FeishuAPIError(f"获取文档信息失败: {error_msg}", response.get("code"))
            
            doc_data = response.get("data", {}).get("document", {})
            document = FeishuDocument.from_api_response(doc_data)
            
            self.logger.debug(f"✅ 文档信息获取成功: {document.title}")
            return document
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"获取文档信息异常: {e}")
            raise FeishuAPIError(f"获取文档信息异常: {e}")
    
    def get_document_blocks(
        self, 
        document_id: str,
        page_size: int = 500,
        user_id_type: str = "open_id"
    ) -> List[Dict[str, Any]]:
        """
        获取文档所有块内容
        
        Args:
            document_id: 文档ID
            page_size: 分页大小，默认500
            user_id_type: 用户ID类型
            
        Returns:
            文档块列表
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.debug(f"获取文档块: {document_id}")
        
        all_blocks = []
        page_token = None
        
        while True:
            # 构建API端点
            endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks"
            params = {
                "page_size": page_size,
                "user_id_type": user_id_type
            }
            
            if page_token:
                params["page_token"] = page_token
            
            # 添加参数到URL
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{param_str}"
            
            try:
                response = self.client.get(endpoint)
                
                if response.get("code") != 0:
                    error_msg = response.get("msg", "未知错误")
                    self.logger.error(f"获取文档块失败: {error_msg}")
                    raise FeishuAPIError(f"获取文档块失败: {error_msg}", response.get("code"))
                
                data = response.get("data", {})
                blocks = data.get("items", [])
                all_blocks.extend(blocks)
                
                # 检查是否还有更多页
                page_token = data.get("page_token")
                has_more = data.get("has_more", False)
                
                if not has_more or not page_token:
                    break
                    
            except FeishuAPIError:
                raise
            except Exception as e:
                self.logger.error(f"获取文档块异常: {e}")
                raise FeishuAPIError(f"获取文档块异常: {e}")
        
        self.logger.debug(f"✅ 文档块获取成功: 共{len(all_blocks)}个块")
        return all_blocks
    
    def create_blocks(
        self, 
        document_id: str, 
        blocks: List[Dict[str, Any]],
        parent_block_id: Optional[str] = None,
        index: int = 0
    ) -> List[str]:
        """
        在文档中创建新的内容块
        
        Args:
            document_id: 文档ID
            blocks: 要创建的块列表
            parent_block_id: 父块ID，不提供则添加到根级别
            index: 插入位置索引
            
        Returns:
            创建的块ID列表
            
        Raises:
            FeishuAPIError: API调用失败
        """
        if not blocks:
            self.logger.warning("没有要创建的块")
            return []
        
        self.logger.info(f"创建文档块: document_id={document_id}, 块数量={len(blocks)}")
        
        # 构建API端点
        if parent_block_id:
            endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children"
        else:
            endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/children"
        
        # 构建请求数据
        request_data = {
            "children": blocks,
            "index": index
        }
        
        try:
            response = self.client.post(endpoint, data=request_data)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"创建块失败: {error_msg}")
                raise FeishuAPIError(f"创建块失败: {error_msg}", response.get("code"))
            
            # 解析创建的块ID
            data = response.get("data", {})
            children = data.get("children", [])
            block_ids = [child.get("block_id") for child in children if child.get("block_id")]
            
            self.logger.info(f"✅ 块创建成功: 共{len(block_ids)}个块")
            return block_ids
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"创建块异常: {e}")
            raise FeishuAPIError(f"创建块异常: {e}")
    
    def update_block(
        self, 
        document_id: str, 
        block_id: str, 
        block_data: Dict[str, Any]
    ) -> bool:
        """
        更新特定的文档块
        
        Args:
            document_id: 文档ID
            block_id: 要更新的块ID
            block_data: 新的块数据
            
        Returns:
            更新是否成功
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.debug(f"更新文档块: document_id={document_id}, block_id={block_id}")
        
        endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}"
        
        try:
            response = self.client.patch(endpoint, data=block_data)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"更新块失败: {error_msg}")
                raise FeishuAPIError(f"更新块失败: {error_msg}", response.get("code"))
            
            self.logger.debug(f"✅ 块更新成功: {block_id}")
            return True
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"更新块异常: {e}")
            raise FeishuAPIError(f"更新块异常: {e}")
    
    def batch_update_blocks(
        self, 
        document_id: str, 
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        批量更新文档块
        
        Args:
            document_id: 文档ID
            updates: 更新操作列表，每个包含block_id和更新数据
            
        Returns:
            更新是否成功
            
        Raises:
            FeishuAPIError: API调用失败
        """
        if not updates:
            self.logger.warning("没有要更新的块")
            return True
        
        self.logger.info(f"批量更新文档块: document_id={document_id}, 更新数量={len(updates)}")
        
        endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/batch_update"
        
        request_data = {
            "requests": updates
        }
        
        try:
            response = self.client.patch(endpoint, data=request_data)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"批量更新失败: {error_msg}")
                raise FeishuAPIError(f"批量更新失败: {error_msg}", response.get("code"))
            
            self.logger.info(f"✅ 批量更新成功: 共{len(updates)}个块")
            return True
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"批量更新异常: {e}")
            raise FeishuAPIError(f"批量更新异常: {e}")
    
    def delete_blocks(
        self, 
        document_id: str, 
        start_index: int,
        end_index: int,
        parent_block_id: Optional[str] = None
    ) -> bool:
        """
        删除文档块
        
        Args:
            document_id: 文档ID
            start_index: 开始索引
            end_index: 结束索引
            parent_block_id: 父块ID，不提供则操作根级别
            
        Returns:
            删除是否成功
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.info(f"删除文档块: document_id={document_id}, 范围={start_index}-{end_index}")
        
        # 构建API端点
        if parent_block_id:
            endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children/batch_delete"
        else:
            endpoint = f"/open-apis/docx/v1/documents/{document_id}/blocks/children/batch_delete"
        
        request_data = {
            "start_index": start_index,
            "end_index": end_index
        }
        
        try:
            response = self.client.delete(endpoint, data=request_data)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"删除块失败: {error_msg}")
                raise FeishuAPIError(f"删除块失败: {error_msg}", response.get("code"))
            
            self.logger.info(f"✅ 块删除成功: 范围={start_index}-{end_index}")
            return True
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"删除块异常: {e}")
            raise FeishuAPIError(f"删除块异常: {e}")
    
    def clear_document(self, document_id: str) -> bool:
        """
        清空文档内容（删除所有块）
        
        Args:
            document_id: 文档ID
            
        Returns:
            清空是否成功
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.info(f"清空文档内容: {document_id}")
        
        try:
            # 获取所有块
            blocks = self.get_document_blocks(document_id)
            
            if not blocks:
                self.logger.info("文档已经是空的")
                return True
            
            # 删除所有块
            result = self.delete_blocks(
                document_id=document_id,
                start_index=0,
                end_index=len(blocks)
            )
            
            if result:
                self.logger.info(f"✅ 文档清空成功: 删除了{len(blocks)}个块")
            
            return result
            
        except Exception as e:
            self.logger.error(f"清空文档失败: {e}")
            raise
    
    def update_document_title(self, document_id: str, title: str) -> bool:
        """
        更新文档标题
        
        Args:
            document_id: 文档ID
            title: 新标题
            
        Returns:
            更新是否成功
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.debug(f"更新文档标题: {document_id} -> {title}")
        
        endpoint = f"/open-apis/docx/v1/documents/{document_id}"
        
        request_data = {
            "title": title
        }
        
        try:
            response = self.client.patch(endpoint, data=request_data)
            
            if response.get("code") != 0:
                error_msg = response.get("msg", "未知错误")
                self.logger.error(f"更新标题失败: {error_msg}")
                raise FeishuAPIError(f"更新标题失败: {error_msg}", response.get("code"))
            
            self.logger.debug(f"✅ 标题更新成功: {title}")
            return True
            
        except FeishuAPIError:
            raise
        except Exception as e:
            self.logger.error(f"更新标题异常: {e}")
            raise FeishuAPIError(f"更新标题异常: {e}")
    
    def replace_document_content(
        self, 
        document_id: str, 
        blocks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        替换文档的全部内容
        
        Args:
            document_id: 文档ID
            blocks: 新的内容块列表
            
        Returns:
            创建的块ID列表
            
        Raises:
            FeishuAPIError: API调用失败
        """
        self.logger.info(f"替换文档内容: document_id={document_id}, 新块数量={len(blocks)}")
        
        try:
            # 1. 清空文档
            self.clear_document(document_id)
            
            # 2. 添加新内容
            if blocks:
                block_ids = self.create_blocks(document_id, blocks)
                self.logger.info(f"✅ 文档内容替换成功: 创建了{len(block_ids)}个块")
                return block_ids
            else:
                self.logger.info("✅ 文档内容已清空")
                return []
                
        except Exception as e:
            self.logger.error(f"替换文档内容失败: {e}")
            raise


# 便捷函数
def create_feishu_docs_client(feishu_client: FeishuClient) -> FeishuDocsClient:
    """
    创建飞书文档客户端实例
    
    Args:
        feishu_client: 飞书API客户端
        
    Returns:
        飞书文档客户端实例
    """
    return FeishuDocsClient(feishu_client) 