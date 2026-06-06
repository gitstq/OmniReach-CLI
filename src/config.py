"""
配置管理模块 / Configuration Management Module

管理 OmniReach-CLI 的全局配置，包括平台启用/禁用、代理设置、输出格式等。
Manages global configuration for OmniReach-CLI, including platform enable/disable,
proxy settings, output format, etc.
"""

import json
import os
import sys

# 默认配置 / Default configuration
DEFAULT_CONFIG = {
    "version": "0.1.0",
    "platforms": {
        "twitter": {"enabled": True, "priority": 1},
        "reddit": {"enabled": True, "priority": 2},
        "youtube": {"enabled": True, "priority": 3},
        "github": {"enabled": True, "priority": 4},
        "bilibili": {"enabled": True, "priority": 5},
        "zhihu": {"enabled": True, "priority": 6},
        "hackernews": {"enabled": True, "priority": 7},
        "medium": {"enabled": True, "priority": 8},
    },
    "proxy": "",
    "timeout": 15,
    "output_format": "table",  # table | json | csv | markdown | text
    "export_dir": "./exports",
    "max_results": 20,
    "color_enabled": True,
    "llm": {
        "enabled": False,
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "max_tokens": 500,
    },
}

# 配置目录 / Configuration directory
CONFIG_DIR = os.path.expanduser("~/.omnireach")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class Config:
    """
    配置管理器。
    Configuration manager.

    支持从配置文件加载、保存配置，以及环境变量覆盖。
    Supports loading/saving from config file and environment variable overrides.
    """

    def __init__(self, config_path=None):
        """
        初始化配置管理器。
        Initialize configuration manager.

        Args:
            config_path: 自定义配置文件路径 / Custom config file path
        """
        self.config_path = config_path or CONFIG_FILE
        self._config = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        """
        从配置文件加载配置。
        Load configuration from config file.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self._deep_merge(self._config, file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[警告/Warning] 配置文件加载失败: {e}")

        # 环境变量覆盖 / Environment variable overrides
        self._apply_env_overrides()

    def _deep_merge(self, base, override):
        """
        深度合并字典。
        Deep merge dictionaries.

        Args:
            base: 基础字典 / Base dictionary (will be modified in-place)
            override: 覆盖字典 / Override dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self):
        """
        应用环境变量覆盖配置。
        Apply environment variable overrides.
        """
        # 代理设置 / Proxy settings
        env_proxy = os.environ.get("OMNIREACH_PROXY", "")
        if env_proxy:
            self._config["proxy"] = env_proxy

        # LLM设置 / LLM settings
        env_api_key = os.environ.get("OMNIREACH_LLM_API_KEY", "")
        if env_api_key:
            self._config["llm"]["api_key"] = env_api_key
            self._config["llm"]["enabled"] = True

        env_base_url = os.environ.get("OMNIREACH_LLM_BASE_URL", "")
        if env_base_url:
            self._config["llm"]["base_url"] = env_base_url

        env_model = os.environ.get("OMNIREACH_LLM_MODEL", "")
        if env_model:
            self._config["llm"]["model"] = env_model

    def save(self):
        """
        保存配置到文件。
        Save configuration to file.
        """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[错误/Error] 配置文件保存失败: {e}")

    def get(self, key, default=None):
        """
        获取配置值（支持点号分隔的嵌套键）。
        Get configuration value (supports dot-separated nested keys).

        Args:
            key: 配置键 / Config key (e.g. "llm.api_key")
            default: 默认值 / Default value

        Returns:
            配置值 / Configuration value
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """
        设置配置值（支持点号分隔的嵌套键）。
        Set configuration value (supports dot-separated nested keys).

        Args:
            key: 配置键 / Config key
            value: 配置值 / Config value
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    @property
    def proxy(self):
        """获取代理设置 / Get proxy setting"""
        return self.get("proxy", "")

    @property
    def timeout(self):
        """获取超时设置 / Get timeout setting"""
        return self.get("timeout", 15)

    @property
    def output_format(self):
        """获取输出格式 / Get output format"""
        return self.get("output_format", "table")

    @property
    def enabled_platforms(self):
        """
        获取已启用的平台列表。
        Get list of enabled platforms.

        Returns:
            list: 已启用的平台名称列表 / List of enabled platform names
        """
        platforms = self.get("platforms", {})
        return [name for name, cfg in platforms.items() if cfg.get("enabled", True)]

    def is_platform_enabled(self, platform_name):
        """
        检查平台是否启用。
        Check if a platform is enabled.

        Args:
            platform_name: 平台名称 / Platform name

        Returns:
            bool: 是否启用 / Whether enabled
        """
        return self.get(f"platforms.{platform_name}.enabled", True)

    def enable_platform(self, platform_name, enabled=True):
        """
        启用/禁用平台。
        Enable/disable a platform.

        Args:
            platform_name: 平台名称 / Platform name
            enabled: 是否启用 / Whether to enable
        """
        self.set(f"platforms.{platform_name}.enabled", enabled)

    @property
    def all(self):
        """获取完整配置字典 / Get full configuration dictionary"""
        return dict(self._config)

    def __repr__(self):
        return f"<Config(path={self.config_path})>"
