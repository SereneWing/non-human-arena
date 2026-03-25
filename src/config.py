"""
配置管理模块
负责管理应用配置，包括API Key、模型等设置
"""

import os
from dataclasses import dataclass
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.txt"
CONVERSATIONS_DIR = DATA_DIR / "conversations"


@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str = ""
    model: str = "minimax-m2.7"
    base_url: str = "https://api.minimax.chat/v1"
    temperature: float = 0.7
    max_tokens: int = 100000


@dataclass
class AppConfig:
    """应用配置"""
    llm: LLMConfig = None
    auto_interval: int = 3  # 自动模式间隔（秒）

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMConfig()


def ensure_data_dirs():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)
    CONVERSATIONS_DIR.mkdir(exist_ok=True)


def load_config() -> AppConfig:
    """加载配置"""
    ensure_data_dirs()
    
    config = AppConfig()
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'api_key':
                        config.llm.api_key = value
                    elif key == 'model':
                        config.llm.model = value
                    elif key == 'base_url':
                        config.llm.base_url = value
                    elif key == 'temperature':
                        config.llm.temperature = float(value)
                    elif key == 'max_tokens':
                        config.llm.max_tokens = int(value)
                    elif key == 'auto_interval':
                        config.auto_interval = int(value)
    
    return config


def save_config(config: AppConfig) -> None:
    """保存配置（不包含敏感信息如api_key）"""
    ensure_data_dirs()
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"model={config.llm.model}\n")
        f.write(f"base_url={config.llm.base_url}\n")
        f.write(f"temperature={config.llm.temperature}\n")
        f.write(f"max_tokens={config.llm.max_tokens}\n")
        f.write(f"auto_interval={config.auto_interval}\n")
