# Obsidian到飞书知识库同步工具

这是一个将Obsidian笔记同步到飞书知识库的Python工具，支持增量同步、格式转换、批量处理等功能。

## ✨ 主要特性

- 🔄 **增量同步**: 基于YAML front-matter的智能增量同步
- 📝 **格式转换**: Markdown到飞书富文本格式的自动转换
- 🏷️ **标签过滤**: 根据指定标签自动筛选需要同步的笔记
- 🚀 **高性能**: 支持批量操作和并发处理
- 💾 **状态管理**: 自动跟踪同步状态，避免重复操作
- 🛡️ **安全可靠**: 支持备份、错误重试、冲突检测

## 📋 系统要求

- Python 3.8+
- 飞书开放平台应用权限
- Obsidian笔记库

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/your-username/ob2feishu.git
cd ob2feishu

# 安装依赖
pip install -r requirements.txt

# 或使用开发模式安装
pip install -e .
```

### 2. 配置

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑.env文件，填入飞书应用信息
# FEISHU_APP_ID=cli_your_app_id_here
# FEISHU_APP_SECRET=your_app_secret_here
```

### 3. 配置同步设置

编辑 `config/config.yaml` 文件：

```yaml
obsidian:
  vault_path: "/path/to/your/obsidian/vault"
  sync_tags:
    - "飞书知识库"
```

### 4. 运行同步

```bash
# 执行同步
ob2feishu sync

# 或使用Python模块方式
python -m ob2feishu.cli sync
```

## 📁 项目结构

```
ob2feishu/
├── src/ob2feishu/          # 主要源代码
│   ├── __init__.py
│   ├── cli.py              # 命令行界面
│   ├── sync_manager.py     # 同步管理器
│   ├── feishu_client.py    # 飞书API客户端
│   ├── obsidian_parser.py  # Obsidian文件解析器
│   └── markdown_converter.py # Markdown转换器
├── config/                 # 配置文件
│   └── config.yaml
├── docs/                   # 文档
│   └── feishu-api/         # 飞书API文档
├── tests/                  # 测试代码
├── examples/               # 示例文件
├── requirements.txt        # 依赖列表
└── README.md
```

## 📖 使用说明

### 笔记准备

在需要同步的Obsidian笔记中添加标签：

```yaml
---
tags: ["飞书知识库"]
title: "我的笔记标题"
---

# 笔记内容

这里是笔记的正文内容...
```

### 同步状态

同步完成后，工具会自动在YAML front-matter中添加同步状态：

```yaml
---
tags: ["飞书知识库"]
title: "我的笔记标题"
feishu_document_id: "doxcnAJ9VRRJqVMYZ1MyKnavXWe"
feishu_last_sync: "2024-12-25T10:30:00Z"
feishu_sync_version: 1
---
```

### 命令行选项

```bash
# 查看帮助
ob2feishu --help

# 指定配置文件
ob2feishu --config /path/to/config.yaml sync

# 强制全量同步
ob2feishu sync --full

# 只检查不实际同步
ob2feishu sync --dry-run
```

## 🔧 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src/ob2feishu
```

### 代码格式化

```bash
# 格式化代码
black src/ tests/

# 检查代码质量
flake8 src/ tests/
```

## 📚 文档

- [飞书API接口文档](./docs/feishu-api/README.md)
- [增量同步策略](./docs/feishu-api/08-sync-strategy.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## ⚠️ 注意事项

- 请确保备份重要数据
- 首次使用建议在测试环境中验证
- 飞书API有调用频率限制，大量文件同步时请注意
- 工具会修改Obsidian笔记的YAML front-matter，请提前备份

## 🐛 问题排查

### 常见问题

1. **认证失败**: 检查飞书应用ID和密钥是否正确
2. **文件未同步**: 确认笔记包含指定的同步标签
3. **格式转换问题**: 查看日志文件了解详细错误信息
4. **YAML格式错误**: 工具会尝试保持原有格式，如有问题请检查原始文件

### 日志查看

```bash
# 查看最新日志
tail -f ./logs/ob2feishu.log

# 启用调试模式
export OB2FEISHU_LOG_LEVEL=DEBUG
ob2feishu sync
```

---

如有问题，请提交Issue或联系开发团队。 