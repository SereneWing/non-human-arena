# LLM 模块数据结构

## 一、LLM 相关配置

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class LLMProvider(Enum):
    """LLM提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"

class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

@dataclass
class ModelConfig:
    """模型配置"""
    provider: LLMProvider
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    
    # 生成参数
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    
    # 重试配置
    max_retries: int = 3
    timeout: float = 60.0
    
    # 成本控制
    max_cost_per_request: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatMessage:
    """聊天消息"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "name": self.name,
            "function_call": self.function_call
        }

@dataclass
class ChatCompletionRequest:
    """聊天完成请求"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    stream: bool = False
    stop: Optional[List[str]] = None
    user: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream,
            "stop": self.stop,
            "user": self.user
        }

@dataclass
class ChatCompletionResponse:
    """聊天完成响应"""
    id: str
    model: str
    content: str
    finish_reason: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
```

## 二、提示词管理

```python
@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0"
    
    def render(self, **kwargs) -> str:
        """渲染模板"""
        return self.template.format(**kwargs)

@dataclass
class PromptLibrary:
    """提示词库"""
    
    SYSTEM_PROMPTS = {
        "debate": PromptTemplate(
            name="debate",
            template="""你是一个参与辩论的角色扮演AI。
角色信息:
- 姓名: {participant_name}
- 角色描述: {role_description}
- 性格特点: {personality_traits}
- 说话风格: {speaking_style}

辩论规则:
{debate_rules}

请以角色的身份，基于上述信息，给出你的回应。""",
            variables=["participant_name", "role_description", "personality_traits", "speaking_style", "debate_rules"]
        ),
        
        "analysis": PromptTemplate(
            name="analysis",
            template="""分析以下论点:
{content}

请提供:
1. 逻辑分析
2. 可能的反驳
3. 建议的回应策略""",
            variables=["content"]
        ),
    }
```

## 三、调用统计

```python
@dataclass
class LLMCallRecord:
    """LLM调用记录"""
    request_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LLMStats:
    """LLM统计"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    calls_by_model: Dict[str, int] = field(default_factory=dict)
```
