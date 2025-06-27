"""
Markdown转换器模块的测试
"""

import unittest
import json
from src.ob2feishu.markdown_converter import (
    MarkdownConverter,
    FeishuBlock,
    FeishuTextElement,
    FeishuBlockType,
    convert_markdown_to_feishu
)


class TestFeishuTextElement(unittest.TestCase):
    """测试飞书文本元素"""
    
    def test_basic_text_element(self):
        """测试基本文本元素"""
        element = FeishuTextElement(text="Hello World")
        result = element.to_dict()
        
        self.assertEqual(result["text"], "Hello World")
        self.assertNotIn("style", result)
    
    def test_text_element_with_style(self):
        """测试带样式的文本元素"""
        element = FeishuTextElement(
            text="Bold Text",
            style={"bold": True}
        )
        result = element.to_dict()
        
        self.assertEqual(result["text"], "Bold Text")
        self.assertEqual(result["style"]["bold"], True)


class TestFeishuBlock(unittest.TestCase):
    """测试飞书文档块"""
    
    def test_basic_block(self):
        """测试基本块"""
        block = FeishuBlock(block_type=FeishuBlockType.TEXT)
        result = block.to_dict()
        
        self.assertEqual(result["block_type"], 2)  # TEXT = 2
        self.assertNotIn("text", result)
        self.assertNotIn("children", result)
    
    def test_block_with_text(self):
        """测试带文本的块"""
        element = FeishuTextElement(text="Test text")
        block = FeishuBlock(
            block_type=FeishuBlockType.TEXT,
            text_elements=[element]
        )
        result = block.to_dict()
        
        self.assertEqual(result["block_type"], 2)
        self.assertIn("text", result)
        self.assertEqual(len(result["text"]["elements"]), 1)
        self.assertEqual(result["text"]["elements"][0]["text"], "Test text")
    
    def test_block_with_children(self):
        """测试带子块的块"""
        child_block = FeishuBlock(block_type=FeishuBlockType.TEXT)
        parent_block = FeishuBlock(
            block_type=FeishuBlockType.BULLET_LIST,
            children=[child_block]
        )
        result = parent_block.to_dict()
        
        self.assertEqual(result["block_type"], 9)  # BULLET_LIST = 9
        self.assertIn("children", result)
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["block_type"], 2)


class TestMarkdownConverter(unittest.TestCase):
    """测试Markdown转换器"""
    
    def setUp(self):
        """设置测试环境"""
        self.converter = MarkdownConverter()
    
    def test_empty_content(self):
        """测试空内容"""
        result = self.converter.convert("")
        self.assertEqual(result, [])
    
    def test_simple_paragraph(self):
        """测试简单段落"""
        content = "这是一段普通文本。"
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 2)  # TEXT
        self.assertEqual(result[0]["text"]["elements"][0]["text"], content)
    
    def test_multiple_paragraphs(self):
        """测试多个段落"""
        content = """第一段文本。

第二段文本。"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "第一段文本。")
        self.assertEqual(result[1]["text"]["elements"][0]["text"], "第二段文本。")
    
    def test_headings(self):
        """测试标题"""
        content = """# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 6)
        
        # 检查各级标题
        expected_types = [3, 4, 5, 6, 7, 8]  # HEADING1-6
        expected_texts = ["一级标题", "二级标题", "三级标题", "四级标题", "五级标题", "六级标题"]
        
        for i, (block_type, text) in enumerate(zip(expected_types, expected_texts)):
            self.assertEqual(result[i]["block_type"], block_type)
            self.assertEqual(result[i]["text"]["elements"][0]["text"], text)
    
    def test_code_block(self):
        """测试代码块"""
        content = """```python
def hello():
    print("Hello World")
```"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 11)  # CODE_BLOCK
        
        code_content = result[0]["text"]["elements"][0]["text"]
        self.assertIn("def hello():", code_content)
        self.assertIn('print("Hello World")', code_content)
    
    def test_code_block_with_language(self):
        """测试带语言标识的代码块"""
        content = """```javascript
console.log("Hello World");
```"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 11)
        self.assertEqual(result[0]["code"]["language"], "javascript")
    
    def test_bullet_list(self):
        """测试无序列表"""
        content = """- 第一项
- 第二项
- 第三项"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 9)  # BULLET_LIST
        self.assertEqual(len(result[0]["children"]), 3)
        
        # 检查列表项
        items = result[0]["children"]
        self.assertEqual(items[0]["text"]["elements"][0]["text"], "第一项")
        self.assertEqual(items[1]["text"]["elements"][0]["text"], "第二项")
        self.assertEqual(items[2]["text"]["elements"][0]["text"], "第三项")
    
    def test_ordered_list(self):
        """测试有序列表"""
        content = """1. 第一项
