# AI 模块数据结构

## 一、决策相关数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class DecisionType(Enum):
    """决策类型"""
    SPEAK = "speak"                # 发言
    ACT = "act"                   # 执行动作
    SKIP = "skip"                 # 跳过
    WAIT = "wait"                 # 等待

class ActionType(Enum):
    """动作类型"""
    SPEECH = "speech"              # 发言
    MENTAL = "mental"              # 心理活动
    EMOTION = "emotion"            # 情绪表达
    GESTURE = "gesture"            # 手势动作

@dataclass
class DecisionContext:
    """决策上下文"""
    session_id: str
    participant_id: str
    turn_number: int
    recent_messages: List[Dict[str, Any]] = field(default_factory=list)
    session_state: str = "running"
    time_remaining: Optional[float] = None
    rule_states: Dict[str, bool] = field(default_factory=dict)

@dataclass
class AIDecision:
    """AI决策结果"""
    decision_type: DecisionType
    content: str = ""
    mental_activity: Optional[str] = None
    confidence: float = 1.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIAction:
    """AI动作"""
    action_type: ActionType
    content: str
    target: Optional[str] = None
    intensity: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## 二、行为配置

```python
@dataclass
class BehaviorConfig:
    """行为配置"""
    temperature: float = 0.7              # LLM温度
    max_tokens: int = 500                 # 最大令牌数
    top_p: float = 0.9                    # Top-p采样
    presence_penalty: float = 0.0         # 存在惩罚
    frequency_penalty: float = 0.0         # 频率惩罚
    
@dataclass
class ThinkingConfig:
    """思考配置"""
    enabled: bool = True                  # 启用思考模式
    max_thinking_time: float = 5.0       # 最大思考时间（秒）
    include_reasoning: bool = True        # 包含推理过程
    chain_of_thought: bool = True         # 思维链

@dataclass
class ResponseConfig:
    """响应配置"""
    max_response_length: int = 2000        # 最大响应长度
    min_response_length: int = 10          # 最小响应长度
    response_delay: float = 0.0           # 响应延迟
    typing_indicator: bool = True          # 显示打字指示器
```

## 三、提示词模板

```python
@dataclass
class PromptTemplate:
    """提示词模板"""
    system_prompt: str                    # 系统提示
    user_template: str                    # 用户模板
    examples: List[Dict[str, str]] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)

class DefaultPrompts:
    """默认提示词"""
    
    DEBATE_SYSTEM_PROMPT = """你是一个参与辩论的角色扮演AI。
你需要根据给定的角色设定和当前辩论情境，做出符合角色性格的回应。

角色信息:
- 姓名: {participant_name}
- 角色描述: {role_description}
- 性格特点: {personality_traits}
- 说话风格: {speaking_style}

辩论规则:
{debate_rules}

当前辩论状态:
- 当前回合: {turn_number}/{max_turns}
- 剩余时间: {time_remaining}秒
- 对方观点: {opponent_viewpoint}

请以角色的身份，基于上述信息，给出你的回应。
"""

    MENTAL_ACTIVITY_PROMPT = """基于以下对话内容，描述角色的内心想法（心理活动）。
要求:
1. 符合角色性格
2. 不超过50字
3. 使用第一人称

对话内容:
{conversation}
"""
```

## 四、统计和监控

```python
@dataclass
class AIStats:
    """AI统计信息"""
    participant_id: str
    total_decisions: int = 0
    speak_count: int = 0
    act_count: int = 0
    skip_count: int = 0
    avg_thinking_time: float = 0.0
    total_thinking_time: float = 0.0
    rule_violations: int = 0
    last_decision_at: Optional[datetime] = None

@dataclass
class PerformanceMetrics:
    """性能指标"""
    decision_latency_ms: float
    llm_call_latency_ms: float
    total_processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
```
