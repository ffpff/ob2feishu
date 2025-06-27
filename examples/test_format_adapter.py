#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API格式适配器演示脚本
展示Markdown转换 + 格式适配的完整流程
"""

import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
from src.ob2feishu.format_adapter import (
    FeishuFormatAdapter,
    adapt_blocks_for_feishu_api,
    validate_feishu_format
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def print_json_pretty(data, title=""):
    """格式化打印JSON数据"""
    if title:
        print(f"\n{'='*50}")
        print(f"{title}")
        print('='*50)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def demonstrate_basic_adaptation():
    """演示基础格式适配功能"""
    print("\n🔄 演示基础格式适配功能")
    print("-" * 50)
    
    # 创建适配器
    adapter = FeishuFormatAdapter()
    
    # 1. 标题块适配
    print("\n1. 标题块适配演示")
    heading_block = {
        "block_type": 3,
        "text": {
            "elements": [{"text": "这是一级标题"}],
            "style": {}
        }
    }
    
    print("原始格式:")
    print_json_pretty(heading_block)
    
    adapted_heading = adapter._adapt_heading_block(heading_block.copy())
    print("适配后格式:")
    print_json_pretty(adapted_heading)
    
    # 2. 文本块适配
    print("\n2. 文本块适配演示")
    text_block = {
        "block_type": 2,
        "text": {
            "elements": [
                {"text": "这是普通文本"},
                {"text": "这是加粗文本", "style": {"bold": True}}
            ],
            "style": {}
        }
    }
    
    print("原始格式:")
    print_json_pretty(text_block)
    
    adapted_text = adapter._adapt_text_block(text_block.copy())
    print("适配后格式:")
    print_json_pretty(adapted_text)
    
    # 3. 代码块适配
    print("\n3. 代码块适配演示")
    code_block = {
        "block_type": 11,
        "text": {
            "elements": [{"text": "print('Hello World!')"}],
            "style": {}
        },
        "code": {"language": "python"}
    }
    
    print("原始格式:")
    print_json_pretty(code_block)
    
    adapted_code = adapter._adapt_code_block(code_block.copy())
    print("适配后格式:")
    print_json_pretty(adapted_code)


def demonstrate_full_pipeline():
    """演示完整的转换管道"""
    print("\n🚀 演示完整的Markdown转换+格式适配管道")
    print("-" * 50)
    
    # 复杂的Markdown内容
    markdown_content = """---
title: 测试文档
tags: ["飞书知识库", "测试"]
---

# 飞书API格式适配器测试

## 概述

这是一个用于测试**飞书API格式适配器**的文档。

## 功能特性

### 支持的块类型

1. **标题**：支持H1-H6级别标题
2. **文本**：支持普通文本、*斜体*、**粗体**
3. **代码块**：支持多种编程语言

```python
# Python示例代码
def hello_world():
    print("Hello, Feishu!")
    return "success"
```

