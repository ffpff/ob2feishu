"""
配置管理模块

负责加载和管理应用配置，支持从YAML文件和环境变量读取配置。
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from ruamel.yaml import YAML
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 config/config.yaml
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 优先从环境变量获取
        config_path = os.getenv("OB2FEISHU_CONFIG_PATH")
        if config_path:
            return config_path
        
        # 默认路径
        return "config/config.yaml"
    
    def _load_config(self) -> None:
        """加载配置文件"""
        # 加载.env文件
        load_dotenv()
        
        # 加载YAML配置
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {self.config_path}")
            self.config = self._get_default_config()
            return
        
        try:
            yaml = YAML(typ='safe')
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.load(f) or {}
            
            # 处理环境变量替换
            self._process_env_vars()
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def _process_env_vars(self) -> None:
        """处理配置中的环境变量替换"""
        def replace_env_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                return os.getenv(env_var, obj)
            else:
                return obj
        
        self.config = replace_env_vars(self.config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "obsidian": {
                "vault_path": "",
                "sync_tags": ["飞书知识库"],
                "exclude_folders": [".obsidian", ".trash", "templates"],
                "exclude_patterns": ["*.tmp", "draft-*"]
            },
            "feishu": {
                "api_base_url": "https://open.feishu.cn/open-apis",
                "app_id": "",
                "app_secret": "",
                "target_folder_token": None,
                "api_timeout": 30,
                "max_retries": 3,
                "retry_delay": 1.0
            },
            "sync": {
                "mode": "incremental",
                "batch_size": 50,
                "backup_before_sync": True,
                "backup_dir": "./backups",
                "max_workers": 4
            },
            "conversion": {
                "preserve_obsidian_syntax": False,
                "code_language_mapping": {
                    "js": "javascript",
                    "ts": "typescript",
                    "py": "python"
                },
                "image_handling": "preserve_links"
            },
            "logging": {
                "level": "INFO",
                "file_path": "./logs/ob2feishu.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "max_file_size": 10,
                "backup_count": 5
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，如 'obsidian.vault_path'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，如 'obsidian.vault_path'
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    # 便捷属性访问
    @property
    def obsidian_vault_path(self) -> str:
        """Obsidian库路径"""
        return self.get("obsidian.vault_path", "")
    
    @property
    def obsidian_sync_tags(self) -> List[str]:
        """同步标签列表"""
        return self.get("obsidian.sync_tags", ["飞书知识库"])
    
    @property
    def obsidian_exclude_folders(self) -> List[str]:
        """排除文件夹列表"""
        return self.get("obsidian.exclude_folders", [])
    
    @property
    def obsidian_exclude_patterns(self) -> List[str]:
        """排除文件模式列表"""
        return self.get("obsidian.exclude_patterns", [])
    
    @property
    def feishu_api_base_url(self) -> str:
        """飞书API基础URL"""
        return self.get("feishu.api_base_url", "https://open.feishu.cn/open-apis")
    
    @property
    def feishu_app_id(self) -> str:
        """飞书应用ID"""
        return self.get("feishu.app_id", "")
    
    @property
    def feishu_app_secret(self) -> str:
        """飞书应用密钥"""
        return self.get("feishu.app_secret", "")
    
    @property
    def feishu_target_folder_token(self) -> Optional[str]:
        """飞书目标文件夹token"""
        return self.get("feishu.target_folder_token")
    
    @property
    def feishu_api_timeout(self) -> int:
        """API超时时间"""
        return self.get("feishu.api_timeout", 30)
    
    @property
    def feishu_max_retries(self) -> int:
        """最大重试次数"""
        return self.get("feishu.max_retries", 3)
    
    @property
    def feishu_retry_delay(self) -> float:
        """重试延迟时间"""
        return self.get("feishu.retry_delay", 1.0)
    
    @property
    def sync_mode(self) -> str:
        """同步模式"""
        return self.get("sync.mode", "incremental")
    
    @property
    def sync_batch_size(self) -> int:
        """批量处理大小"""
        return self.get("sync.batch_size", 50)
    
    @property
    def sync_backup_before_sync(self) -> bool:
        """同步前是否备份"""
        return self.get("sync.backup_before_sync", True)
    
    @property
    def sync_backup_dir(self) -> str:
        """备份目录"""
        return self.get("sync.backup_dir", "./backups")
    
    @property
    def sync_max_workers(self) -> int:
        """最大工作线程数"""
        return self.get("sync.max_workers", 4)
    
    @property
    def logging_level(self) -> str:
        """日志级别"""
        # 环境变量可以覆盖配置文件
        return os.getenv("OB2FEISHU_LOG_LEVEL", self.get("logging.level", "INFO"))
    
    @property
    def logging_file_path(self) -> str:
        """日志文件路径"""
        return self.get("logging.file_path", "./logs/ob2feishu.log")
    
    @property
    def logging_format(self) -> str:
        """日志格式"""
        return self.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @property
    def logging_max_file_size(self) -> int:
        """日志文件最大大小（MB）"""
        return self.get("logging.max_file_size", 10)
    
    @property
    def logging_backup_count(self) -> int:
        """日志文件备份数量"""
        return self.get("logging.backup_count", 5)
    
    def validate(self) -> List[str]:
        """
        验证配置完整性
        
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查必需的配置项
        if not self.obsidian_vault_path:
            errors.append("Obsidian库路径未配置 (obsidian.vault_path)")
        
        if not self.feishu_app_id:
            errors.append("飞书应用ID未配置 (feishu.app_id)")
        
        if not self.feishu_app_secret:
            errors.append("飞书应用密钥未配置 (feishu.app_secret)")
        
        # 检查路径是否存在
        if self.obsidian_vault_path and not Path(self.obsidian_vault_path).exists():
            errors.append(f"Obsidian库路径不存在: {self.obsidian_vault_path}")
        
        return errors


# 全局配置实例
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    获取全局配置实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置实例
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """
    重新加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        新的配置实例
    """
    global _config
    _config = Config(config_path)
    return _config 