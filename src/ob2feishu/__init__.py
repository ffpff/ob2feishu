"""
Obsidian到飞书知识库同步工具

这是一个将Obsidian笔记同步到飞书知识库的Python工具。
支持增量同步、格式转换、批量处理等功能。
"""

__version__ = "0.1.0"
__author__ = "Obsidian2Feishu Team"
__email__ = ""
__description__ = "将Obsidian笔记同步到飞书知识库的工具"

# 导入主要模块
from .config import Config, get_config
from .feishu_client import FeishuClient, FeishuAPIError
from .obsidian_parser import ObsidianParser, ObsidianNote
from .markdown_converter import convert_markdown_to_feishu
from .format_adapter import FeishuFormatAdapter, adapt_blocks_for_feishu_api, validate_feishu_format
from .feishu_docs import FeishuDocsClient, FeishuDocument, create_feishu_docs_client

__all__ = [
    "Config",
    "get_config",
    "FeishuClient", 
    "FeishuAPIError",
    "ObsidianParser",
    "ObsidianNote",

    "convert_markdown_to_feishu",
    "FeishuFormatAdapter",
    "adapt_blocks_for_feishu_api",
    "validate_feishu_format",
    "FeishuDocsClient",
    "FeishuDocument",
    "create_feishu_docs_client"
] 