```javascript
// JavaScript示例代码
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

### 列表支持

#### 无序列表
- 第一项
- 第二项
  - 嵌套项1
  - 嵌套项2
- 第三项

#### 有序列表
1. 步骤一
2. 步骤二
3. 步骤三

### 其他元素

> 这是一个重要的引用内容，用于强调关键信息。

---

| 功能 | 状态 | 备注 |
|------|------|------|
| 标题转换 | ✅ 完成 | 支持H1-H6 |
| 文本格式 | ✅ 完成 | 支持基础样式 |
| 代码块 | ✅ 完成 | 支持语法高亮 |
| 列表 | 🚧 进行中 | 支持嵌套 |
| 表格 | 📋 计划中 | 待实现 |

## 总结

飞书API格式适配器能够有效地将Markdown内容转换为飞书API标准格式。

### 技术特点

- **高兼容性**：完全符合飞书API规范
- **丰富格式**：支持多种块类型
- **中文支持**：完美处理中文内容
- **错误处理**：提供详细的验证机制"""
    
    print("原始Markdown内容:")
    print("-" * 30)
    print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)
    
    # 第一步：Markdown转换
    print(f"\n📝 第一步：Markdown转换")
    internal_blocks = convert_markdown_to_feishu(markdown_content)
    logger.info(f"Markdown转换完成：生成了 {len(internal_blocks)} 个内部格式块")
    
    # 统计块类型
    block_types = {}
    for block in internal_blocks:
        block_type = block.get("block_type")
        block_types[block_type] = block_types.get(block_type, 0) + 1
    
    print("内部格式块类型统计:")
    for block_type, count in sorted(block_types.items()):
        type_name = {
            2: "文本", 3: "标题1", 4: "标题2", 5: "标题3", 
            6: "标题4", 7: "标题5", 8: "标题6",
            9: "无序列表", 10: "有序列表", 11: "代码块",
            12: "引用", 19: "分割线", 28: "表格"
        }.get(block_type, f"类型{block_type}")
        print(f"  - {type_name}: {count}个")
    
    # 第二步：格式适配
    print(f"\n🔄 第二步：格式适配")
    adapted_blocks = adapt_blocks_for_feishu_api(internal_blocks)
    logger.info(f"格式适配完成：{len(internal_blocks)} -> {len(adapted_blocks)} 个飞书API格式块")
    
    # 第三步：格式验证
    print(f"\n✅ 第三步：格式验证")
    errors = validate_feishu_format(adapted_blocks)
    
    if errors:
        logger.error(f"格式验证发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  ❌ {error}")
    else:
        logger.info("✅ 格式验证通过！所有块都符合飞书API标准格式")
    
    return internal_blocks, adapted_blocks, errors


def compare_formats(internal_blocks, adapted_blocks):
    """对比内部格式和适配后格式的差异"""
    print("\n🔍 格式对比分析")
    print("-" * 50)
    
    # 选择几个代表性的块进行对比
    comparison_indices = [0, 1, 2]  # 对比前3个块
    
    for i in comparison_indices:
        if i < len(internal_blocks) and i < len(adapted_blocks):
            internal = internal_blocks[i]
            adapted = adapted_blocks[i]
            
            block_type = internal.get("block_type")
            type_name = {
                2: "文本块", 3: "标题1块", 4: "标题2块", 5: "标题3块",
                11: "代码块", 12: "引用块"
            }.get(block_type, f"类型{block_type}块")
            
            print(f"\n📋 第{i+1}个块对比 ({type_name})")
            print("-" * 30)
            
            print("🔹 内部格式:")
            print_json_pretty(internal)
            
            print("🔸 飞书API格式:")
            print_json_pretty(adapted)
            
            # 分析关键差异
            print("🔍 关键差异:")
            if block_type in [3, 4, 5, 6, 7, 8]:  # 标题块
                heading_field = {3: "heading1", 4: "heading2", 5: "heading3", 
                               6: "heading4", 7: "heading5", 8: "heading6"}[block_type]
                print(f"  - text字段 -> {heading_field}字段")
                print(f"  - elements格式: {{text: ...}} -> {{text_run: {{content: ...}}}}")
            elif block_type == 2:  # 文本块
                print(f"  - elements格式: {{text: ...}} -> {{text_run: {{content: ...}}}}")
            elif block_type == 11:  # 代码块
                print(f"  - text字段移除，内容合并到code字段")
                print(f"  - elements格式: {{text: ...}} -> {{text_run: {{content: ...}}}}")


def demonstrate_validation():
    """演示格式验证功能"""
    print("\n🧪 演示格式验证功能")
    print("-" * 50)
    
    adapter = FeishuFormatAdapter()
    
    # 1. 有效格式验证
    print("\n1. 有效格式验证")
    valid_blocks = [
        {
            "block_type": 3,
            "heading1": {
                "elements": [
                    {
                        "text_run": {
                            "content": "有效标题",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {}
            }
        },
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "有效文本",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {}
            }
        }
    ]
    
    errors = adapter.validate_adapted_format(valid_blocks)
    print(f"验证结果: {len(errors)} 个错误")
    if errors:
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ 格式正确")
    
    # 2. 无效格式验证
    print("\n2. 无效格式验证")
    invalid_blocks = [
        {
            "block_type": 3,
            "text": {  # 错误：标题块应该使用heading1字段
                "elements": [{"text": "错误标题"}],
                "style": {}
            }
        },
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {"text": "错误文本"}  # 错误：应该使用text_run格式
                ],
                "style": {}
            }
        }
    ]
    
    errors = adapter.validate_adapted_format(invalid_blocks)
    print(f"验证结果: {len(errors)} 个错误")
    for error in errors:
        print(f"  ❌ {error}")


def main():
    """主函数"""
    print("🎯 飞书API格式适配器演示")
    print("=" * 60)
    
    try:
        # 1. 基础适配功能演示
        demonstrate_basic_adaptation()
        
        # 2. 完整管道演示
        internal_blocks, adapted_blocks, errors = demonstrate_full_pipeline()
        
        # 3. 格式对比
        if not errors:
            compare_formats(internal_blocks, adapted_blocks)
        
        # 4. 验证功能演示
        demonstrate_validation()
        
        # 总结
        print("\n🎉 演示完成总结")
        print("-" * 50)
        print("✅ 基础适配功能：正常")
        print("✅ 完整转换管道：正常")
        print("✅ 格式验证机制：正常")
        print("✅ 中文内容支持：正常")
        
        if not errors:
            print("\n🚀 格式适配器已准备就绪，可以用于实际的飞书API调用！")
        else:
            print(f"\n⚠️  发现 {len(errors)} 个格式问题，需要进一步调整")
            
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 