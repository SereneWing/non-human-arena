"""AI service implementation."""
from __future__ import annotations

import logging
from typing import List, Optional

from llm.base import ChatMessage, LLMConfig, LLMResponse, MessageRole
from llm.manager import LLMManager

logger = logging.getLogger(__name__)


class AIService:
    """AI service for generating responses."""
    
    def __init__(
        self,
        llm_manager: LLMManager,
        config: Optional[LLMConfig] = None,
    ):
        self.llm_manager = llm_manager
        self.config = config or LLMConfig()
    
    async def generate_response(
        self,
        system_prompt: str,
        messages: List[ChatMessage],
        **kwargs,
    ) -> LLMResponse:
        """Generate an AI response."""
        all_messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *messages,
        ]
        
        return await self.llm_manager.chat(
            messages=all_messages,
            **kwargs,
        )
    
    async def generate_with_context(
        self,
        context: str,
        current_message: str,
        **kwargs,
    ) -> LLMResponse:
        """Generate response with context."""
        prompt = f"""Context:
{context}

Current message:
{current_message}

Please respond appropriately based on the context and current message."""
        
        return await self.llm_manager.generate(prompt, **kwargs)
    
    async def generate_stream(
        self,
        system_prompt: str,
        messages: List[ChatMessage],
        **kwargs,
    ):
        """Generate a streaming AI response."""
        all_messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            *messages,
        ]
        
        return await self.llm_manager.stream_chat(
            messages=all_messages,
            **kwargs,
        )


_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get the global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(get_llm_manager())
    return _ai_service


def set_ai_service(service: AIService) -> None:
    """Set the global AI service instance."""
    global _ai_service
    _ai_service = service
