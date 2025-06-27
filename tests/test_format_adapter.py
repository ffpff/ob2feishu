"""
飞书API格式适配器模块的测试
"""

import unittest
import json
from src.ob2feishu.format_adapter import (
    FeishuFormatAdapter,
    adapt_blocks_for_feishu_api,
    validate_feishu_format
)


class TestFeishuFormatAdapter(unittest.TestCase):
    """测试飞书格式适配器"""
    
    def setUp(self):
        """设置测试环境"""
        self.adapter = FeishuFormatAdapter()
    
    def test_heading_block_adaptation(self):
        """测试标题块适配"""
        # 内部格式
        internal_block = {
            "block_type": 3,
            "text": {
                "elements": [
                    {"text": "这是一级标题"}
                ],
                "style": {}
            }
        }
        
        # 适配后
        adapted = self.adapter._adapt_heading_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 3)
        self.assertIn("heading1", adapted)
        self.assertNotIn("text", adapted)
        
        # 验证内容
        heading_data = adapted["heading1"]
        self.assertIn("elements", heading_data)
        elements = heading_data["elements"]
        self.assertEqual(len(elements), 1)
        
        # 验证text_run格式
        element = elements[0]
        self.assertIn("text_run", element)
        self.assertEqual(element["text_run"]["content"], "这是一级标题")
    
    def test_text_block_adaptation(self):
        """测试文本块适配"""
        internal_block = {
            "block_type": 2,
            "text": {
                "elements": [
                    {"text": "这是一段文本"}
                ],
                "style": {}
            }
        }
        
        adapted = self.adapter._adapt_text_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 2)
        self.assertIn("text", adapted)
        
        # 验证text_run格式
        elements = adapted["text"]["elements"]
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertIn("text_run", element)
        self.assertEqual(element["text_run"]["content"], "这是一段文本")
        self.assertIn("text_element_style", element["text_run"])
    
    def test_code_block_adaptation(self):
        """测试代码块适配"""
        internal_block = {
            "block_type": 11,
            "text": {
                "elements": [
                    {"text": "print('Hello World')"}
                ],
                "style": {}
            },
            "code": {
                "language": "python"
            }
        }
        
        adapted = self.adapter._adapt_code_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 11)
        self.assertIn("code", adapted)
        self.assertNotIn("text", adapted)
        
        # 验证code字段
        code_data = adapted["code"]
        self.assertEqual(code_data["language"], "python")
        self.assertIn("elements", code_data)
        
        # 验证内容
        elements = code_data["elements"]
        self.assertEqual(len(elements), 1)
        element = elements[0]
        self.assertIn("text_run", element)
        self.assertEqual(element["text_run"]["content"], "print('Hello World')")
    
    def test_list_block_adaptation(self):
        """测试列表块适配"""
        internal_block = {
            "block_type": 9,  # 无序列表
            "children": [
                {
                    "block_type": 2,
                    "text": {
                        "elements": [{"text": "列表项1"}],
                        "style": {}
                    }
                },
                {
                    "block_type": 2,
                    "text": {
                        "elements": [{"text": "列表项2"}],
                        "style": {}
                    }
                }
            ]
        }
        
        adapted = self.adapter._adapt_list_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 9)
        self.assertIn("bullet_list", adapted)
        self.assertIn("children", adapted)
        
        # 验证子项
        children = adapted["children"]
        self.assertEqual(len(children), 2)
        
        # 验证子项格式
        for child in children:
            self.assertEqual(child["block_type"], 2)
            elements = child["text"]["elements"]
            self.assertIn("text_run", elements[0])
    
    def test_quote_block_adaptation(self):
        """测试引用块适配"""
        internal_block = {
            "block_type": 12,
            "text": {
                "elements": [
                    {"text": "这是引用内容"}
                ],
                "style": {}
            }
        }
        
        adapted = self.adapter._adapt_quote_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 12)
        self.assertIn("text", adapted)
        
        # 验证text_run格式
        elements = adapted["text"]["elements"]
        element = elements[0]
        self.assertIn("text_run", element)
        self.assertEqual(element["text_run"]["content"], "这是引用内容")
    
    def test_divider_block_adaptation(self):
        """测试分割线块适配"""
        internal_block = {
            "block_type": 19
        }
        
        adapted = self.adapter._adapt_divider_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 19)
        # 分割线只需要block_type
        self.assertEqual(len(adapted), 1)
    
    def test_table_block_adaptation(self):
        """测试表格块适配"""
        internal_block = {
            "block_type": 28,
            "table": {
                "header": ["列1", "列2", "列3"],
                "rows": [
                    ["值1", "值2", "值3"],
                    ["值4", "值5", "值6"]
                ]
            }
        }
        
        adapted = self.adapter._adapt_table_block(internal_block.copy())
        
        # 验证结构
        self.assertEqual(adapted["block_type"], 28)
        self.assertIn("table", adapted)
        
        # 验证表格信息
        table_data = adapted["table"]
        self.assertEqual(table_data["rowSize"], 3)  # 2行数据 + 1行标题
        self.assertEqual(table_data["columnSize"], 3)
        
        # 验证原始数据保存
        self.assertIn("_original_table_data", adapted)
        original = adapted["_original_table_data"]
        self.assertEqual(original["header"], ["列1", "列2", "列3"])
        self.assertEqual(len(original["rows"]), 2)
    
    def test_multiple_heading_levels(self):
        """测试多级标题适配"""
        heading_types = [3, 4, 5, 6, 7, 8]
        expected_fields = ["heading1", "heading2", "heading3", "heading4", "heading5", "heading6"]
        
        for i, (block_type, expected_field) in enumerate(zip(heading_types, expected_fields)):
            with self.subTest(heading_level=i+1):
                internal_block = {
                    "block_type": block_type,
                    "text": {
                        "elements": [{"text": f"标题{i+1}"}],
                        "style": {}
                    }
                }
                
                adapted = self.adapter._adapt_heading_block(internal_block.copy())
                
                self.assertEqual(adapted["block_type"], block_type)
                self.assertIn(expected_field, adapted)
                self.assertNotIn("text", adapted)
    
    def test_elements_conversion(self):
        """测试elements格式转换"""
        internal_elements = [
            {"text": "普通文本"},
            {"text": "带样式文本", "style": {"bold": True, "italic": True}}
        ]
        
        converted = self.adapter._convert_elements_to_text_run(internal_elements)
        
        self.assertEqual(len(converted), 2)
        
        # 第一个元素
        element1 = converted[0]
        self.assertIn("text_run", element1)
        self.assertEqual(element1["text_run"]["content"], "普通文本")
        self.assertEqual(element1["text_run"]["text_element_style"], {})
        
        # 第二个元素
        element2 = converted[1]
        self.assertIn("text_run", element2)
        self.assertEqual(element2["text_run"]["content"], "带样式文本")
        self.assertEqual(element2["text_run"]["text_element_style"], {"bold": True, "italic": True})
    
    def test_full_blocks_adaptation(self):
        """测试完整的块列表适配"""
        internal_blocks = [
            {
                "block_type": 3,
                "text": {
                    "elements": [{"text": "标题"}],
                    "style": {}
                }
            },
            {
                "block_type": 2,
                "text": {
                    "elements": [{"text": "段落文本"}],
                    "style": {}
                }
            },
            {
                "block_type": 11,
                "text": {
                    "elements": [{"text": "print('code')"}],
                    "style": {}
                },
                "code": {"language": "python"}
            }
        ]
        
        adapted = self.adapter.adapt_blocks_for_api(internal_blocks)
        
        self.assertEqual(len(adapted), 3)
        
        # 验证标题块
        heading_block = adapted[0]
        self.assertEqual(heading_block["block_type"], 3)
        self.assertIn("heading1", heading_block)
        self.assertNotIn("text", heading_block)
        
        # 验证文本块
        text_block = adapted[1]
        self.assertEqual(text_block["block_type"], 2)
        self.assertIn("text", text_block)
        elements = text_block["text"]["elements"][0]
        self.assertIn("text_run", elements)
        
        # 验证代码块
        code_block = adapted[2]
        self.assertEqual(code_block["block_type"], 11)
        self.assertIn("code", code_block)
        self.assertNotIn("text", code_block)


