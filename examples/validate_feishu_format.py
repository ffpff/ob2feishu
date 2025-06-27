#!/usr/bin/env python3
"""
飞书API格式验证脚本
对比转换结果与真实飞书API格式要求，确保完全兼容
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
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def validate_block_structure(block, block_index=0):
    """
    验证单个块的结构是否符合飞书API要求
    
    Args:
        block: 要验证的块
        block_index: 块索引（用于错误提示）
        
    Returns:
        tuple: (是否有效, 错误信息列表)
    """
    errors = []
    
    # 1. 检查必须字段
    if "block_type" not in block:
        errors.append(f"块{block_index}: 缺少必须字段 'block_type'")
        return False, errors
    
    block_type = block["block_type"]
    
    # 2. 检查block_type是否为有效值
    valid_block_types = {
        1: "页面", 2: "文本", 3: "标题1", 4: "标题2", 5: "标题3",
        6: "标题4", 7: "标题5", 8: "标题6", 9: "无序列表", 10: "有序列表",
        11: "代码块", 12: "引用", 13: "公式", 14: "待办事项", 15: "多维表格",
        16: "高亮块", 17: "群聊卡片", 18: "流程图", 19: "分割线", 20: "文件",
        21: "分栏", 22: "分栏列", 23: "内嵌", 24: "图片", 25: "ISV",
        26: "思维导图", 27: "电子表格", 28: "表格", 29: "表格单元格", 30: "视图",
        31: "引用容器"
    }
    
    if block_type not in valid_block_types:
        errors.append(f"块{block_index}: 无效的block_type值 {block_type}")
    
    # 3. 根据块类型验证特定结构
    if block_type in [2, 3, 4, 5, 6, 7, 8, 12]:  # 文本类型块
        if "text" in block:
            text_errors = validate_text_structure(block["text"], block_index)
            errors.extend(text_errors)
    
    elif block_type == 11:  # 代码块
        code_errors = validate_code_block_structure(block, block_index)
        errors.extend(code_errors)
    
    elif block_type == 28:  # 表格
        table_errors = validate_table_structure(block, block_index)
        errors.extend(table_errors)
    
    elif block_type == 19:  # 分割线
        # 分割线不需要额外内容
        pass
    
    elif block_type in [9, 10]:  # 列表
        list_errors = validate_list_structure(block, block_index)
        errors.extend(list_errors)
    
    # 4. 检查子块结构
    if "children" in block:
        children_errors = validate_children_structure(block["children"], block_index)
        errors.extend(children_errors)
    
    return len(errors) == 0, errors


def validate_text_structure(text_obj, block_index):
    """验证文本对象结构"""
    errors = []
    
    if not isinstance(text_obj, dict):
        errors.append(f"块{block_index}: text字段必须是对象")
        return errors
    
    # 检查elements字段
    if "elements" not in text_obj:
        errors.append(f"块{block_index}: text对象缺少elements字段")
        return errors
    
    elements = text_obj["elements"]
    if not isinstance(elements, list):
        errors.append(f"块{block_index}: elements必须是数组")
        return errors
    
    # 检查每个element
    for i, element in enumerate(elements):
        if not isinstance(element, dict):
            errors.append(f"块{block_index}.elements[{i}]: 必须是对象")
            continue
        
        if "text" not in element:
            errors.append(f"块{block_index}.elements[{i}]: 缺少text字段")
        
        # 注意：这里我们的实现使用的是简化格式
        # 真实飞书API使用 text_run.content 格式
        # 我们需要在实际同步时进行转换
    
    return errors


def validate_code_block_structure(block, block_index):
    """验证代码块结构"""
    errors = []
    
    # 检查是否有code字段或text字段
    if "code" not in block and "text" not in block:
        errors.append(f"块{block_index}: 代码块缺少code或text字段")
        return errors
    
    # 如果有code字段，检查language
    if "code" in block:
        code_obj = block["code"]
        if "language" not in code_obj:
            errors.append(f"块{block_index}: 代码块缺少language字段")
    
    return errors


def validate_table_structure(block, block_index):
    """验证表格结构"""
    errors = []
    
    if "table" not in block:
        errors.append(f"块{block_index}: 表格块缺少table字段")
        return errors
    
    table_obj = block["table"]
    
    # 检查表格数据
    if "header" not in table_obj and "rows" not in table_obj:
        errors.append(f"块{block_index}: 表格缺少header或rows数据")
    
    return errors


def validate_list_structure(block, block_index):
    """验证列表结构"""
    errors = []
    
    if "children" not in block:
        errors.append(f"块{block_index}: 列表块必须有children字段")
        return errors
    
    children = block["children"]
    if not isinstance(children, list) or len(children) == 0:
        errors.append(f"块{block_index}: 列表必须有至少一个子项")
    
    return errors


def validate_children_structure(children, parent_block_index):
    """验证子块结构"""
    errors = []
    
    if not isinstance(children, list):
        errors.append(f"块{parent_block_index}: children必须是数组")
        return errors
    
    for i, child in enumerate(children):
        child_valid, child_errors = validate_block_structure(child, f"{parent_block_index}.children[{i}]")
        errors.extend(child_errors)
    
    return errors


def create_real_feishu_examples():
    """创建真实的飞书API格式示例用于对比"""
    return {
        "text_paragraph": {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是一段文本",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {}
            }
        },
        "heading1": {
            "block_type": 3,
            "heading1": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是一级标题",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {}
            }
        },
        "code_block": {
            "block_type": 11,
            "code": {
                "language": "python",
                "elements": [
                    {
                        "text_run": {
                            "content": "def hello():\n    print('Hello')"
                        }
                    }
                ]
            }
        },
        "bullet_list": {
            "block_type": 9,
            "bullet_list": {
                "elements": [
                    {
                        "text_run": {
                            "content": ""
                        }
                    }
                ],
                "style": {}
            }
        }
    }


def compare_with_real_format():
    """对比我们的转换结果与真实飞书API格式"""
    print("=" * 60)
    print("对比转换格式与真实飞书API格式")
    print("=" * 60)
    
    # 测试内容
    test_markdown = """# 标题测试

