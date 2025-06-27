#!/usr/bin/env python3
"""
快速测试混合格式解析
"""

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ob2feishu.markdown_converter import _parse_inline_formatting

def test_mixed_formatting():
    """测试混合格式解析"""
    test_cases = [
        "这是一个全面测试**粗体**、*斜体*和`代码`格式的文档。",
        "包含**粗体**和*斜体*的混合文本",
        "*斜体*文本和**粗体**文本",
        "单独的*斜体*测试",
        "单独的**粗体**测试", 
        "单独的`代码`测试",
        "**粗体中包含*斜体***",
        "*斜体中包含`代码`*"
    ]
    
    print("🧪 混合格式解析测试")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {text}")
        elements = _parse_inline_formatting(text)
        
        for j, elem in enumerate(elements):
            style = elem.style or {}
            format_marks = []
            if style.get('bold'):
                format_marks.append('粗体')
            if style.get('italic'):
                format_marks.append('斜体')
            if style.get('inline_code'):
                format_marks.append('代码')
            
            format_str = f" [{'/'.join(format_marks)}]" if format_marks else ""
            print(f"  Element {j+1}: '{elem.text}'{format_str}")

if __name__ == "__main__":
    test_mixed_formatting() 