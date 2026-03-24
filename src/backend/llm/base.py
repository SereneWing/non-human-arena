"""LLM base adapter interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(str, Enum):
    """Message role enumeration."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    PARTICIPANT = "participant"


@dataclass
class LLMConfig:
    """LLM configuration."""
    
    provider: str = "openai"
    api_key: str = ""
    base_url: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    timeout: float = 60.0
    max_retries: int = 3


@dataclass
class ChatMessage:
    """Chat message."""
    
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class LLMResponse:
    """LLM response."""
    
    content: str
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    })
    latency_ms: float = 0.0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class LLMAdapter(ABC):
    """Abstract LLM adapter base class."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        **kwargs,
    ) -> LLMResponse:
        """Send a chat request."""
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        **kwargs,
    ):
        """Send a streaming chat request."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> LLMResponse:
        """Generate text from a prompt."""
        pass
