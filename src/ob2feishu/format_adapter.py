"""
飞书API格式适配器模块
将内部Markdown转换格式适配为飞书API标准格式
"""

import copy
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FeishuFormatAdapter:
    """飞书API格式适配器"""
    
    def __init__(self):
        """初始化适配器"""
        # 标题块类型到字段名的映射
        self.heading_field_map = {
            3: "heading1",
            4: "heading2", 
            5: "heading3",
            6: "heading4",
            7: "heading5",
            8: "heading6"
        }
    
    def adapt_blocks_for_api(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将内部格式的块列表适配为飞书API格式
        
        Args:
            blocks: 内部格式的块列表
            
        Returns:
            适配后的飞书API格式块列表
        """
        logger.debug(f"开始适配 {len(blocks)} 个块为飞书API格式")
        
        adapted_blocks = []
        
        for i, block in enumerate(blocks):
            try:
                adapted_block = self._adapt_single_block(block)
                if adapted_block:
                    adapted_blocks.append(adapted_block)
                    logger.debug(f"成功适配块 {i+1}, 类型: {block.get('block_type')}")
                else:
                    logger.warning(f"跳过不支持的块 {i+1}, 类型: {block.get('block_type')}")
            except Exception as e:
                logger.error(f"适配块 {i+1} 时出错: {e}")
                continue
        
        logger.info(f"适配完成: {len(blocks)} -> {len(adapted_blocks)} 个块")
        return adapted_blocks
    
    def _adapt_single_block(self, block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        适配单个块
        
        Args:
            block: 内部格式的块
            
        Returns:
            适配后的飞书API格式块，如果不支持则返回None
        """
        # 深拷贝避免修改原始数据
        adapted_block = copy.deepcopy(block)
        block_type = adapted_block.get("block_type")
        
        if block_type in [3, 4, 5, 6, 7, 8]:  # 标题块
            return self._adapt_heading_block(adapted_block)
        elif block_type == 2:  # 文本块
            return self._adapt_text_block(adapted_block)
        elif block_type == 11:  # 代码块
            return self._adapt_code_block(adapted_block)
        elif block_type in [9, 10]:  # 列表块
            return self._adapt_list_block(adapted_block)
        elif block_type == 12:  # 引用块
            return self._adapt_quote_block(adapted_block)
        elif block_type == 28:  # 表格块
            return self._adapt_table_block(adapted_block)
        elif block_type == 19:  # 分割线
            return self._adapt_divider_block(adapted_block)
        else:
            logger.warning(f"不支持的块类型: {block_type}")
            return None
    
    def _adapt_heading_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配标题块：使用heading1-6专用字段
        
        从: {block_type: 3, text: {elements: [{text: "标题"}]}}
        到: {block_type: 3, heading1: {elements: [{text_run: {content: "标题"}}]}}
        """
        block_type = block["block_type"]
        heading_field = self.heading_field_map.get(block_type)
        
        if not heading_field:
            raise ValueError(f"无效的标题块类型: {block_type}")
        
        # 获取原始text内容
        text_data = block.pop("text", {})
        elements = text_data.get("elements", [])
        
        # 转换为标题专用字段
        block[heading_field] = {
            "elements": self._convert_elements_to_text_run(elements),
            "style": text_data.get("style", {})
        }
        
        logger.debug(f"适配标题块: 类型{block_type} -> {heading_field}字段")
        return block
    
    def _adapt_text_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配文本块：转换elements格式
        
        从: {text: "内容"}
        到: {text_run: {content: "内容", text_element_style: {}}}
        """
        if "text" in block:
            text_data = block["text"]
            elements = text_data.get("elements", [])
            
            # 转换elements格式
            text_data["elements"] = self._convert_elements_to_text_run(elements)
        
        return block
    
    def _adapt_code_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配代码块：使用标准code字段结构
        
        从: {block_type: 11, text: {elements: [{text: "code"}]}, code: {language: "python"}}
        到: {block_type: 11, code: {language: "python", elements: [...]}}
        """
        # 获取代码内容
        text_data = block.pop("text", {})
        elements = text_data.get("elements", [])
        
        # 获取代码语言信息
        code_info = block.get("code", {})
        language = code_info.get("language", "plain")
        
        # 重新构建code字段
        block["code"] = {
            "language": language,
            "elements": self._convert_elements_to_text_run(elements)
        }
        
        logger.debug(f"适配代码块: 语言 {language}")
        return block
    
    def _adapt_list_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配列表块：处理子项格式
        """
        block_type = block["block_type"]
        
        # 根据列表类型添加相应字段
        if block_type == 9:  # 无序列表
            list_field = "bullet_list"
        elif block_type == 10:  # 有序列表
            list_field = "ordered_list"
        else:
            raise ValueError(f"无效的列表块类型: {block_type}")
        
        # 处理子项
        children = block.get("children", [])
        adapted_children = []
        
        for child in children:
            adapted_child = self._adapt_single_block(child)
            if adapted_child:
                adapted_children.append(adapted_child)
        
        block["children"] = adapted_children
        
        # 添加列表特定字段（保持为空，由子项提供内容）
        block[list_field] = {
            "elements": [
                {
                    "text_run": {
                        "content": "",
                        "text_element_style": {}
                    }
                }
            ],
            "style": {}
        }
        
        logger.debug(f"适配列表块: {list_field}, {len(adapted_children)} 个子项")
        return block
    
    def _adapt_quote_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配引用块：转换text元素格式
        """
        if "text" in block:
            text_data = block["text"]
            elements = text_data.get("elements", [])
            text_data["elements"] = self._convert_elements_to_text_run(elements)
        
        return block
    
    def _adapt_table_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配表格块：转换为飞书表格格式
        
        注意：这是一个简化实现，实际表格创建可能需要先创建表格再填充内容
        """
        table_data = block.get("table", {})
        
        if "header" in table_data and "rows" in table_data:
            header = table_data["header"]
            rows = table_data["rows"]
            
            # 转换为飞书表格格式（简化版本）
            # 实际实现中可能需要调用表格创建API
            block["table"] = {
                "rowSize": len(rows) + 1,  # +1 for header
                "columnSize": len(header) if header else 0,
                "table_range": f"A1:{chr(65 + len(header) - 1)}{len(rows) + 1}" if header else "A1:A1"
            }
            
            # 保存原始数据用于后续填充
            block["_original_table_data"] = {
                "header": header,
                "rows": rows
            }
        
        logger.debug(f"适配表格块: {table_data.get('header', [])} x {len(table_data.get('rows', []))}")
        return block
    
    def _adapt_divider_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        适配分割线块：分割线通常不需要额外内容
        """
        # 分割线块通常只需要block_type
        return {
            "block_type": block["block_type"]
        }
    
    def _convert_elements_to_text_run(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将内部elements格式转换为飞书API的text_run格式
        
        从: [{text: "内容", style: {...}}]
        到: [{text_run: {content: "内容", text_element_style: {...}}}]
        """
        converted_elements = []
        
        for element in elements:
            if "text" in element:
                # 基本转换
                text_run = {
                    "content": element["text"],
                    "text_element_style": element.get("style", {})
                }
                
                converted_elements.append({
                    "text_run": text_run
                })
            else:
                # 如果已经是text_run格式，保持不变
                converted_elements.append(element)
        
        return converted_elements
    
    def validate_adapted_format(self, blocks: List[Dict[str, Any]]) -> List[str]:
        """
        验证适配后的格式是否符合飞书API要求
        
        Args:
            blocks: 适配后的块列表
            
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        for i, block in enumerate(blocks):
            block_errors = self._validate_single_block(block, i)
            errors.extend(block_errors)
        
        return errors
    
    def _validate_single_block(self, block: Dict[str, Any], index: int) -> List[str]:
        """验证单个块的格式"""
        errors = []
        block_type = block.get("block_type")
        
        if not block_type:
            errors.append(f"块{index}: 缺少block_type字段")
            return errors
        
        # 验证标题块
        if block_type in [3, 4, 5, 6, 7, 8]:
            heading_field = self.heading_field_map.get(block_type)
            if heading_field not in block:
                errors.append(f"块{index}: 标题块缺少{heading_field}字段")
            elif "text" in block:
                errors.append(f"块{index}: 标题块不应包含text字段")
        
        # 验证文本块
        elif block_type == 2:
            if "text" not in block:
                errors.append(f"块{index}: 文本块缺少text字段")
            else:
                text_errors = self._validate_text_elements(block["text"], index)
                errors.extend(text_errors)
        
        # 验证代码块
        elif block_type == 11:
            if "code" not in block:
                errors.append(f"块{index}: 代码块缺少code字段")
            elif "text" in block:
                errors.append(f"块{index}: 代码块不应包含text字段")
        
        return errors
    
    def _validate_text_elements(self, text_obj: Dict[str, Any], block_index: int) -> List[str]:
        """验证text对象中的elements格式"""
        errors = []
        elements = text_obj.get("elements", [])
        
        for i, element in enumerate(elements):
            if "text_run" not in element:
                errors.append(f"块{block_index}.elements[{i}]: 缺少text_run字段")
            elif "text" in element:
                errors.append(f"块{block_index}.elements[{i}]: 不应包含text字段")
        
        return errors


def adapt_blocks_for_feishu_api(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将内部格式的块列表适配为飞书API格式的便捷函数
    
    Args:
        blocks: 内部格式的块列表
        
    Returns:
        适配后的飞书API格式块列表
    """
    adapter = FeishuFormatAdapter()
    return adapter.adapt_blocks_for_api(blocks)


def validate_feishu_format(blocks: List[Dict[str, Any]]) -> List[str]:
    """
    验证块列表是否符合飞书API格式要求的便捷函数
    
    Args:
        blocks: 要验证的块列表
        
    Returns:
        错误信息列表，空列表表示验证通过
    """
    adapter = FeishuFormatAdapter()
    return adapter.validate_adapted_format(blocks) 