class TestValidation(unittest.TestCase):
    """测试格式验证功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.adapter = FeishuFormatAdapter()
    
    def test_valid_adapted_format(self):
        """测试有效的适配格式验证"""
        valid_blocks = [
            {
                "block_type": 3,
                "heading1": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "标题",
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
                                "content": "文本",
                                "text_element_style": {}
                            }
                        }
                    ],
                    "style": {}
                }
            }
        ]
        
        errors = self.adapter.validate_adapted_format(valid_blocks)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_adapted_format(self):
        """测试无效的适配格式验证"""
        # 标题块使用了text字段而非heading1字段
        invalid_blocks = [
            {
                "block_type": 3,
                "text": {
                    "elements": [{"text": "标题"}],
                    "style": {}
                }
            }
        ]
        
        errors = self.adapter.validate_adapted_format(invalid_blocks)
        self.assertGreater(len(errors), 0)
        self.assertIn("标题块缺少heading1字段", errors[0])
    
    def test_text_elements_validation(self):
        """测试text元素格式验证"""
        # 使用了错误的text格式而非text_run格式
        invalid_block = {
            "block_type": 2,
            "text": {
                "elements": [
                    {"text": "内容"}  # 应该是text_run格式
                ],
                "style": {}
            }
        }
        
        errors = self.adapter._validate_text_elements(invalid_block["text"], 0)
        self.assertGreater(len(errors), 0)
        self.assertIn("缺少text_run字段", errors[0])


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_adapt_blocks_for_feishu_api(self):
        """测试便捷适配函数"""
        internal_blocks = [
            {
                "block_type": 2,
                "text": {
                    "elements": [{"text": "测试文本"}],
                    "style": {}
                }
            }
        ]
        
        adapted = adapt_blocks_for_feishu_api(internal_blocks)
        
        self.assertEqual(len(adapted), 1)
        block = adapted[0]
        self.assertEqual(block["block_type"], 2)
        elements = block["text"]["elements"]
        self.assertIn("text_run", elements[0])
    
    def test_validate_feishu_format(self):
        """测试便捷验证函数"""
        valid_blocks = [
            {
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "文本",
                                "text_element_style": {}
                            }
                        }
                    ],
                    "style": {}
                }
            }
        ]
        
        errors = validate_feishu_format(valid_blocks)
        self.assertEqual(len(errors), 0)


class TestIntegrationWithMarkdownConverter(unittest.TestCase):
    """测试与Markdown转换器的集成"""
    
    def test_full_conversion_pipeline(self):
        """测试完整的转换管道"""
        from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
        
        # Markdown内容
        markdown_content = """# 测试标题

