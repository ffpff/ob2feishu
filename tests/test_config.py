"""
配置模块测试
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.ob2feishu.config import Config, get_config, reload_config


class TestConfig:
    """配置类测试"""
    
    def test_default_config(self):
        """测试默认配置加载"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建一个不存在的配置文件路径
            config_path = os.path.join(temp_dir, "nonexistent.yaml")
            config = Config(config_path)
            
            # 验证默认配置
            assert config.obsidian_sync_tags == ["飞书知识库"]
            assert config.feishu_api_base_url == "https://open.feishu.cn/open-apis"
            assert config.sync_mode == "incremental"
    
    def test_config_loading(self):
        """测试配置文件加载"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            config_content = """
obsidian:
  vault_path: "/test/path"
  sync_tags:
    - "测试标签"
feishu:
  app_id: "test_app_id"
  app_secret: "test_secret"
"""
            config_file.write_text(config_content, encoding='utf-8')
            
            config = Config(str(config_file))
            
            assert config.obsidian_vault_path == "/test/path"
            assert config.obsidian_sync_tags == ["测试标签"]
            assert config.feishu_app_id == "test_app_id"
            assert config.feishu_app_secret == "test_secret"
    
    @patch.dict(os.environ, {"TEST_VAR": "env_value"})
    def test_env_var_replacement(self):
        """测试环境变量替换"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            config_content = """
feishu:
  app_id: "${TEST_VAR}"
"""
            config_file.write_text(config_content, encoding='utf-8')
            
            config = Config(str(config_file))
            
            assert config.feishu_app_id == "env_value"
    
    def test_config_get_set(self):
        """测试配置获取和设置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用不存在的配置文件，确保加载默认配置
            config_path = os.path.join(temp_dir, "nonexistent.yaml")
            config = Config(config_path)
            
            # 测试嵌套键获取
            assert config.get("obsidian.vault_path", "") == ""
            assert config.get("nonexistent.key", "default") == "default"
            
            # 测试设置
            config.set("test.nested.key", "test_value")
            assert config.get("test.nested.key") == "test_value"
    
    def test_config_validation(self):
        """测试配置验证"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用不存在的配置文件，确保加载默认配置
            config_path = os.path.join(temp_dir, "nonexistent.yaml")
            config = Config(config_path)
            
            errors = config.validate()
            
            # 应该有错误（因为必需配置未设置）
            assert len(errors) > 0
            assert any("Obsidian库路径未配置" in error for error in errors)
            assert any("飞书应用ID未配置" in error for error in errors)
    
    @patch.dict(os.environ, {"OB2FEISHU_LOG_LEVEL": "DEBUG"})
    def test_env_override(self):
        """测试环境变量覆盖"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用不存在的配置文件，确保加载默认配置
            config_path = os.path.join(temp_dir, "nonexistent.yaml")
            config = Config(config_path)
            
            # 环境变量应该覆盖配置文件
            assert config.logging_level == "DEBUG"


def test_global_config():
    """测试全局配置"""
    # 重置全局配置
    reload_config()
    
    config1 = get_config()
    config2 = get_config()
    
    # 应该是同一个实例
    assert config1 is config2


if __name__ == "__main__":
    pytest.main([__file__]) 