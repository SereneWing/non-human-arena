"""LLM manager."""
from __future__ import annotations

import logging
from typing import Dict, Optional

from llm.base import ChatMessage, LLMAdapter, LLMConfig, LLMResponse
from llm.adapters.openai_adapter import OpenAIAdapter

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM manager for handling multiple LLM providers."""
    
    def __init__(self, default_config: Optional[LLMConfig] = None):
        self.default_config = default_config or LLMConfig()
        self._adapters: Dict[str, LLMAdapter] = {}
    
    def register_adapter(self, provider: str, adapter: LLMAdapter) -> None:
        """Register an LLM adapter."""
        self._adapters[provider] = adapter
        logger.info(f"Registered LLM adapter: {provider}")
    
    def get_adapter(self, provider: Optional[str] = None) -> LLMAdapter:
        """Get an LLM adapter."""
        provider = provider or self.default_config.provider
        
        if provider not in self._adapters:
            if provider == "openai":
                adapter = OpenAIAdapter(self.default_config)
                self.register_adapter(provider, adapter)
            else:
                raise ValueError(f"Unknown LLM provider: {provider}")
        
        return self._adapters[provider]
    
    async def chat(
        self,
        messages: list[ChatMessage],
        provider: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """Send a chat request."""
        adapter = self.get_adapter(provider)
        return await adapter.chat(messages, **kwargs)
    
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        provider: Optional[str] = None,
        **kwargs,
    ):
        """Send a streaming chat request."""
        adapter = self.get_adapter(provider)
        return await adapter.stream_chat(messages, **kwargs)
    
    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate text from a prompt."""
        adapter = self.get_adapter(provider)
        return await adapter.generate(prompt, **kwargs)


_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def set_llm_manager(manager: LLMManager) -> None:
    """Set the global LLM manager instance."""
    global _llm_manager
    _llm_manager = manager