这是一段测试文本。

```python
print("Hello World")
```

- 列表项1
- 列表项2

> 这是引用内容

---

结束段落。"""
        
        # 第一步：Markdown转换
        internal_blocks = convert_markdown_to_feishu(markdown_content)
        self.assertGreater(len(internal_blocks), 0)
        
        # 第二步：格式适配
        adapted_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        self.assertEqual(len(adapted_blocks), len(internal_blocks))
        
        # 第三步：格式验证
        errors = validate_feishu_format(adapted_blocks)
        self.assertEqual(len(errors), 0, f"格式验证失败: {errors}")
        
        # 验证具体适配结果
        # 第一个应该是标题块
        heading_block = adapted_blocks[0]
        self.assertEqual(heading_block["block_type"], 3)
        self.assertIn("heading1", heading_block)
        self.assertNotIn("text", heading_block)
        
        # 验证文本块
        text_blocks = [b for b in adapted_blocks if b["block_type"] == 2]
        for text_block in text_blocks:
            elements = text_block["text"]["elements"]
            for element in elements:
                self.assertIn("text_run", element)
                self.assertIn("content", element["text_run"])
        
        # 验证代码块
        code_blocks = [b for b in adapted_blocks if b["block_type"] == 11]
        for code_block in code_blocks:
            self.assertIn("code", code_block)
            self.assertNotIn("text", code_block)
            self.assertIn("language", code_block["code"])


if __name__ == '__main__':
    unittest.main() 