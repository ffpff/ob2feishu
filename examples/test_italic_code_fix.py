#!/usr/bin/env python3
"""
测试斜体和代码格式修复
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ob2feishu.config import get_config
from src.ob2feishu.feishu_client import create_feishu_client
from src.ob2feishu.feishu_docs import create_feishu_docs_client
from src.ob2feishu.markdown_converter import convert_markdown_to_feishu
from src.ob2feishu.format_adapter import adapt_blocks_for_feishu_api


def test_italic_and_code_formatting():
    """测试斜体和代码格式修复"""
    print("=" * 60)
    print("🎨 测试斜体和代码格式修复")
    print("=" * 60)
    
    try:
        # 1. 加载配置
        load_dotenv(override=True)
        config = get_config()
        
        # 2. 创建客户端
        feishu_client = create_feishu_client(
            app_id=config.feishu.app_id,
            app_secret=config.feishu.app_secret
        )
        docs_client = create_feishu_docs_client(feishu_client)
        
        # 3. 测试连接
        print("🔗 测试飞书API连接...")
        if feishu_client.test_connection():
            print("✅ 飞书API连接成功")
        else:
            print("❌ 飞书API连接失败")
            return False
        
        # 4. 准备包含各种格式的测试内容
        test_content = f"""# 🎨 格式化文本测试文档

这是一个全面测试**粗体**、*斜体*和`代码`格式的文档。

## 📝 内联格式测试

### 基础格式
- **粗体文本**: 这是粗体
- *斜体文本*: 这是斜体  
- `代码文本`: 这是内联代码

### 混合格式测试
- 这是一个包含**粗体**、*斜体*和`代码`的混合段落
- **粗体中包含*斜体***
- *斜体中包含`代码`*
- `代码中不应该有格式`

### 列表中的格式
1. **第一项**: 包含*斜体强调*的列表项
2. *第二项*: 包含`代码示例`的列表项  
3. `第三项`: 完全是代码格式的列表项
4. 混合格式: **粗体** + *斜体* + `代码`

### 段落格式测试
这是一个普通段落，包含**重要的粗体信息**，一些*强调的斜体内容*，以及一些`关键的代码片段`。

另一个段落测试：当我们需要*强调某个概念*时，或者引用`变量名`和**重要警告**时，格式应该正确显示。

## 💻 代码块测试

下面是一个代码块示例：

```python
def sync_to_feishu():
    print("🚀 开始同步到飞书知识库...")
    return "✅ 同步成功!"
```

另一个代码块：

```javascript
const message = "Hello, World!";
console.log(message);
```

## ✅ 验证项目

如果你看到：
1. **粗体文本**正确显示为粗体
2. *斜体文本*正确显示为斜体
3. `代码文本`正确显示为代码格式
4. 代码块正确显示为代码格式
5. 混合格式正确处理

那么所有格式修复就成功了！

测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 5. 转换内容
        print("🔄 转换Markdown内容...")
        internal_blocks = convert_markdown_to_feishu(test_content)
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 转换完成: {len(feishu_blocks)} 个内容块")
        
        # 6. 显示转换结果的详细预览
        print("\n📋 格式转换结果预览:")
        for i, block in enumerate(feishu_blocks[:8]):
            print(f"  Block {i+1}:")
            if 'text' in block and 'elements' in block['text']:
                elements = block['text']['elements']
                for j, elem in enumerate(elements):
                    if 'text_run' in elem:
                        content = elem['text_run']['content']
                        style = elem['text_run'].get('text_element_style', {})
                        
                        format_marks = []
                        if style.get('bold'):
                            format_marks.append('粗体')
                        if style.get('italic'):
                            format_marks.append('斜体')
                        if style.get('inline_code'):
                            format_marks.append('代码')
                        
                        format_str = f" [{'/'.join(format_marks)}]" if format_marks else ""
                        print(f"    Element {j+1}: '{content}'{format_str}")
            print()
        
        # 7. 创建测试文档
        print("📄 创建测试文档...")
        document_title = f"🎨 格式化测试 - {datetime.now().strftime('%m%d_%H%M')}"
        
        document = docs_client.create_document(title=document_title)
        print(f"✅ 文档创建成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        if document.url:
            print(f"   🔗 访问链接: {document.url}")
        
        # 8. 获取文档根块ID并添加内容
        print("\n📋 获取文档结构...")
        blocks_info = docs_client.get_document_blocks(document.document_id)
        if not blocks_info:
            print("❌ 无法获取文档块结构")
            return False
        
        root_block_id = blocks_info[0].get('block_id')
        print(f"📦 根块ID: {root_block_id}")
        
        # 9. 同步内容
        print("\n☁️  同步内容到飞书...")
        block_ids = docs_client.create_blocks(
            document.document_id, 
            feishu_blocks,
            parent_block_id=root_block_id
        )
        print(f"✅ 内容同步成功: 创建了 {len(block_ids)} 个内容块")
        
        # 10. 总结
        print("\n🎉 格式化测试完成！")
        print("=" * 60)
        print("📊 测试结果:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📦 内容块数: {len(block_ids)}")
        
        if document.url:
            print(f"\n🔗 请在飞书中查看测试结果:")
            print(f"   {document.url}")
        
        print("\n✅ 请验证以下项目:")
        print("   1. **粗体文本**是否正确显示为粗体")
        print("   2. *斜体文本*是否正确显示为斜体") 
        print("   3. `代码文本`是否正确显示为代码格式")
        print("   4. 代码块是否正确显示")
        print("   5. 混合格式是否正确处理")
        
        return True
        
    except Exception as e:
        print(f"❌ 格式化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_italic_and_code_formatting()
    if success:
        print("\n🎊 测试成功完成!")
    else:
        print("\n💥 测试失败")
        sys.exit(1) 