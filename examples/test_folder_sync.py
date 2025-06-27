#!/usr/bin/env python3
"""
测试同步到指定知识库文件夹
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


def test_knowledge_base_sync():
    """测试同步到知识库文件夹"""
    print("=" * 60)
    print("📁 测试同步到飞书知识库文件夹")
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
        
        # 4. 准备测试内容
        test_content = f"""# 🏢 知识库同步测试文档

这是一个测试文档，验证Obsidian到飞书知识库的同步功能。

## 📅 测试信息
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试目标**: 验证文档是否正确创建在指定的知识库文件夹中
- **权限测试**: 验证文档的编辑权限设置是否正确

## 🔧 技术详情

### Markdown元素测试
1. **标题**: 测试不同级别的标题显示
2. **列表**: 
   - 有序列表项目1
   - 有序列表项目2
3. **格式化**: 
   - *斜体文本*
   - **粗体文本** 
   - `代码文本`

### 代码块测试
```python
def sync_to_feishu():
    print("🚀 开始同步到飞书知识库...")
    return "✅ 同步成功!"
```

## ✅ 验证项目
如果你能看到这个文档并且可以编辑，说明同步功能正常工作！
"""
        
        # 5. 转换内容
        print("🔄 转换Markdown内容...")
        internal_blocks = convert_markdown_to_feishu(test_content)
        feishu_blocks = adapt_blocks_for_feishu_api(internal_blocks)
        print(f"✓ 转换完成: {len(feishu_blocks)} 个内容块")
        
        # 获取用户输入的文件夹token
        print("\n📁 文件夹配置:")
        print("💡 要将文档创建到特定知识库文件夹，请提供文件夹token")
        print("💡 如果直接回车，将创建到根目录")
        print("💡 文件夹token可以从飞书知识库URL中获取")
        
        folder_token = input("请输入目标文件夹token (或直接回车): ").strip()
        
        if not folder_token:
            folder_token = None
            print("📂 将创建到根目录")
        else:
            print(f"📁 将创建到文件夹: {folder_token}")
        
        # 6. 创建文档
        print("\n📄 创建飞书文档...")
        document_title = f"🏢 知识库同步测试 - {datetime.now().strftime('%m%d_%H%M')}"
        
        # 使用文件夹token创建文档
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
        
        # 7. 获取文档根块ID并添加内容
        print("\n📋 获取文档结构...")
        blocks_info = docs_client.get_document_blocks(document.document_id)
        if not blocks_info:
            print("❌ 无法获取文档块结构")
            return False
        
        root_block_id = blocks_info[0].get('block_id')
        print(f"📦 根块ID: {root_block_id}")
        
        # 8. 同步内容
        print("\n☁️  同步内容到飞书...")
        block_ids = docs_client.create_blocks(
            document.document_id, 
            feishu_blocks,
            parent_block_id=root_block_id
        )
        print(f"✅ 内容同步成功: 创建了 {len(block_ids)} 个内容块")
        
        # 9. 验证结果
        print("\n🎉 知识库同步测试完成！")
        print("=" * 60)
        print("📊 测试结果:")
        print(f"   📄 文档ID: {document.document_id}")
        print(f"   📝 标题: {document.title}")
        print(f"   📁 目标位置: {folder_token or '根目录'}")
        print(f"   📦 内容块数: {len(block_ids)}")
        
        if document.url:
            print(f"\n🔗 请在飞书中查看同步结果:")
            print(f"   {document.url}")
        
        print("\n✅ 请验证以下项目:")
        print("   1. 文档是否出现在正确的知识库文件夹中")
        print("   2. 你是否有文档的编辑权限")
        print("   3. 标题和内容格式是否正确显示")
        
        return True
        
    except Exception as e:
        print(f"❌ 知识库同步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_knowledge_base_sync()
    if success:
        print("\n🎊 测试成功完成!")
    else:
        print("\n💥 测试失败")
        sys.exit(1) 