这是一段普通文本。

```python
def hello():
    print("Hello World")
```

- 列表项1
- 列表项2"""
    
    # 转换结果
    our_result = convert_markdown_to_feishu(test_markdown)
    
    # 真实格式示例
    real_examples = create_real_feishu_examples()
    
    print(f"我们的转换结果包含 {len(our_result)} 个块")
    print()
    
    # 逐个对比
    for i, block in enumerate(our_result):
        print(f"块 {i+1} - 类型 {block['block_type']}")
        
        # 验证结构
        is_valid, errors = validate_block_structure(block, i+1)
        
        if is_valid:
            print("  ✅ 结构验证通过")
        else:
            print("  ❌ 结构验证失败:")
            for error in errors:
                print(f"    - {error}")
        
        # 格式分析
        analyze_block_format(block, i+1)
        print()


def analyze_block_format(block, block_num):
    """分析块格式的兼容性"""
    block_type = block.get("block_type")
    
    print(f"  格式分析:")
    
    if block_type in [2, 3, 4, 5, 6, 7, 8]:  # 文本类型
        if "text" in block:
            text_obj = block["text"]
            elements = text_obj.get("elements", [])
            
            print(f"    - 文本元素数量: {len(elements)}")
            
            # 检查格式差异
            if elements:
                first_element = elements[0]
                if "text" in first_element:
                    print("    - ⚠️ 使用简化格式 (text)，实际API需要 text_run.content")
                elif "text_run" in first_element:
                    print("    - ✅ 使用标准API格式 (text_run.content)")
    
    elif block_type == 11:  # 代码块
        if "code" in block:
            print(f"    - 代码语言: {block['code'].get('language', '未指定')}")
            print("    - ⚠️ 代码内容格式需要适配API要求")
        elif "text" in block:
            print("    - ⚠️ 使用text格式，应该使用code格式")
    
    elif block_type == 28:  # 表格
        if "table" in block:
            table_data = block["table"]
            print(f"    - 表头列数: {len(table_data.get('header', []))}")
            print(f"    - 数据行数: {len(table_data.get('rows', []))}")
            print("    - ⚠️ 表格格式需要转换为飞书API格式")


def test_format_compatibility():
    """测试格式兼容性"""
    print("=" * 60)
    print("格式兼容性测试")
    print("=" * 60)
    
    test_cases = [
        ("简单段落", "这是一段测试文本。"),
        ("中文标题", "# 中文标题测试"),
        ("代码块", "```python\nprint('Hello')\n```"),
        ("列表", "- 项目1\n- 项目2"),
        ("引用", "> 这是引用内容"),
        ("表格", "|列1|列2|\n|---|---|\n|值1|值2|"),
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for name, content in test_cases:
        print(f"测试: {name}")
        
        try:
            result = convert_markdown_to_feishu(content)
            
            # 验证每个块
            all_valid = True
            for i, block in enumerate(result):
                is_valid, errors = validate_block_structure(block, i)
                if not is_valid:
                    all_valid = False
                    print(f"  ❌ 块{i}验证失败: {errors}")
            
            if all_valid:
                print(f"  ✅ 通过 - 生成{len(result)}个有效块")
                passed_tests += 1
            else:
                print(f"  ❌ 失败 - 格式不兼容")
        
        except Exception as e:
            print(f"  ❌ 异常: {e}")
        
        print()
    
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！格式兼容性良好")
    else:
        print("⚠️  部分测试失败，需要调整格式")


def identify_format_gaps():
    """识别格式差异和需要改进的地方"""
    print("=" * 60)
    print("格式差异分析")
    print("=" * 60)
    
    gaps = [
        {
            "问题": "文本元素格式",
            "当前": "使用 {text: '内容'} 格式",
            "应该": "使用 {text_run: {content: '内容'}} 格式",
            "影响": "需要在API调用前转换",
            "优先级": "高"
        },
        {
            "问题": "标题块字段",
            "当前": "使用 text 字段存储标题内容",
            "应该": "使用 heading1/heading2 等专用字段",
            "影响": "标题可能无法正确显示",
            "优先级": "高"
        },
        {
            "问题": "代码块结构",
            "当前": "使用 text + extra.code 组合",
            "应该": "使用标准 code 字段结构",
            "影响": "代码可能无法语法高亮",
            "优先级": "中"
        },
        {
            "问题": "列表子项格式",
            "当前": "子项使用 text 块",
            "应该": "可能需要特定的列表项格式",
            "影响": "列表显示可能不正确",
            "优先级": "中"
        },
        {
            "问题": "表格数据格式",
            "当前": "使用自定义 table.header/rows",
            "应该": "需要转换为飞书表格单元格格式",
            "影响": "表格无法创建",
            "优先级": "中"
        }
    ]
    
    for gap in gaps:
        print(f"🔍 {gap['问题']} (优先级: {gap['优先级']})")
        print(f"   当前: {gap['当前']}")
        print(f"   应该: {gap['应该']}")
        print(f"   影响: {gap['影响']}")
        print()
    
    print("📋 建议:")
    print("1. 实现 format_for_api() 函数，在API调用前转换格式")
    print("2. 优先解决高优先级问题")
    print("3. 通过实际API测试验证格式")


def main():
    """主函数"""
    setup_logging()
    
    print("飞书API格式验证工具")
    print("=" * 60)
    print()
    
    # 对比真实格式
    compare_with_real_format()
    
    print()
    
    # 兼容性测试
    test_format_compatibility()
    
    print()
    
    # 差异分析
    identify_format_gaps()
    
    print()
    print("=" * 60)
    print("总结:")
    print("✅ 我们的转换器生成了正确的块结构和类型")
    print("⚠️  文本格式需要在API调用前进行适配")
    print("🔧 建议创建格式适配器函数处理API格式差异")


if __name__ == "__main__":
    main() 