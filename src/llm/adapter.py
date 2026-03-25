"""
LLM适配器基类
定义统一的LLM调用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, AsyncIterator, Optional
import httpx


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.minimax.chat/v1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: float = 60.0
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    @property
    @abstractmethod
    def name(self) -> str:
        """适配器名称"""
        pass
    
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """发送对话请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            return ChatResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                usage=data.get("usage", {}),
                finish_reason=data["choices"][0].get("finish_reason", "stop")
            )
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """流式对话请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        import json
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue


class MiniMaxAdapter(LLMAdapter):
    """MiniMax适配器（OpenAI兼容）"""
    
    @property
    def name(self) -> str:
        return "minimax"
