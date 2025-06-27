#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感文件检查脚本
用于推送到GitHub前检查是否有敏感信息泄露
"""

import os
import re
import glob
from pathlib import Path


def check_sensitive_patterns():
    """检查可能包含敏感信息的模式"""
    
    sensitive_patterns = [
        # API密钥模式
        (r'cli_[a-zA-Z0-9]{16}', 'Feishu App ID'),
        (r'[a-zA-Z0-9]{32}', 'Potential API Secret'),
        (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
        (r'xoxb-[a-zA-Z0-9\-]+', 'Slack Bot Token'),
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
        
        # 敏感关键词
        (r'password\s*[:=]\s*["\']?[^"\'\s]+', 'Password'),
        (r'secret\s*[:=]\s*["\']?[^"\'\s]+', 'Secret'),
        (r'token\s*[:=]\s*["\']?[^"\'\s]+', 'Token'),
        (r'api_key\s*[:=]\s*["\']?[^"\'\s]+', 'API Key'),
        
        # 数据库连接
        (r'mysql://[^"\s]+', 'MySQL Connection String'),
        (r'postgresql://[^"\s]+', 'PostgreSQL Connection String'),
        (r'mongodb://[^"\s]+', 'MongoDB Connection String'),
    ]
    
    # 检查的文件类型
    file_patterns = [
        '**/*.py',
        '**/*.yaml', 
        '**/*.yml',
        '**/*.json',
        '**/*.env*',
        '**/env',
        '**/*.conf',
        '**/*.config',
        '**/*.txt',
        '**/*.md'
    ]
    
    # 排除的目录
    exclude_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules', 
        '.venv', 'venv', 'env', '.env', 'dist', 'build'
    }
    
    found_issues = []
    
    print("🔍 检查敏感信息...")
    print("=" * 50)
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            path = Path(file_path)
            
            # 跳过排除的目录
            if any(exclude_dir in path.parts for exclude_dir in exclude_dirs):
                continue
                
            # 跳过二进制文件
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue
            
            # 检查每个敏感模式
            for regex_pattern, description in sensitive_patterns:
                matches = re.finditer(regex_pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    found_issues.append({
                        'file': str(path),
                        'line': line_num,
                        'pattern': description,
                        'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                    })
    
    return found_issues


def check_gitignore_coverage():
    """检查.gitignore是否正确覆盖了敏感文件"""
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        return ["❌ 没有找到.gitignore文件"]
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        gitignore_content = f.read()
    
    issues = []
    
    # 检查关键的忽略模式
    required_patterns = [
        '.env',
        '*.key',
        'config/config.yaml',
        'secrets/',
        'credentials/',
        '__pycache__/',
        '*.log'
    ]
    
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            issues.append(f"❌ .gitignore缺少模式: {pattern}")
    
    return issues


def check_existing_sensitive_files():
    """检查当前目录中存在的敏感文件"""
    
    sensitive_files = [
        'env',          # 实际环境配置文件
        '.env',         # 常见环境文件
        'config/config.yaml',  # 实际配置文件
        'secrets.json',
        'credentials.json',
        '*.key',
        '*.pem',
        '*.p12'
    ]
    
    found_files = []
    
    for pattern in sensitive_files:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if os.path.exists(match):
                found_files.append(match)
    
    return found_files


def main():
    """主检查函数"""
    print("🔐 敏感信息安全检查")
    print("=" * 60)
    
    # 1. 检查敏感模式
    print("\n1️⃣ 检查文件中的敏感信息模式...")
    sensitive_issues = check_sensitive_patterns()
    
    if sensitive_issues:
        print(f"⚠️  发现 {len(sensitive_issues)} 个潜在敏感信息:")
        for issue in sensitive_issues:
            print(f"  📄 {issue['file']}:{issue['line']}")
            print(f"     类型: {issue['pattern']}")
            print(f"     内容: {issue['match']}")
            print()
    else:
        print("✅ 未发现敏感信息模式")
    
    # 2. 检查.gitignore覆盖
    print("\n2️⃣ 检查.gitignore配置...")
    gitignore_issues = check_gitignore_coverage()
    
    if gitignore_issues:
        print("⚠️  .gitignore配置问题:")
        for issue in gitignore_issues:
            print(f"  {issue}")
    else:
        print("✅ .gitignore配置完整")
    
    # 3. 检查存在的敏感文件
    print("\n3️⃣ 检查存在的敏感文件...")
    sensitive_files = check_existing_sensitive_files()
    
    if sensitive_files:
        print("⚠️  发现以下敏感文件:")
        for file_path in sensitive_files:
            print(f"  📁 {file_path}")
        print("\n💡 建议:")
        print("  1. 确认这些文件包含在.gitignore中")
        print("  2. 如果已经被Git跟踪，使用: git rm --cached <file>")
        print("  3. 重命名或移动包含真实密钥的文件")
    else:
        print("✅ 未发现明显的敏感文件")
    
    # 4. 总结建议
    print("\n📋 推送前检查清单:")
    print("=" * 30)
    print("□ 所有真实API密钥都在.gitignore中")
    print("□ 配置文件使用模板格式（如env.example）")
    print("□ 没有硬编码的密码或令牌")
    print("□ 日志文件被正确忽略")
    print("□ 测试数据不包含真实凭据")
    
    # 5. 返回结果
    total_issues = len(sensitive_issues) + len(gitignore_issues) + len(sensitive_files)
    
    if total_issues == 0:
        print("\n🎉 安全检查通过！可以安全推送到GitHub")
        return True
    else:
        print(f"\n⚠️  发现 {total_issues} 个需要注意的问题，建议修复后再推送")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 