2. 第二项
3. 第三项"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 10)  # ORDERED_LIST
        self.assertEqual(len(result[0]["children"]), 3)
    
    def test_quote(self):
        """测试引用"""
        content = "> 这是一个引用文本。"
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 12)  # QUOTE
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "这是一个引用文本。")
    
    def test_divider(self):
        """测试分割线"""
        test_cases = ["---", "***", "___"]
        
        for divider in test_cases:
            with self.subTest(divider=divider):
                result = self.converter.convert(divider)
                
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["block_type"], 19)  # DIVIDER
    
    def test_table(self):
        """测试表格"""
        content = """|列1|列2|列3|
|---|---|---|
|值1|值2|值3|
|值4|值5|值6|"""
        result = self.converter.convert(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 28)  # TABLE
        
        table_data = result[0]["table"]
        self.assertEqual(table_data["header"], ["列1", "列2", "列3"])
        self.assertEqual(len(table_data["rows"]), 2)
        self.assertEqual(table_data["rows"][0], ["值1", "值2", "值3"])
        self.assertEqual(table_data["rows"][1], ["值4", "值5", "值6"])
    
    def test_mixed_content(self):
        """测试混合内容"""
        content = """# 标题

这是一段普通文本。

## 子标题

- 列表项1
- 列表项2

> 这是引用

```python
print("代码")
```

---

结束段落。"""
        result = self.converter.convert(content)
        
        # 应该有多个块
        self.assertGreater(len(result), 5)
        
        # 检查第一个块是标题
        self.assertEqual(result[0]["block_type"], 3)  # HEADING1
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "标题")
    
    def test_empty_lines_handling(self):
        """测试空行处理"""
        content = """段落1


段落2"""
        result = self.converter.convert(content)
        
        # 空行应该被忽略，只有两个段落
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "段落1")
        self.assertEqual(result[1]["text"]["elements"][0]["text"], "段落2")
    
    def test_frontmatter_removal(self):
        """测试YAML front-matter移除"""
        content = """---
tags: ["test", "markdown"]
title: "Test Document"
---

# 实际标题

这是正文内容。"""
        result = self.converter.convert(content)
        
        # 应该只有标题和段落，没有front-matter内容
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["block_type"], 3)  # HEADING1
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "实际标题")
        self.assertEqual(result[1]["text"]["elements"][0]["text"], "这是正文内容。")


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_convert_markdown_to_feishu(self):
        """测试便捷转换函数"""
        content = "# 测试标题"
        result = convert_markdown_to_feishu(content)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["block_type"], 3)  # HEADING1
        self.assertEqual(result[0]["text"]["elements"][0]["text"], "测试标题")


class TestRealWorldExamples(unittest.TestCase):
    """测试真实世界的例子"""
    
    def test_obsidian_note_example(self):
        """测试典型的Obsidian笔记"""
        content = """---
tags: ["飞书知识库", "测试"]
---

# AI编程助手使用指南

## 简介

AI编程助手是一个强大的工具，可以帮助开发者提高编程效率。

## 主要功能

- 代码生成
- 错误诊断
- 性能优化

### 代码示例

```python
def greet(name):
    return f"Hello, {name}!"
```

> 注意：使用时请确保网络连接稳定。

---

## 总结

AI编程助手值得每个开发者尝试。"""
        
        result = convert_markdown_to_feishu(content)
        
        # 检查基本结构
        self.assertGreater(len(result), 5)
        
        # 查找主标题
        title_found = False
        for block in result:
            if (block.get("block_type") == 3 and 
                block.get("text", {}).get("elements", [{}])[0].get("text") == "AI编程助手使用指南"):
                title_found = True
                break
        
        self.assertTrue(title_found, "应该找到主标题")


if __name__ == '__main__':
    unittest.main() 