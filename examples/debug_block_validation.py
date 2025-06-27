#!/usr/bin/env python3
"""
调试块验证和API错误
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ob2feishu.config import get_config
from ob2feishu.feishu_client import FeishuClient, FeishuConfig
from ob2feishu.feishu_docs import FeishuDocsClient
from ob2feishu.markdown_converter import convert_markdown_to_feishu
from ob2feishu.format_adapter import FeishuFormatAdapter
import json
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

def test_individual_blocks():
    """测试每个块类型，逐一验证"""
    
    print("🔍 逐个测试块类型，找出问题根源")
    print("=" * 60)
    
    # 1. 配置和连接
    config = get_config()
    feishu_config = FeishuConfig(
        app_id=config.feishu.app_id,
        app_secret=config.feishu.app_secret,
        base_url=config.feishu.api_base_url,
        timeout=config.feishu.api_timeout
    )
    
    client = FeishuClient(feishu_config)
    docs_client = FeishuDocsClient(client)
    
    # 测试连接
    if not client.test_connection():
        print("❌ 连接失败")
        return
    print("✅ 连接成功")
    
    # 2. 创建测试文档
    try:
        doc = docs_client.create_document("块验证测试文档")
        doc_id = doc.document_id
        print(f"✅ 文档创建成功: {doc_id}")
    except Exception as e:
        print(f"❌ 文档创建失败: {e}")
        return
    
    # 3. 定义测试内容
    test_content = f"""# 标题测试

这是普通段落文本。

## 二级标题

**粗体文本** 和 *斜体文本* 以及 `内联代码`。

```python
def hello():
    print("Hello World")
```

- 列表项目1
- 列表项目2

