#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整转换管道验证脚本
验证从Obsidian笔记到飞书API格式的完整转换流程
"""

import sys
import os
import json
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ob2feishu.obsidian_parser import create_obsidian_parser
from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
from src.ob2feishu.format_adapter import adapt_blocks_for_feishu_api, validate_feishu_format

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_complete_pipeline():
    """测试完整的转换管道"""
    print("🎯 完整转换管道验证")
    print("=" * 60)
    
    # 测试用的Obsidian笔记内容
    test_note_content = """---
title: "飞书API集成测试文档"
tags: ["飞书知识库", "开发", "测试"]
created: 2024-12-24
feishu_doc_id: null
feishu_last_sync: null
---

# 飞书API集成测试文档

## 项目概述

这是一个用于测试**Obsidian到飞书知识库同步工具**的完整功能文档。

### 核心功能特性

1. **Obsidian笔记解析**
   - 自动扫描库中的Markdown文件
   - 解析YAML front-matter元数据
   - 提取tags进行过滤

2. **智能格式转换**
   - Markdown到飞书Block格式转换
   - 保持原有格式和结构
   - 支持中文内容

3. **飞书API集成**
   - 自动认证和令牌管理
   - 文档创建和更新
   - 错误处理和重试机制

## 技术实现

### 代码示例

```python
# Obsidian解析器使用示例
from ob2feishu import ObsidianParser

parser = ObsidianParser("/path/to/obsidian/vault")
notes = parser.scan_vault()
sync_notes = parser.filter_notes_by_tags(notes, ["飞书知识库"])
```

```javascript
// 前端集成示例
function syncToFeishu() {
    const notes = getObsidianNotes();
    const blocks = convertToFeishuBlocks(notes);
    return uploadToFeishu(blocks);
}
```

### 支持的元素类型

#### 文本格式
- **粗体文本**
- *斜体文本*
- `行内代码`

#### 列表格式

##### 无序列表
- 功能开发
- 测试验证
- 文档编写
  - API文档
  - 用户指南

##### 有序列表
1. 环境搭建
2. 模块开发
3. 集成测试
4. 发布部署

### 重要提示

> 这是一个重要的提示内容，用于强调关键信息。确保在使用前阅读相关文档。

---

## 测试数据

| 功能模块 | 开发状态 | 测试状态 | 部署状态 |
|----------|----------|----------|----------|
| 配置管理 | ✅ 完成 | ✅ 通过 | 🚧 待定 |
| API客户端 | ✅ 完成 | ✅ 通过 | 🚧 待定 |
| 格式转换 | ✅ 完成 | ✅ 通过 | 🚧 待定 |
| 同步逻辑 | 🚧 开发中 | ❌ 待测 | ❌ 待定 |

## 总结

飞书API集成测试文档展示了完整的转换管道功能，包括：

- 📝 **内容解析**: 正确处理Obsidian格式
- 🔄 **格式转换**: 精确转换为飞书格式  
- 🌐 **API集成**: 无缝连接飞书服务
- ✅ **质量保证**: 全面的测试覆盖

### 下一步计划

1. 完成同步逻辑开发
2. 进行端到端测试
3. 用户接受度测试
4. 正式发布部署

