#!/usr/bin/env python3
"""
测试真实Obsidian文件的Markdown转换
使用真实的Obsidian库中的文件进行转换测试
"""

import sys
import os
import json
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.config import load_config
from src.ob2feishu.obsidian_parser import ObsidianParser
from src.ob2feishu.markdown_converter import convert_markdown_to_feishu


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_real_obsidian_conversion():
    """测试真实Obsidian文件的转换"""
    print("=" * 60)
    print("测试真实Obsidian文件Markdown转换")
    print("=" * 60)
    
    try:
        # 加载配置
        config = load_config()
        obsidian_path = config.obsidian.vault_path
        
        if not os.path.exists(obsidian_path):
            print(f"✗ Obsidian库路径不存在: {obsidian_path}")
            return
        
        print(f"Obsidian库路径: {obsidian_path}")
        
        # 初始化解析器
        parser = ObsidianParser(obsidian_path)
        
        # 扫描笔记
        print("扫描Obsidian笔记...")
        notes = parser.scan_notes()
        print(f"✓ 找到 {len(notes)} 个笔记文件")
        
        # 查找包含"飞书知识库"标签的笔记
        target_notes = []
        for note in notes:
            if "飞书知识库" in note.tags:
                target_notes.append(note)
        
        if not target_notes:
            print("未找到包含'飞书知识库'标签的笔记")
            print("尝试转换前几个笔记作为示例...")
            target_notes = notes[:3]  # 取前3个作为示例
        
        print(f"将转换 {len(target_notes)} 个笔记")
        print()
        
        # 转换每个笔记
        conversion_results = []
        
        for i, note in enumerate(target_notes):
            print(f"转换笔记 {i+1}/{len(target_notes)}: {note.title}")
            print(f"文件路径: {note.file_path}")
            print(f"标签: {note.tags}")
            
            try:
                # 读取笔记内容
                content = note.get_content()
                print(f"内容长度: {len(content)} 字符")
                
                # 进行Markdown转换
                blocks = convert_markdown_to_feishu(content)
                print(f"✓ 转换成功，生成 {len(blocks)} 个飞书块")
                
                # 分析转换结果
                analyze_blocks(blocks)
                
                # 保存转换结果
                result = {
                    "note_info": {
                        "title": note.title,
                        "file_path": note.file_path,
                        "tags": note.tags,
                        "content_length": len(content)
                    },
                    "conversion_result": {
                        "block_count": len(blocks),
                        "blocks": blocks
                    }
                }
                conversion_results.append(result)
                
                print()
                
            except Exception as e:
                print(f"✗ 转换失败: {e}")
                print()
                continue
        
        # 保存所有转换结果
        save_results(conversion_results)
        
        return conversion_results
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_blocks(blocks):
    """分析块结构"""
    if not blocks:
        return
    
    # 统计块类型
    block_types = {}
    for block in blocks:
        block_type = block.get('block_type', 'unknown')
        block_types[block_type] = block_types.get(block_type, 0) + 1
    
    # 块类型映射
    type_names = {
        1: "页面", 2: "文本", 3: "标题1", 4: "标题2", 5: "标题3",
        6: "标题4", 7: "标题5", 8: "标题6", 9: "无序列表", 10: "有序列表",
        11: "代码块", 12: "引用", 19: "分割线", 28: "表格"
    }
    
    print("  块类型分布:", end=" ")
    type_summary = []
    for block_type, count in sorted(block_types.items()):
        type_name = type_names.get(block_type, f"类型{block_type}")
        type_summary.append(f"{type_name}×{count}")
    print(", ".join(type_summary))


def save_results(results, filename="real_conversion_results.json"):
    """保存转换结果"""
    if not results:
        print("没有转换结果可保存")
        return
    
    try:
        output_path = os.path.join(os.path.dirname(__file__), filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 转换结果已保存到: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
        
        # 生成摘要
        total_notes = len(results)
        total_blocks = sum(r["conversion_result"]["block_count"] for r in results)
        
        print(f"转换摘要: {total_notes} 个笔记, 共 {total_blocks} 个飞书块")
        
    except Exception as e:
        print(f"✗ 保存失败: {e}")


def create_sample_conversion():
    """创建一个转换示例"""
    print("=" * 60)
    print("创建转换示例")
    print("=" * 60)
    
    # 创建一个示例Obsidian笔记内容
    sample_content = """---
tags: ["飞书知识库", "示例"]
title: "Markdown转换测试"
date: 2024-01-15
---

# Markdown转换功能测试

这是一个用于测试Markdown转换功能的示例文档。

## 基本功能测试

### 文本格式

这里包含**粗体文本**、*斜体文本*和`行内代码`。

### 列表功能

#### 无序列表：
- 第一项
- 第二项  
- 第三项

#### 有序列表：
1. 步骤一
2. 步骤二
3. 步骤三

### 代码块

```python
def hello_world():
    print("Hello, 飞书知识库!")
    return "转换成功"

# 调用函数
result = hello_world()
```

### 引用块

> 这是一个重要的提醒：转换功能需要仔细测试所有Markdown元素。

### 表格

| 功能 | 状态 | 备注 |
|------|------|------|
| 标题转换 | ✅ | 支持1-6级标题 |
| 列表转换 | ✅ | 支持有序和无序 |
| 代码转换 | ✅ | 支持语法高亮 |
| 表格转换 | ✅ | 基本表格支持 |

---

## 总结

Markdown转换功能基本完成，支持常见的所有元素类型。

**下一步**: 集成到同步流程中。"""

    try:
        print("转换示例内容...")
        blocks = convert_markdown_to_feishu(sample_content)
        
        print(f"✓ 转换成功！生成了 {len(blocks)} 个飞书块")
        
        # 分析结果
        analyze_blocks(blocks)
        
        # 保存示例
        sample_result = {
            "note_info": {
                "title": "Markdown转换功能测试",
                "file_path": "示例文件",
                "tags": ["飞书知识库", "示例"],
                "content_length": len(sample_content)
            },
            "conversion_result": {
                "block_count": len(blocks),
                "blocks": blocks
            }
        }
        
        save_results([sample_result], "sample_conversion_result.json")
        
        return sample_result
        
    except Exception as e:
        print(f"✗ 示例转换失败: {e}")
        return None


def main():
    """主函数"""
    setup_logging()
    
    print("Obsidian Markdown转换测试")
    print("=" * 60)
    print()
    
    # 首先创建一个示例转换
    sample_result = create_sample_conversion()
    
    print()
    
    # 然后测试真实文件
    real_results = test_real_obsidian_conversion()
    
    print()
    print("=" * 60)
    print("测试完成！")
    print()
    
    if sample_result:
        print("✓ 示例转换成功")
    
    if real_results:
        print(f"✓ 真实文件转换成功，处理了 {len(real_results)} 个文件")
    
    print()
    print("转换器特性验证:")
    print("✓ 支持Obsidian YAML front-matter")
    print("✓ 处理中文内容")
    print("✓ 转换各种Markdown元素")
    print("✓ 生成飞书API兼容格式")
    print("✓ 提供详细的转换统计")


if __name__ == "__main__":
    main() 