> 这是引用内容
"""
    
    # 4. 转换和适配
    print("\n🔄 转换内容...")
    raw_blocks = convert_markdown_to_feishu(test_content)
    adapter = FeishuFormatAdapter()
    adapted_blocks = adapter.adapt_blocks_for_api(raw_blocks)
    
    print(f"✓ 生成了 {len(adapted_blocks)} 个块")
    
    # 5. 逐个测试每种类型的块
    test_blocks_by_type(docs_client, doc_id, adapted_blocks)

def test_blocks_by_type(docs_client, doc_id, blocks):
    """按类型分组测试块"""
    
    # 按block_type分组
    blocks_by_type = {}
    for i, block in enumerate(blocks):
        if block is None:
            continue
        block_type = block.get("block_type")
        if block_type not in blocks_by_type:
            blocks_by_type[block_type] = []
        blocks_by_type[block_type].append((i, block))
    
    print(f"\n📊 发现 {len(blocks_by_type)} 种块类型:")
    for block_type, block_list in blocks_by_type.items():
        type_name = get_block_type_name(block_type)
        print(f"   {block_type}: {type_name} ({len(block_list)} 个)")
    
    # 逐个类型测试
    for block_type, block_list in blocks_by_type.items():
        test_single_block_type(docs_client, doc_id, block_type, block_list)

def get_block_type_name(block_type):
    """获取块类型名称"""
    type_names = {
        1: "页面",
        2: "段落",
        3: "标题1",
        4: "标题2", 
        5: "标题3",
        6: "标题4",
        7: "标题5",
        8: "标题6",
        12: "无序列表",
        13: "有序列表", 
        14: "代码块",
        15: "引用块"
    }
    return type_names.get(block_type, f"未知类型({block_type})")

def test_single_block_type(docs_client, doc_id, block_type, block_list):
    """测试单一类型的块"""
    
    type_name = get_block_type_name(block_type)
    print(f"\n🧪 测试 {type_name} (block_type: {block_type})")
    print("-" * 40)
    
    for i, (original_index, block) in enumerate(block_list):
        print(f"\n  测试 {type_name} #{i+1} (原索引 {original_index}):")
        
        # 显示块内容
        print("  JSON结构:")
        print("  " + json.dumps(block, ensure_ascii=False, indent=4).replace('\n', '\n  '))
        
        # 验证块结构
        validation_errors = validate_block_structure(block)
        if validation_errors:
            print(f"  ❌ 结构验证失败:")
            for error in validation_errors:
                print(f"     - {error}")
            continue
        else:
            print("  ✓ 结构验证通过")
        
        # 尝试创建块
        try:
            block_ids = docs_client.create_blocks(doc_id, [block], parent_block_id=doc_id)
            print(f"  ✅ 创建成功: {block_ids}")
        except Exception as e:
            print(f"  ❌ 创建失败: {e}")
            
            # 尝试获取更详细的错误信息
            try:
                import requests
                print("  🔍 尝试获取详细错误信息...")
            except:
                pass

def validate_block_structure(block):
    """验证块结构"""
    errors = []
    
    if not isinstance(block, dict):
        errors.append("块必须是字典类型")
        return errors
    
    block_type = block.get("block_type")
    if block_type is None:
        errors.append("缺少block_type字段")
        return errors
    
    # 根据块类型验证结构
    if block_type == 2:  # 文本块
        errors.extend(validate_text_block(block))
    elif block_type == 14:  # 代码块
        errors.extend(validate_code_block(block))
    elif block_type in [3, 4, 5, 6, 7, 8]:  # 标题块
        errors.extend(validate_heading_block(block))
    elif block_type == 15:  # 引用块
        errors.extend(validate_quote_block(block))
    
    return errors

def validate_text_block(block):
    """验证文本块"""
    errors = []
    
    if "text" not in block:
        errors.append("文本块缺少text字段")
        return errors
    
    text_data = block["text"]
    if not isinstance(text_data, dict):
        errors.append("text字段必须是字典")
        return errors
    
    if "elements" not in text_data:
        errors.append("text缺少elements字段")
        return errors
    
    elements = text_data["elements"]
    if not isinstance(elements, list):
        errors.append("elements必须是列表")
        return errors
    
    if len(elements) == 0:
        errors.append("elements不能为空")
        return errors
    
    for i, element in enumerate(elements):
        if not isinstance(element, dict):
            errors.append(f"element[{i}]必须是字典")
            continue
        
        if "text_run" not in element:
            errors.append(f"element[{i}]缺少text_run字段")
            continue
        
        text_run = element["text_run"]
        if not isinstance(text_run, dict):
            errors.append(f"element[{i}].text_run必须是字典")
            continue
        
        if "content" not in text_run:
            errors.append(f"element[{i}].text_run缺少content字段")
            continue
    
    return errors

def validate_code_block(block):
    """验证代码块"""
    errors = []
    
    if "code" not in block:
        errors.append("代码块缺少code字段")
        return errors
    
    code_data = block["code"]
    if not isinstance(code_data, dict):
        errors.append("code字段必须是字典")
        return errors
    
    if "language" not in code_data:
        errors.append("code缺少language字段")
    
    if "elements" not in code_data:
        errors.append("code缺少elements字段")
        return errors
    
    elements = code_data["elements"]
    if not isinstance(elements, list):
        errors.append("code.elements必须是列表")
        return errors
    
    if len(elements) == 0:
        errors.append("code.elements不能为空")
        return errors
    
    for i, element in enumerate(elements):
        if not isinstance(element, dict):
            errors.append(f"code.element[{i}]必须是字典")
            continue
        
        if "text_run" not in element:
            errors.append(f"code.element[{i}]缺少text_run字段")
            continue
        
        text_run = element["text_run"]
        if not isinstance(text_run, dict):
            errors.append(f"code.element[{i}].text_run必须是字典")
            continue
        
        if "content" not in text_run:
            errors.append(f"code.element[{i}].text_run缺少content字段")
            continue
    
    return errors

def validate_heading_block(block):
    """验证标题块"""
    errors = []
    
    block_type = block.get("block_type")
    heading_fields = {
        3: "heading1", 
        4: "heading2",
        5: "heading3",
        6: "heading4",
        7: "heading5",
        8: "heading6"
    }
    
    expected_field = heading_fields.get(block_type)
    if not expected_field:
        errors.append(f"无效的标题块类型: {block_type}")
        return errors
    
    if expected_field not in block:
        errors.append(f"标题块缺少{expected_field}字段")
        return errors
    
    # 验证内部结构类似文本块
    heading_data = block[expected_field]
    if "elements" not in heading_data:
        errors.append(f"{expected_field}缺少elements字段")
    
    return errors

def validate_quote_block(block):
    """验证引用块"""
    errors = []
    
    if "quote" not in block:
        errors.append("引用块缺少quote字段")
        return errors
    
    # 引用块的结构验证
    quote_data = block["quote"]
    if "elements" not in quote_data:
        errors.append("quote缺少elements字段")
    
    return errors

if __name__ == "__main__":
    test_individual_blocks() 