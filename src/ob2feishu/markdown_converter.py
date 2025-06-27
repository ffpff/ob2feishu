#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown到飞书格式转换器

简化版本：只生成文本块，避免复杂的块类型
"""

import re
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FeishuBlockType(Enum):
    """飞书块类型枚举"""
    PAGE = 1
    TEXT = 2            # 文本块
    HEADING1 = 3
    HEADING2 = 4
    HEADING3 = 5
    HEADING4 = 6
    HEADING5 = 7
    HEADING6 = 8
    UNORDERED_LIST = 12  # 无序列表
    ORDERED_LIST = 13    # 有序列表
    CODE = 14           # 代码块
    QUOTE = 15          # 引用块


@dataclass
class FeishuTextElement:
    """飞书文本元素"""
    text: str
    style: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为飞书API所需的text_run格式"""
        element = {
            "text_run": {
                "content": self.text,
                "text_element_style": self.style or {}
            }
        }
        return element


def create_text_block(content: str, style: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    创建简单的文本块
    
    Args:
        content: 文本内容
        style: 文本样式（bold, italic等）
        
    Returns:
        飞书文本块字典
    """
    if not content.strip():
        return None
    
    text_element = FeishuTextElement(text=content, style=style)
    
    return {
        "block_type": FeishuBlockType.TEXT.value,
        "text": {
            "elements": [text_element.to_dict()],
            "style": {}
        }
    }


def convert_markdown_to_feishu(markdown_content: str) -> List[Dict[str, Any]]:
    """
    将Markdown内容转换为飞书块结构的简化版本
    
    Args:
        markdown_content: Markdown文本内容
        
    Returns:
        飞书块结构的字典列表（只包含文本块）
    """
    # 预处理：移除YAML front-matter
    processed_content = _remove_frontmatter(markdown_content)
    
    lines = processed_content.split('\n')
    blocks = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 跳过空行
        if not line.strip():
            i += 1
            continue
        
        # 处理标题
        if line.startswith('#'):
            block = _process_heading(line)
            if block:
                blocks.append(block)
            i += 1
            continue
        
        # 处理列表
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            # 处理列表项，保留内联格式
            list_content = re.sub(r'^\s*[-*+]\s+', '• ', line)
            list_content = re.sub(r'^\s*\d+\.\s+', '1. ', list_content)
            
            # 解析列表项中的内联格式
            formatted_elements = _parse_inline_formatting(list_content)
            if formatted_elements:
                block = {
                    "block_type": FeishuBlockType.TEXT.value,
                    "text": {
                        "elements": [elem.to_dict() for elem in formatted_elements],
                        "style": {}
                    }
                }
                blocks.append(block)
            i += 1
            continue
        
        # 处理引用
        if line.strip().startswith('>'):
            quote_content = re.sub(r'^\s*>\s*', '', line)
            block = create_text_block(f"引用：{quote_content}", {"italic": True})
            if block:
                blocks.append(block)
            i += 1
            continue
        
        # 处理代码块
        if line.strip().startswith('```'):
            # 提取语言类型（如果有）
            first_line = line.strip()
            language = first_line[3:].strip() if len(first_line) > 3 else ""
            
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_content = '\n'.join(code_lines)
                # 创建真正的代码块
                block = {
                    "block_type": FeishuBlockType.CODE.value,
                    "code": {
                        "language": language or "plain",
                        "elements": [
                            {
                                "text_run": {
                                    "content": code_content
                                }
                            }
                        ]
                    }
                }
                blocks.append(block)
            i += 1
            continue
        
        # 处理分割线
        if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', line.strip()):
            block = create_text_block("───────────────────")
            if block:
                blocks.append(block)
            i += 1
            continue
        
        # 处理普通段落（带内联格式）
        formatted_elements = _parse_inline_formatting(line.strip())
        if formatted_elements:
            block = {
                "block_type": FeishuBlockType.TEXT.value,
                "text": {
                    "elements": [elem.to_dict() for elem in formatted_elements],
                    "style": {}
                }
            }
            blocks.append(block)
        
        i += 1
    
    # 过滤掉空块
    return [block for block in blocks if block]


def _remove_frontmatter(content: str) -> str:
    """移除YAML front-matter"""
    lines = content.split('\n')
    
    if not lines or lines[0].strip() != '---':
        return content
    
    # 查找结束的---
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break
    
    if end_index == -1:
        return content
    
    return '\n'.join(lines[end_index + 1:])


def _process_heading(line: str) -> Optional[Dict[str, Any]]:
    """处理标题行，转换为粗体文本（不显示#号）"""
    # 计算标题级别
    level = 0
    for char in line:
        if char == '#':
            level += 1
        else:
            break
    
    # 提取标题文本
    title_text = line[level:].strip()
    if not title_text:
        return None
    
    # 根据级别创建不同样式的文本（不显示#号）
    if level == 1:
        # 一级标题：大字号粗体
        content = title_text
        style = {"bold": True}
    elif level == 2:
        # 二级标题：粗体，前面加缩进
        content = f"  {title_text}"
        style = {"bold": True}
    elif level == 3:
        # 三级标题：粗体，更多缩进
        content = f"    {title_text}"
        style = {"bold": True}
    else:
        # 其他标题：粗体，根据级别缩进
        indent = "  " * (level - 1)
        content = f"{indent}{title_text}"
        style = {"bold": True}
    
    return create_text_block(content, style)


def _parse_inline_formatting(text: str) -> List[FeishuTextElement]:
    """
    解析内联格式（粗体、斜体、内联代码）
    
    支持：**粗体**、*斜体*、`代码`
    """
    elements = []
    
    if not text:
        return elements
    
    # 定义所有格式的正则表达式（按优先级排序）
    patterns = [
        (r'\*\*(.+?)\*\*', {"bold": True}),           # **粗体**
        (r'(?<!\*)\*([^*\s][^*]*?[^*\s]|\w)\*(?!\*)', {"italic": True}),  # *斜体*（更精确的匹配）
        (r'`([^`]+?)`', {"inline_code": True}),       # `代码`
    ]
    
    # 找到所有格式化文本的位置和类型
    all_matches = []
    for pattern, style in patterns:
        for match in re.finditer(pattern, text):
            all_matches.append({
                'start': match.start(),
                'end': match.end(),
                'text': match.group(1),
                'style': style,
                'full_match': match.group(0)
            })
    
    # 按开始位置排序
    all_matches.sort(key=lambda x: x['start'])
    
    # 处理重叠的匹配（优先处理更长的匹配）
    filtered_matches = []
    for match in all_matches:
        # 检查是否与已有匹配重叠
        overlapped = False
        for existing in filtered_matches:
            if (match['start'] < existing['end'] and match['end'] > existing['start']):
                overlapped = True
                break
        
        if not overlapped:
            filtered_matches.append(match)
    
    # 如果没有格式化文本，返回纯文本
    if not filtered_matches:
        elements.append(FeishuTextElement(text=text))
        return elements
    
    # 构建元素列表
    current_pos = 0
    
    for match in filtered_matches:
        # 添加匹配前的普通文本
        if match['start'] > current_pos:
            normal_text = text[current_pos:match['start']]
            if normal_text:
                elements.append(FeishuTextElement(text=normal_text))
        
        # 添加格式化文本
        elements.append(FeishuTextElement(text=match['text'], style=match['style']))
        
        current_pos = match['end']
    
    # 添加最后的普通文本
    if current_pos < len(text):
        remaining_text = text[current_pos:]
        if remaining_text:
            elements.append(FeishuTextElement(text=remaining_text))
    
    return elements


# 向后兼容的函数
def create_markdown_converter():
    """创建Markdown转换器的便捷函数（向后兼容）"""
    return None  # 不再需要类实例


# 主要的转换函数已经是 convert_markdown_to_feishu 