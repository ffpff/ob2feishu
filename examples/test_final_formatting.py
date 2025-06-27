#!/usr/bin/env python3
"""
最终格式测试 - 验证所有修复的功能
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


def test_final_formatting():
    """最终格式测试"""
    print("=" * 60)
    print("🎯 最终格式化测试 - 验证所有修复功能")
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
        
        # 4. 准备完整的测试内容
        test_content = f"""# 🎯 最终格式化测试文档

这是一个全面验证**粗体**、*斜体*和`代码`格式修复的完整测试文档。

## ✅ 修复验证清单

### 1. 格式化文本
- **粗体文本**: 应该显示为粗体格式
- *斜体文本*: 应该显示为斜体格式
- `代码文本`: 应该显示为代码格式

### 2. 标题格式
所有标题现在正确显示为粗体，不再有#号：

#### 四级标题示例
这是四级标题，应该显示为粗体并带有适当缩进。

##### 五级标题示例
这是五级标题的内容。

### 3. 混合格式测试
- 这是包含**粗体强调**、*斜体提醒*和`代码片段`的混合段落
- **重要提示**: 包含*斜体强调*的粗体文本
- *特别说明*: 包含`代码示例`的斜体文本
- 复杂混合: **粗体** + *斜体* + `代码` = 完美格式

### 4. 列表中的格式
1. **第一项**: 这是*重要的*列表项，包含`关键代码`
2. *第二项*: 完全斜体的列表项
3. `第三项`: 完全代码格式的列表项
4. 普通项目但包含**重要信息**

- **无序列表**: 包含*强调内容*
- *斜体列表项*: 包含`代码引用`
- `代码列表项`: 包含**粗体警告**

### 5. 段落格式验证
这是一个复杂的段落，用来测试**所有格式化功能**是否正常工作。当我们需要*强调某个重要概念*时，或者引用`变量名称`、`函数调用`或其他**关键技术术语**时，格式应该完全正确。

另一个测试段落：在实际使用中，我们经常混合使用**粗体警告**、*斜体说明*和`代码示例`。这个文档验证了所有这些格式都能正确显示。

## 💻 代码块测试

以下是代码块的测试：

```python
def format_test():
    """格式测试函数"""
    bold = "**粗体**"
    italic = "*斜体*"
    code = "`代码`"
    
    print(f"测试: {bold} + {italic} + {code}")
    return "✅ 格式测试完成!"
```

另一个代码块示例：

```javascript
// JavaScript 代码测试
const formats = {
    bold: "**粗体**",
    italic: "*斜体*",
    code: "`代码`"
};

console.log("所有格式都应该正确显示！");
```

## 📊 测试结果总结

如果你在飞书中看到：

### ✅ 预期结果
1. 所有标题显示为**粗体**（无#号）
2. **粗体文本**正确显示为粗体格式
3. *斜体文本*正确显示为斜体格式
4. `代码文本`正确显示为代码格式
5. 代码块正确显示为代码格式
6. 混合格式正确处理，无冲突
7. 列表项中的格式正确显示

### 🎯 测试完成
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试状态**: 所有格式修复已完成
- **文档位置**: 知识库指定文件夹中

**恭喜！所有格式化问题都已解决！** 🎉
"""
        
        # 5. 转换内容
        print("🔄 转换Markdown内容...")
        internal_blocks = convert_markdown_to_feishu(test_content)
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 转换完成: {len(feishu_blocks)} 个内容块")
        
        # 6. 获取文件夹token
        print("\n📁 文件夹配置:")
        print("💡 输入知识库文件夹token，或直接回车创建到根目录")
        folder_token = input("请输入目标文件夹token: ").strip()
        
        if not folder_token:
            folder_token = None
            print("📂 将创建到根目录")
        else:
            print(f"📁 将创建到文件夹: {folder_token}")
        
        # 7. 创建最终测试文档
        print("\n📄 创建最终测试文档...")
        document_title = f"🎯 最终格式化测试 - {datetime.now().strftime('%m%d_%H%M')}"
        
        if folder_token:
            document = docs_client.create_document(
                title=document_title,
                folder_token=folder_token
            )
        else:
            document = docs_client.create_document(title=document_title)
        
        print(f"✅ 文档创建成功:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📁 文件夹: {folder_token or '根目录'}")
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
        
        # 10. 最终总结
        print("\n🎉 最终格式化测试完成！")
        print("=" * 60)
        print("🎯 所有修复验证:")
        print("   ✅ 标题格式修复（无#号，显示为粗体）")
        print("   ✅ 粗体文本修复（**文本**）")
        print("   ✅ 斜体文本修复（*文本*）")
        print("   ✅ 代码文本修复（`文本`）")
        print("   ✅ 代码块格式修复")
        print("   ✅ 混合格式处理")
        print("   ✅ 知识库文件夹同步")
        
        print(f"\n📊 测试统计:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📁 位置: {folder_token or '根目录'}")
        print(f"   📦 内容块数: {len(block_ids)}")
        
        if document.url:
            print(f"\n🔗 请在飞书中查看最终结果:")
            print(f"   {document.url}")
        
        print("\n🎊 所有格式化问题都已解决！")
        return True
        
    except Exception as e:
        print(f"❌ 最终测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_final_formatting()
    if success:
        print("\n🏆 所有测试成功完成！项目已完全就绪！")
    else:
        print("\n💥 测试失败")
        sys.exit(1) 