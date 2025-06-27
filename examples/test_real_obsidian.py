#!/usr/bin/env python3
"""
真实Obsidian库测试脚本

使用用户真实的Obsidian库测试解析器功能
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ob2feishu.obsidian_parser import create_obsidian_parser, ObsidianNote
from ob2feishu.config import get_config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_real_obsidian_vault():
    """测试真实的Obsidian库"""
    print("🧪 真实Obsidian库测试")
    print("=" * 60)
    
    # 加载配置
    try:
        config = get_config()
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    # 获取Obsidian配置
    obsidian_config = config.get('obsidian', {})
    vault_path = obsidian_config.get('vault_path')
    sync_tags = obsidian_config.get('sync_tags', [])
    exclude_folders = obsidian_config.get('exclude_folders', [])
    exclude_patterns = obsidian_config.get('exclude_patterns', [])
    
    print(f"📂 Obsidian库路径: {vault_path}")
    print(f"🏷️  同步标签: {sync_tags}")
    print(f"🚫 排除文件夹: {exclude_folders}")
    print(f"🚫 排除模式: {exclude_patterns}")
    
    # 检查路径是否存在
    if not vault_path or not Path(vault_path).exists():
        print(f"❌ Obsidian库路径不存在: {vault_path}")
        return False
    
    # 创建解析器
    try:
        parser = create_obsidian_parser(
            vault_path=vault_path,
            sync_tags=sync_tags,
            exclude_folders=exclude_folders,
            exclude_patterns=exclude_patterns
        )
        print("✅ 解析器创建成功")
    except Exception as e:
        print(f"❌ 解析器创建失败: {e}")
        return False
    
    # 1. 扫描文件
    print(f"\n📋 扫描Obsidian库...")
    try:
        scanned_files = list(parser.scan_vault())
        print(f"找到 {len(scanned_files)} 个Markdown文件")
        
        # 显示前10个文件
        for i, file_path in enumerate(scanned_files[:10]):
            try:
                relative_path = file_path.relative_to(Path(vault_path))
                print(f"  📄 {relative_path}")
            except ValueError:
                print(f"  📄 {file_path}")
        
        if len(scanned_files) > 10:
            print(f"  ... 还有 {len(scanned_files) - 10} 个文件")
            
    except Exception as e:
        print(f"❌ 文件扫描失败: {e}")
        return False
    
    # 2. 解析笔记（只解析前5个文件作为示例）
    print(f"\n📝 解析笔记内容（前5个文件）...")
    parsed_notes = []
    
    for i, file_path in enumerate(scanned_files[:5]):
        try:
            print(f"\n🔍 解析文件 {i+1}: {file_path.name}")
            note = parser.parse_note(file_path)
            
            if note:
                parsed_notes.append(note)
                print(f"  ✅ 标题: {note.title}")
                print(f"  🏷️  标签: {note.tags}")
                print(f"  📏 内容长度: {len(note.content)} 字符")
                print(f"  📊 文件大小: {note.file_size} 字节")
                print(f"  🕒 修改时间: {note.modified_time}")
                print(f"  🔗 内容哈希: {note.content_hash[:8]}...")
                print(f"  🔄 需要同步: {'是' if note.needs_sync else '否'}")
                
                # 显示内容预览（前200字符）
                content_preview = note.content.replace('\n', ' ')[:200]
                print(f"  📖 内容预览: {content_preview}...")
                
                # 检查是否有飞书同步信息
                if note.feishu_document_id:
                    print(f"  📋 飞书文档ID: {note.feishu_document_id}")
                    print(f"  🕒 上次同步: {note.feishu_last_sync}")
                    print(f"  📈 同步版本: {note.feishu_sync_version}")
                
            else:
                print(f"  ❌ 解析失败")
                
        except Exception as e:
            print(f"  ❌ 解析错误: {e}")
    
    print(f"\n✅ 成功解析 {len(parsed_notes)} 个笔记")
    
    # 3. 测试标签过滤
    if sync_tags:
        print(f"\n🏷️  测试标签过滤...")
        try:
            filtered_notes = parser.filter_notes_by_tags(parsed_notes)
            print(f"匹配同步标签 {sync_tags} 的笔记: {len(filtered_notes)} 个")
            
            for note in filtered_notes:
                matching_tags = [tag for tag in note.tags if tag in sync_tags]
                print(f"  ✅ {note.title}")
                print(f"     匹配标签: {matching_tags}")
                
        except Exception as e:
            print(f"❌ 标签过滤失败: {e}")
    else:
        print(f"\n⚠️  未配置同步标签，跳过标签过滤测试")
    
    # 4. 测试同步检测（基于配置的完整扫描）
    print(f"\n🔄 测试同步检测...")
    try:
        sync_notes = parser.get_notes_for_sync()
        print(f"需要同步的笔记: {len(sync_notes)} 个")
        
        for i, note in enumerate(sync_notes[:3]):  # 只显示前3个
            print(f"  🚀 {note.title}")
            print(f"     文件: {note.file_path.name}")
            print(f"     标签: {note.tags}")
            
        if len(sync_notes) > 3:
            print(f"  ... 还有 {len(sync_notes) - 3} 个需要同步的笔记")
            
    except Exception as e:
        print(f"❌ 同步检测失败: {e}")
        return False
    
    # 5. 文件内容分析
    print(f"\n📊 笔记内容统计分析...")
    if parsed_notes:
        # 标签统计
        all_tags = set()
        for note in parsed_notes:
            all_tags.update(note.tags)
        
        print(f"  📈 发现的所有标签 ({len(all_tags)} 个): ")
        sorted_tags = sorted(list(all_tags))
        for i in range(0, len(sorted_tags), 5):  # 每行显示5个标签
            row_tags = sorted_tags[i:i+5]
            print(f"     {', '.join(row_tags)}")
        
        # 文件大小统计
        total_size = sum(note.file_size for note in parsed_notes)
        avg_size = total_size / len(parsed_notes)
        
        print(f"  📏 文件大小统计:")
        print(f"     总大小: {total_size} 字节")
        print(f"     平均大小: {avg_size:.1f} 字节")
        print(f"     最大文件: {max(note.file_size for note in parsed_notes)} 字节")
        print(f"     最小文件: {min(note.file_size for note in parsed_notes)} 字节")
    
    print(f"\n🎉 真实Obsidian库测试完成！")
    print(f"📊 测试结果总结:")
    print(f"   - 扫描文件数: {len(scanned_files)}")
    print(f"   - 解析成功数: {len(parsed_notes)}")
    print(f"   - 需要同步数: {len(sync_notes) if 'sync_notes' in locals() else '未计算'}")
    print(f"   - 发现标签数: {len(all_tags) if 'all_tags' in locals() else '未统计'}")
    
    return True


def analyze_specific_file(file_path: str):
    """分析特定文件的详细信息"""
    print(f"\n🔍 详细分析文件: {file_path}")
    print("=" * 60)
    
    try:
        config = get_config()
        obsidian_config = config.get('obsidian', {})
        
        parser = create_obsidian_parser(
            vault_path=obsidian_config.get('vault_path'),
            sync_tags=obsidian_config.get('sync_tags', []),
            exclude_folders=obsidian_config.get('exclude_folders', []),
            exclude_patterns=obsidian_config.get('exclude_patterns', [])
        )
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"❌ 文件不存在: {file_path}")
            return
        
        note = parser.parse_note(file_path_obj)
        if not note:
            print(f"❌ 文件解析失败")
            return
        
        print(f"📋 文件基本信息:")
        print(f"   标题: {note.title}")
        print(f"   路径: {note.file_path}")
        print(f"   大小: {note.file_size} 字节")
        print(f"   创建时间: {note.created_time}")
        print(f"   修改时间: {note.modified_time}")
        print(f"   内容哈希: {note.content_hash}")
        
        print(f"\n🏷️  标签信息:")
        print(f"   标签列表: {note.tags}")
        print(f"   标签数量: {len(note.tags)}")
        
        print(f"\n📝 元数据信息:")
        if note.metadata:
            for key, value in note.metadata.items():
                print(f"   {key}: {value}")
        else:
            print("   无YAML front-matter")
        
        print(f"\n🔄 同步信息:")
        print(f"   已同步到飞书: {'是' if note.is_synced_to_feishu else '否'}")
        print(f"   需要同步: {'是' if note.needs_sync else '否'}")
        if note.feishu_document_id:
            print(f"   飞书文档ID: {note.feishu_document_id}")
            print(f"   上次同步时间: {note.feishu_last_sync}")
            print(f"   同步版本: {note.feishu_sync_version}")
        
        print(f"\n📖 内容预览:")
        lines = note.content.split('\n')
        for i, line in enumerate(lines[:10]):  # 显示前10行
            print(f"   {i+1:2d}: {line}")
        if len(lines) > 10:
            print(f"   ... 还有 {len(lines) - 10} 行")
        
        return note
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 如果提供了文件路径参数，分析特定文件
        file_path = sys.argv[1]
        analyze_specific_file(file_path)
    else:
        # 否则运行完整测试
        success = test_real_obsidian_vault()
        if success:
            print(f"\n💡 提示: 可以使用以下命令分析特定文件:")
            print(f"   python3 examples/test_real_obsidian.py '/path/to/specific/file.md'")
        
        return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 