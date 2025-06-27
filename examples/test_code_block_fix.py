#!/usr/bin/env python3
"""
测试代码块格式修复
验证代码块现在使用正确的block_type: 10和code字段
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ob2feishu.markdown_converter import convert_markdown_to_feishu
import json

def test_code_block_format():
    """测试代码块格式是否正确"""
    
    # 测试用的Markdown内容，包含不同语言的代码块
    markdown_content = '''# 代码示例测试

这是一个Python代码块：

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

这是一个JavaScript代码块：

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return true;
}
```

这是一个没有语言标识的代码块：

```
这是纯文本代码
没有语法高亮
```

这是另一段普通文本。
'''
    
    print("测试代码块格式修复...")
    print("=" * 50)
    
    # 转换Markdown
    blocks = convert_markdown_to_feishu(markdown_content)
    
    print(f"转换后共生成 {len(blocks)} 个块")
    print()
    
    # 检查每个块
    code_block_count = 0
    for i, block in enumerate(blocks):
        block_type = block.get("block_type")
        print(f"块 {i+1}: block_type = {block_type}")
        
        if block_type == 10:  # 代码块
            code_block_count += 1
            print(f"  → 代码块 #{code_block_count}")
            
            # 检查代码块结构
            if "code" in block:
                code_data = block["code"]
                language = code_data.get("language", "")
                elements = code_data.get("elements", [])
                
                print(f"    语言: '{language}'")
                print(f"    元素数量: {len(elements)}")
                
                if elements and "text_run" in elements[0]:
                    content = elements[0]["text_run"]["content"]
                    content_preview = content.replace('\n', '\\n')[:50]
                    print(f"    内容预览: {content_preview}...")
                
                # 验证结构正确性
                assert "language" in code_data, "代码块应该包含language字段"
                assert "elements" in code_data, "代码块应该包含elements字段"
                assert isinstance(elements, list), "elements应该是列表"
                assert len(elements) > 0, "应该至少有一个元素"
                assert "text_run" in elements[0], "第一个元素应该包含text_run"
                assert "content" in elements[0]["text_run"], "text_run应该包含content"
                
                print("    ✓ 代码块结构验证通过")
            else:
                print("    ✗ 错误：代码块缺少code字段")
                assert False, "代码块应该包含code字段"
        
        elif block_type == 2:  # 文本块
            print(f"  → 文本块")
            if "text" in block:
                elements = block["text"].get("elements", [])
                if elements and "text_run" in elements[0]:
                    content = elements[0]["text_run"]["content"]
                    content_preview = content.replace('\n', '\\n')[:30]
                    print(f"    内容: {content_preview}...")
        
        print()
    
    print(f"总共找到 {code_block_count} 个代码块")
    
    # 验证预期的代码块数量
    expected_code_blocks = 3  # Python, JavaScript, 和纯文本代码块
    assert code_block_count == expected_code_blocks, f"预期 {expected_code_blocks} 个代码块，实际找到 {code_block_count} 个"
    
    print("✓ 所有代码块格式验证通过！")
    
    # 打印一个完整的代码块示例
    print("\n代码块示例（JSON格式）:")
    print("=" * 50)
    for block in blocks:
        if block.get("block_type") == 10:
            print(json.dumps(block, ensure_ascii=False, indent=2))
            break

def test_inline_code_still_works():
    """测试内联代码是否仍然正常工作"""
    print("\n测试内联代码...")
    print("=" * 50)
    
    markdown_content = "这里有一个内联代码：`print('hello')`，应该仍然工作。"
    blocks = convert_markdown_to_feishu(markdown_content)
    
    assert len(blocks) == 1, "应该只有一个文本块"
    assert blocks[0]["block_type"] == 2, "应该是文本块"
    
    elements = blocks[0]["text"]["elements"]
    print(f"文本元素数量: {len(elements)}")
    
    # 应该有3个元素：普通文本 + 内联代码 + 普通文本
    assert len(elements) == 3, f"预期3个元素，实际有{len(elements)}个"
    
    # 检查内联代码元素
    code_element = elements[1]
    assert "text_run" in code_element
    assert "text_element_style" in code_element["text_run"]
    assert code_element["text_run"]["text_element_style"].get("inline_code") == True
    
    print("✓ 内联代码仍然正常工作")

if __name__ == "__main__":
    test_code_block_format()
    test_inline_code_still_works()
    print("\n🎉 所有测试通过！代码块格式修复成功！") 