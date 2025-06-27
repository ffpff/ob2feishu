#!/usr/bin/env python3
"""
Markdown转换器演示脚本
展示如何将Markdown内容转换为飞书格式
"""

import sys
import os
import json
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.markdown_converter import convert_markdown_to_feishu


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_basic_conversion():
    """测试基本转换功能"""
    print("=" * 60)
    print("测试基本Markdown转换功能")
    print("=" * 60)
    
    # 测试用的Markdown内容
    markdown_content = """# AI编程助手使用指南

## 简介

AI编程助手是一个强大的工具，可以帮助开发者**提高编程效率**。

## 主要功能

### 核心特性

- 智能代码生成
- 实时错误诊断
- 性能优化建议
- 代码重构支持

### 支持的语言

1. Python
2. JavaScript/TypeScript
3. Java
4. C++

## 使用示例

### Python代码生成

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 使用示例
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
```

### JavaScript代码生成

```javascript
function greetUser(name) {
    return `Hello, ${name}! Welcome to AI Coding Assistant.`;
}

console.log(greetUser("开发者"));
```

## 注意事项

> **重要提醒**: 使用AI编程助手时，请始终review生成的代码，确保其符合你的项目需求和安全标准。

### 最佳实践

| 项目 | 建议 | 注意事项 |
|------|------|----------|
| 代码审查 | 必须进行 | 不要盲目信任 |
| 测试覆盖 | 至少80% | 包含边界情况 |
| 性能优化 | 渐进式 | 避免过度优化 |

---

## 总结

AI编程助手是现代开发者的得力工具，合理使用可以显著提升开发效率。

**记住**: 工具是为了帮助我们，而不是替代我们的思考。"""

    try:
        # 执行转换
        print("开始转换Markdown内容...")
        blocks = convert_markdown_to_feishu(markdown_content)
        
        print(f"✓ 转换成功！生成了 {len(blocks)} 个飞书块")
        print()
        
        # 分析转换结果
        analyze_conversion_result(blocks)
        
        # 显示部分结果
        show_sample_blocks(blocks)
        
        return blocks
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_conversion_result(blocks):
    """分析转换结果"""
    print("转换结果分析:")
    print("-" * 40)
    
    # 统计块类型
    block_types = {}
    total_blocks = len(blocks)
    
    def count_blocks(block_list, depth=0):
        for block in block_list:
            block_type = block.get('block_type', 'unknown')
            block_types[block_type] = block_types.get(block_type, 0) + 1
            
            # 递归统计子块
            if 'children' in block:
                count_blocks(block['children'], depth + 1)
    
    count_blocks(blocks)
    
    # 块类型映射
    type_names = {
        1: "页面", 2: "文本", 3: "标题1", 4: "标题2", 5: "标题3",
        6: "标题4", 7: "标题5", 8: "标题6", 9: "无序列表", 10: "有序列表",
        11: "代码块", 12: "引用", 19: "分割线", 28: "表格"
    }
    
    print(f"总块数: {total_blocks}")
    print("块类型分布:")
    for block_type, count in sorted(block_types.items()):
        type_name = type_names.get(block_type, f"类型{block_type}")
        print(f"  {type_name}: {count} 个")
    
    print()


def show_sample_blocks(blocks, max_blocks=5):
    """显示部分转换结果"""
    print(f"显示前 {min(max_blocks, len(blocks))} 个块的详细信息:")
    print("-" * 40)
    
    for i, block in enumerate(blocks[:max_blocks]):
        print(f"块 {i+1}:")
        print(f"  类型: {block.get('block_type')}")
        
        if 'text' in block:
            elements = block['text'].get('elements', [])
            if elements:
                text_content = elements[0].get('text', '')
                # 限制显示长度
                if len(text_content) > 50:
                    text_content = text_content[:50] + "..."
                print(f"  内容: {text_content}")
        
        if 'children' in block:
            print(f"  子块数: {len(block['children'])}")
        
        if 'code' in block:
            print(f"  代码语言: {block['code'].get('language', 'unknown')}")
        
        if 'table' in block:
            table_info = block['table']
            header_count = len(table_info.get('header', []))
            row_count = len(table_info.get('rows', []))
            print(f"  表格: {header_count} 列, {row_count} 行")
        
        print()