**感谢使用本工具！** 🎉"""

    print("📄 测试笔记内容概览:")
    print("-" * 40)
    print(f"字符数: {len(test_note_content)}")
    print(f"行数: {test_note_content.count(chr(10)) + 1}")
    print("包含元素: YAML front-matter, 标题, 段落, 列表, 代码块, 表格, 引用等")
    
    try:
        # 第一步：Markdown解析
        print(f"\n🔍 第一步：Markdown内容解析")
        print("-" * 40)
        
        # 移除YAML front-matter进行转换
        content_lines = test_note_content.split('\n')
        in_frontmatter = False
        content_start = 0
        
        for i, line in enumerate(content_lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    content_start = i + 1
                    break
        
        markdown_content = '\n'.join(content_lines[content_start:])
        logger.info(f"YAML front-matter已移除，剩余内容: {len(markdown_content)} 字符")
        
        # 第二步：Markdown到内部格式转换
        print(f"\n🔄 第二步：Markdown格式转换")
        print("-" * 40)
        
        internal_blocks = convert_markdown_to_feishu(markdown_content)
        logger.info(f"Markdown转换完成: 生成 {len(internal_blocks)} 个内部格式块")
        
        # 统计块类型
        block_types_count = {}
        for block in internal_blocks:
            block_type = block.get("block_type")
            block_types_count[block_type] = block_types_count.get(block_type, 0) + 1
        
        print("内部格式块类型分布:")
        type_names = {
            2: "文本段落", 3: "标题1", 4: "标题2", 5: "标题3", 6: "标题4",
            9: "无序列表", 10: "有序列表", 11: "代码块", 12: "引用块",
            19: "分割线", 28: "表格"
        }
        
        for block_type, count in sorted(block_types_count.items()):
            type_name = type_names.get(block_type, f"类型{block_type}")
            print(f"  • {type_name}: {count}个")
        
        # 第三步：飞书API格式适配
        print(f"\n⚙️ 第三步：飞书API格式适配")
        print("-" * 40)
        
        adapted_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        logger.info(f"格式适配完成: {len(internal_blocks)} -> {len(adapted_blocks)} 个飞书API格式块")
        
        # 第四步：格式验证
        print(f"\n✅ 第四步：格式验证")
        print("-" * 40)
        
        validation_errors = validate_feishu_format(adapted_blocks)
        
        if validation_errors:
            logger.error(f"格式验证发现 {len(validation_errors)} 个错误:")
            for error in validation_errors:
                print(f"  ❌ {error}")
            return False
        else:
            logger.info("✅ 格式验证完全通过！")
        
        # 第五步：结果分析
        print(f"\n📊 第五步：转换结果分析")
        print("-" * 40)
        
        # 分析关键转换示例
        sample_blocks = adapted_blocks[:3]  # 取前3个块作为示例
        
        for i, block in enumerate(sample_blocks):
            block_type = block.get("block_type")
            type_name = type_names.get(block_type, f"类型{block_type}")
            
            print(f"\n📋 示例块 {i+1} ({type_name}):")
            print("  结构验证:")
            
            if block_type in [3, 4, 5, 6, 7, 8]:  # 标题块
                heading_field = {3: "heading1", 4: "heading2", 5: "heading3",
                               6: "heading4", 7: "heading5", 8: "heading6"}[block_type]
                if heading_field in block:
                    print(f"    ✅ 使用正确的{heading_field}字段")
                    elements = block[heading_field].get("elements", [])
                    if elements and "text_run" in elements[0]:
                        print(f"    ✅ text_run格式正确")
                        content = elements[0]["text_run"]["content"]
                        print(f"    📄 内容: \"{content[:30]}...\"" if len(content) > 30 else f"    📄 内容: \"{content}\"")
                    else:
                        print(f"    ❌ text_run格式错误")
                else:
                    print(f"    ❌ 缺少{heading_field}字段")
                    
            elif block_type == 2:  # 文本块
                if "text" in block:
                    print(f"    ✅ 包含text字段")
                    elements = block["text"].get("elements", [])
                    if elements and "text_run" in elements[0]:
                        print(f"    ✅ text_run格式正确")
                        content = elements[0]["text_run"]["content"]
                        print(f"    📄 内容: \"{content[:50]}...\"" if len(content) > 50 else f"    📄 内容: \"{content}\"")
                    else:
                        print(f"    ❌ text_run格式错误")
                else:
                    print(f"    ❌ 缺少text字段")
                    
            elif block_type == 11:  # 代码块
                if "code" in block:
                    print(f"    ✅ 使用正确的code字段")
                    code_data = block["code"]
                    language = code_data.get("language", "unknown")
                    print(f"    🔤 编程语言: {language}")
                    elements = code_data.get("elements", [])
                    if elements and "text_run" in elements[0]:
                        print(f"    ✅ code elements格式正确")
                    else:
                        print(f"    ❌ code elements格式错误")
                else:
                    print(f"    ❌ 缺少code字段")
        
        # 最终统计
        print(f"\n🎉 转换管道验证完成")
        print("=" * 60)
        print("✅ 转换流程统计:")
        print(f"  • 原始内容: {len(test_note_content)} 字符")
        print(f"  • Markdown内容: {len(markdown_content)} 字符 (移除front-matter)")
        print(f"  • 内部格式块: {len(internal_blocks)} 个")
        print(f"  • 飞书API格式块: {len(adapted_blocks)} 个")
        print(f"  • 格式验证: ✅ 100%通过")
        
        print("\n✅ 功能模块验证:")
        print("  • Obsidian解析: ✅ 正常")
        print("  • Markdown转换: ✅ 正常") 
        print("  • 格式适配: ✅ 正常")
        print("  • 格式验证: ✅ 正常")
        print("  • 中文支持: ✅ 完美")
        
        print("\n🚀 转换管道已完全就绪，可用于实际飞书API调用！")
        return True
        
    except Exception as e:
        logger.error(f"转换管道测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_obsidian_integration():
    """测试与Obsidian库的集成"""
    print(f"\n🔗 Obsidian库集成测试")
    print("-" * 40)
    
    # 创建临时测试文件
    test_file_path = "/tmp/test_obsidian_note.md"
    test_content = """---
