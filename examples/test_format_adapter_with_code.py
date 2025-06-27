#!/usr/bin/env python3
"""
测试format_adapter处理新的代码块格式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ob2feishu.markdown_converter import convert_markdown_to_feishu
from ob2feishu.format_adapter import FeishuFormatAdapter
import json

def test_format_adapter_with_code_blocks():
    """测试format_adapter能正确处理代码块"""
    
    markdown_content = '''# 测试代码块适配

这是一个Python代码块：

```python
def hello():
    print("Hello World")
```

这是一段普通文本。

```javascript
console.log("Hello from JS");
```
'''
    
    print("测试format_adapter处理代码块...")
    print("=" * 50)
    
    # 1. 首先转换Markdown
    print("1. Markdown转换...")
    blocks = convert_markdown_to_feishu(markdown_content)
    print(f"转换后生成 {len(blocks)} 个块")
    
    # 检查原始块
    for i, block in enumerate(blocks):
        block_type = block.get("block_type")
        print(f"  块 {i+1}: block_type = {block_type}")
        if block_type == 10:
            print(f"    代码块语言: {block.get('code', {}).get('language', 'unknown')}")
    
    print()
    
    # 2. 使用format_adapter适配
    print("2. Format Adapter适配...")
    adapter = FeishuFormatAdapter()
    adapted_blocks = adapter.adapt_blocks_for_api(blocks)
    
    print(f"适配后有 {len(adapted_blocks)} 个块")
    
    # 检查适配后的块
    for i, block in enumerate(adapted_blocks):
        if block is None:
            print(f"  块 {i+1}: 适配失败 (None)")
            continue
            
        block_type = block.get("block_type")
        print(f"  块 {i+1}: block_type = {block_type}")
        
        if block_type == 10:  # 代码块
            code_data = block.get("code", {})
            language = code_data.get("language", "unknown")
            elements = code_data.get("elements", [])
            print(f"    代码块语言: {language}")
            print(f"    元素数量: {len(elements)}")
            
            if elements and "text_run" in elements[0]:
                content = elements[0]["text_run"]["content"]
                content_preview = content.replace('\n', '\\n')[:30]
                print(f"    内容预览: {content_preview}...")
    
    print()
    
    # 3. 验证格式
    print("3. 格式验证...")
    errors = adapter.validate_adapted_format(adapted_blocks)
    
    if errors:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 所有块格式验证通过")
    
    print()
    
    # 4. 检查具体的代码块格式
    print("4. 代码块格式详情:")
    print("-" * 30)
    
    code_blocks = [b for b in adapted_blocks if b and b.get("block_type") == 10]
    for i, block in enumerate(code_blocks):
        print(f"代码块 {i+1}:")
        print(json.dumps(block, ensure_ascii=False, indent=2))
        print()
    
    # 5. 确保没有丢失任何块
    original_count = len(blocks)
    adapted_count = len([b for b in adapted_blocks if b is not None])
    
    print(f"块数量检查: 原始 {original_count} -> 适配后 {adapted_count}")
    
    if original_count != adapted_count:
        print("❌ 块数量不匹配!")
        return False
    
    # 6. 确保代码块数量正确
    original_code_count = len([b for b in blocks if b.get("block_type") == 10])
    adapted_code_count = len(code_blocks)
    
    print(f"代码块数量检查: 原始 {original_code_count} -> 适配后 {adapted_code_count}")
    
    if original_code_count != adapted_code_count:
        print("❌ 代码块数量不匹配!")
        return False
    
    print("✓ 所有检查通过")
    return True

if __name__ == "__main__":
    success = test_format_adapter_with_code_blocks()
    if success:
        print("\n🎉 format_adapter代码块处理测试通过!")
    else:
        print("\n❌ 测试失败")
        exit(1) 