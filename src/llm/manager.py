"""
LLM管理器
管理LLM适配器的创建和获取
"""

from typing import Dict, Optional
from .adapter import LLMAdapter, MiniMaxAdapter, ChatMessage, ChatResponse
from ..config import LLMConfig
import asyncio


class LLMManager:
    """LLM管理器"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._adapter: Optional[LLMAdapter] = None
        self._config: Optional[LLMConfig] = None
    
    async def initialize(self, config: LLMConfig) -> None:
        """初始化LLM管理器"""
        async with self._lock:
            self._config = config
            self._adapter = MiniMaxAdapter(
                api_key=config.api_key,
                model=config.model,
                base_url=config.base_url,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
    
    async def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        """发送对话请求"""
        if self._adapter is None:
            raise Exception("LLM管理器未初始化，请先配置API Key")
        return await self._adapter.chat(messages)
    
    async def chat_stream(self, messages: list[ChatMessage]):
        """流式对话请求"""
        if self._adapter is None:
            raise Exception("LLM管理器未初始化，请先配置API Key")
        return self._adapter.chat_stream(messages)
    
    def get_config(self) -> Optional[LLMConfig]:
        """获取当前配置"""
        return self._config
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._adapter is not None and self._config is not None and self._config.api_key != ""


# 全局LLM管理器实例
llm_manager = LLMManager()