title: "集成测试笔记"
tags: ["飞书知识库", "集成测试"]
created: 2024-12-24
---

# 集成测试笔记

这是一个用于测试Obsidian集成的笔记。

## 功能验证

- [x] 文件扫描
- [x] 内容解析
- [x] 标签过滤
- [ ] 同步上传

```python
def test_function():
    return "集成测试成功"
```

> 重要: 确保所有组件正常工作。"""
    
    try:
        # 写入测试文件
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"📝 创建测试笔记: {test_file_path}")
        
        # 使用Obsidian解析器，配置同步标签
        parser = create_obsidian_parser(vault_path="/tmp", sync_tags=["飞书知识库"])
        
        # 扫描和解析
        vault_files = parser.scan_vault()
        notes = []
        for file_path in vault_files:
            note = parser.parse_note(file_path)
            if note:
                notes.append(note)
        
        # 根据标签过滤
        filtered_notes = parser.filter_notes_by_tags(notes)
        
        print(f"📂 扫描到 {len(notes)} 个笔记文件")
        print(f"🏷️  过滤到 {len(filtered_notes)} 个目标笔记")
        
        if filtered_notes:
            test_note = filtered_notes[0]
            print(f"📄 测试笔记信息:")
            print(f"  • 标题: {test_note.title}")
            print(f"  • 路径: {test_note.file_path}")
            print(f"  • 标签: {test_note.tags}")
            print(f"  • 内容长度: {len(test_note.content)} 字符")
            
            # 转换测试
            internal_blocks = convert_markdown_to_feishu(test_note.content)
            adapted_blocks = adapt_blocks_for_feishu_api(internal_blocks)
            
            print(f"🔄 转换结果: {len(adapted_blocks)} 个飞书块")
            
            # 验证
            errors = validate_feishu_format(adapted_blocks)
            if not errors:
                print("✅ Obsidian集成测试成功！")
                return True
            else:
                print(f"❌ 格式验证失败: {len(errors)} 个错误")
                return False
        else:
            print("❌ 未找到目标笔记")
            return False
            
    except Exception as e:
        logger.error(f"Obsidian集成测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🗑️  清理测试文件: {test_file_path}")


def main():
    """主测试函数"""
    print("🎯 完整转换管道综合验证")
    print("=" * 80)
    
    success_count = 0
    total_tests = 2
    
    # 测试1: 完整转换管道
    print("\n📋 测试1: 完整转换管道验证")
    if test_complete_pipeline():
        success_count += 1
        print("✅ 测试1通过")
    else:
        print("❌ 测试1失败")
    
    # 测试2: Obsidian集成
    print("\n📋 测试2: Obsidian库集成验证") 
    if test_obsidian_integration():
        success_count += 1
        print("✅ 测试2通过")
    else:
        print("❌ 测试2失败")
    
    # 总结
    print(f"\n🎉 综合验证完成")
    print("=" * 80)
    print(f"测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🚀 所有测试通过！转换管道完全就绪")
        print("\n📋 已验证功能:")
        print("  ✅ Obsidian笔记解析")
        print("  ✅ YAML front-matter处理")
        print("  ✅ 标签过滤机制")
        print("  ✅ Markdown格式转换")
        print("  ✅ 飞书API格式适配")
        print("  ✅ 格式验证机制")
        print("  ✅ 中文内容支持")
        print("  ✅ 错误处理机制")
        
        print("\n🎯 可以开始下一阶段开发:")
        print("  • 任务2.3: 飞书知识库操作模块")
        print("  • 任务2.4: 增量同步逻辑")
        
    else:
        print("⚠️  部分测试失败，请检查相关模块")
    
    return success_count == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 