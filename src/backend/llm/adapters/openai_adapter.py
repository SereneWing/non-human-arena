"""OpenAI LLM adapter."""
from __future__ import annotations

import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from llm.base import ChatMessage, LLMAdapter, LLMConfig, LLMResponse, MessageRole


class OpenAIAdapter(LLMAdapter):
    """OpenAI API adapter."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.api_key = config.api_key
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _build_messages(
        self,
        messages: List[ChatMessage],
    ) -> List[Dict[str, Any]]:
        """Build OpenAI-compatible messages."""
        return [msg.to_dict() for msg in messages]
    
    async def chat(
        self,
        messages: List[ChatMessage],
        **kwargs,
    ) -> LLMResponse:
        """Send a chat request to OpenAI."""
        start_time = time.time()
        
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        top_p = kwargs.get("top_p", self.config.top_p)
        stop = kwargs.get("stop", self.config.stop)
        
        payload = {
            "model": self.config.model,
            "messages": self._build_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": False,
        }
        
        if stop:
            payload["stop"] = stop
        
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            data = response.json()
        
        latency_ms = (time.time() - start_time) * 1000
        
        content = data["choices"][0]["message"]["content"]
        finish_reason = data["choices"][0].get("finish_reason", "stop")
        
        return LLMResponse(
            content=content,
            finish_reason=finish_reason,
            usage=data.get("usage", {}),
            latency_ms=latency_ms,
            model=self.config.model,
        )
    
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Send a streaming chat request to OpenAI."""
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        top_p = kwargs.get("top_p", self.config.top_p)
        stop = kwargs.get("stop", self.config.stop)
        
        payload = {
            "model": self.config.model,
            "messages": self._build_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
        }
        
        if stop:
            payload["stop"] = stop
        
        async with httpx.AsyncClient(
            timeout=self.config.timeout,
            follow_redirects=True,
        ) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                if response.status_code != 200:
                    raise Exception(
                        f"OpenAI API error: {response.status_code}"
                    )
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        data = response.json() if False else {}
                        import json as json_module
                        data = json_module.loads(data_str)
                        
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> LLMResponse:
        """Generate text from a prompt."""
        messages = [
            ChatMessage(role=MessageRole.USER, content=prompt),
        ]
        return await self.chat(messages, **kwargs)
