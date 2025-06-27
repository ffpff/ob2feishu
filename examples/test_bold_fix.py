#!/usr/bin/env python3
"""
测试粗体文本修复
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


def test_bold_formatting():
    """测试粗体文本格式修复"""
    print("=" * 60)
    print("🔧 测试粗体文本格式修复")
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
        
        # 4. 准备包含粗体的测试内容
        test_content = f"""# 🔧 粗体格式测试文档

这是一个专门测试**粗体文本**显示的文档。

## 📝 各种粗体测试

### 段落中的粗体
- 这是一个包含**粗体文本**的段落
- 另一个列表项包含**多个** **粗体** **片段**
- 混合格式：这里有**粗体**和普通文本

### 标题测试
所有标题应该显示为粗体，不带#号：

#### 四级标题测试
这是四级标题下的内容，包含**粗体强调**。

### 列表中的粗体
1. **第一项**: 这是粗体的列表项
2. **第二项**: 另一个粗体项目
3. 普通项目，但包含**粗体内容**

### 复杂格式测试
- **重要提示**: 这是一个重要的**粗体**信息
- 正常文本中嵌入**粗体片段**和更多普通文本
- **完全粗体的列表项**

## ✅ 验证项目
如果你看到：
1. 标题没有#号但显示为粗体
2. **粗体文本**正确显示为粗体格式
3. 列表项中的粗体也正确显示

那么格式修复就成功了！

测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 5. 转换内容
        print("🔄 转换Markdown内容...")
        internal_blocks = convert_markdown_to_feishu(test_content)
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 转换完成: {len(feishu_blocks)} 个内容块")
        
        # 6. 显示转换结果的前几个块
        print("\n📋 转换结果预览:")
        for i, block in enumerate(feishu_blocks[:5]):
            print(f"  Block {i+1}:")
            if 'text' in block and 'elements' in block['text']:
                elements = block['text']['elements']
                for j, elem in enumerate(elements):
                    if 'text_run' in elem:
                        content = elem['text_run']['content']
                        style = elem['text_run'].get('text_element_style', {})
                        bold_mark = " [粗体]" if style.get('bold') else ""
                        print(f"    Element {j+1}: '{content}'{bold_mark}")
            print()
        
        # 7. 创建测试文档
        print("📄 创建测试文档...")
        document_title = f"🔧 粗体格式测试 - {datetime.now().strftime('%m%d_%H%M')}"
        
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
        print("\n🎉 粗体格式测试完成！")
        print("=" * 60)
        print("📊 测试结果:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📦 内容块数: {len(block_ids)}")
        
        if document.url:
            print(f"\n🔗 请在飞书中查看测试结果:")
            print(f"   {document.url}")
        
        print("\n✅ 请验证以下项目:")
        print("   1. 标题是否显示为粗体（无#号）")
        print("   2. **粗体文本**是否正确显示为粗体")
        print("   3. 列表项中的粗体是否正确显示")
        print("   4. 混合格式是否正确处理")
        
        return True
        
    except Exception as e:
        print(f"❌ 粗体格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_bold_formatting()
    if success:
        print("\n🎊 测试成功完成!")
    else:
        print("\n💥 测试失败")
        sys.exit(1) 