def test_obsidian_frontmatter():
    """测试Obsidian front-matter处理"""
    print("=" * 60)
    print("测试Obsidian Front-matter处理")
    print("=" * 60)
    
    markdown_with_frontmatter = """---
tags: ["飞书知识库", "AI编程", "工具使用"]
title: "AI编程最佳实践"
date: 2024-01-15
author: "开发团队"
---

# AI编程最佳实践

本文档总结了使用AI编程助手的最佳实践。

## 核心原则

- **审查优先**: 始终review生成的代码
- **测试驱动**: 为AI生成的代码编写测试
- **渐进改进**: 逐步优化和完善

> AI是工具，思考是本质。"""

    try:
        print("转换包含front-matter的Obsidian笔记...")
        blocks = convert_markdown_to_feishu(markdown_with_frontmatter)
        
        print(f"✓ 转换成功！生成了 {len(blocks)} 个飞书块")
        
        # 检查是否正确处理了front-matter（应该被忽略）
        first_block = blocks[0] if blocks else None
        if first_block and first_block.get('block_type') == 3:  # HEADING1
            text = first_block.get('text', {}).get('elements', [{}])[0].get('text', '')
            if text == "AI编程最佳实践":
                print("✓ Front-matter被正确忽略，第一个块是主标题")
            else:
                print(f"? 第一个块内容: {text}")
        
        return blocks
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return None


def test_chinese_content():
    """测试中文内容转换"""
    print("=" * 60)
    print("测试中文内容转换")
    print("=" * 60)
    
    chinese_markdown = """# 中文技术文档示例

## 概述

这是一个**中文技术文档**的示例，用于测试Markdown转换器对中文的支持。

### 功能特点

- 支持中文标题和段落
- 处理中文标点符号：！？，。
- 支持中英文混合内容

#### 代码示例

```python
# 中文注释示例
def 问候(姓名):
    \"\"\"
    简单的问候函数
    \"\"\"
    return f"你好，{姓名}！欢迎使用AI编程助手。"

# 使用示例
print(问候("张三"))
```

> 注意：中文编程实践在某些场景下是可行的，但需要考虑团队协作和维护性。

---

## 总结

中文内容转换测试完成。✅"""

    try:
        print("转换中文Markdown内容...")
        blocks = convert_markdown_to_feishu(chinese_markdown)
        
        print(f"✓ 转换成功！生成了 {len(blocks)} 个飞书块")
        
        # 检查中文处理
        analyze_conversion_result(blocks)
        
        return blocks
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return None


def save_conversion_result(blocks, filename="conversion_result.json"):
    """保存转换结果到文件"""
    if not blocks:
        print("没有转换结果可保存")
        return
    
    try:
        output_path = os.path.join(os.path.dirname(__file__), filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blocks, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 转换结果已保存到: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
        
    except Exception as e:
        print(f"✗ 保存失败: {e}")


def main():
    """主函数"""
    setup_logging()
    
    print("Markdown转换器演示")
    print("=" * 60)
    print()
    
    # 测试基本转换
    blocks1 = test_basic_conversion()
    
    print()
    
    # 测试front-matter处理
    blocks2 = test_obsidian_frontmatter()
    
    print()
    
    # 测试中文内容
    blocks3 = test_chinese_content()
    
    print()
    
    # 保存一个示例结果
    if blocks1:
        save_conversion_result(blocks1, "basic_conversion_result.json")
    
    print()
    print("=" * 60)
    print("演示完成！")
    print()
    print("转换器特点:")
    print("✓ 支持多种Markdown元素（标题、段落、列表、代码块等）")
    print("✓ 正确处理中文内容")
    print("✓ 自动忽略Obsidian front-matter")
    print("✓ 生成飞书API兼容的块结构")
    print("✓ 提供详细的转换分析")


if __name__ == "__main__":
    main() 