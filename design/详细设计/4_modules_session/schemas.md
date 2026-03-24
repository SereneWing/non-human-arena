# 会话模块数据结构

> ⚠️ **重要**: 此文件统一定义 SessionState 枚举，其他文件应引用此定义。

## 一、会话状态机

```python
from enum import Enum

class SessionState(Enum):
    """会话状态
    
    状态流转图:
    ┌─────────┐     ┌───────────────┐     ┌─────────┐
    │ CREATED │ ──► │ INITIALIZING  │ ──► │ WAITING │ ──┐
    └─────────┘     └───────────────┘     └─────────┘   │
                                                          │
      ┌───────────────────────────────────────────────────┘
      │
      ▼
    ┌─────────┐     ┌─────────┐     ┌───────────┐
    │ RUNNING │ ◄──► │ PAUSED  │     │  ERROR    │
    └─────────┘     └─────────┘     └───────────┘
      │                                   ▲
      │                                   │
      ▼                                   │
    ┌──────────┐    ┌───────────┐         │
    │ ENDING   │ ─► │ COMPLETED │ ◄───────┤
    └──────────┘    └───────────┘         │
      │                                   │
      ▼                                   │
    ┌───────────┐                        │
    │CANCELLED  │ ───────────────────────┘
    └───────────┘
    """
    CREATED = "created"             # 已创建（初始状态）
    INITIALIZING = "initializing"   # 初始化中
    WAITING = "waiting"             # 等待开始
    RUNNING = "running"             # 运行中
    PAUSED = "paused"               # 暂停
    ENDING = "ending"               # 结束中
    COMPLETED = "completed"         # 已完成（终态）
    ERROR = "error"                 # 错误
    CANCELLED = "cancelled"         # 已取消（终态）

class StateTransition:
    """状态转换规则
    
    说明:
    - CREATED: 初始状态，只能转到 INITIALIZING
    - INITIALIZING: 初始化中，完成后转到 WAITING
    - WAITING: 等待开始，可转到 RUNNING 或 CANCELLED
    - RUNNING: 运行中，可转到 PAUSED、ENDING 或 ERROR
    - PAUSED: 暂停，可转到 RUNNING 或 CANCELLED
    - ENDING: 结束中，最终转到 COMPLETED
    - COMPLETED: 终态，不可转换
    - ERROR: 错误状态，可重试到 WAITING 或取消到 CANCELLED
    - CANCELLED: 终态，不可转换
    """
    VALID_TRANSITIONS = {
        SessionState.CREATED: [SessionState.INITIALIZING],
        SessionState.INITIALIZING: [SessionState.WAITING, SessionState.ERROR],
        SessionState.WAITING: [SessionState.RUNNING, SessionState.CANCELLED],
        SessionState.RUNNING: [SessionState.PAUSED, SessionState.ENDING, SessionState.ERROR],
        SessionState.PAUSED: [SessionState.RUNNING, SessionState.CANCELLED],
        SessionState.ENDING: [SessionState.COMPLETED, SessionState.CANCELLED],
        SessionState.ERROR: [SessionState.WAITING, SessionState.CANCELLED],  # 可重试
        SessionState.COMPLETED: [],  # 终态
        SessionState.CANCELLED: [],   # 终态
    }
    
    @classmethod
    def can_transition(cls, from_state: SessionState, to_state: SessionState) -> bool:
        """检查是否允许转换"""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def get_next_states(cls, from_state: SessionState) -> list:
        """获取可转换的目标状态"""
        return cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def is_terminal(cls, state: SessionState) -> bool:
        """判断是否为终态"""
        return state in [SessionState.COMPLETED, SessionState.CANCELLED]
```

## 二、会话数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class Session:
    """会话"""
    id: str
    name: str
    topic: str = ""  # 辩论话题/讨论主题
    state: SessionState
    template_id: str
    role_ids: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_by: Optional[str] = None
    participant_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "topic": self.topic,
            "state": self.state.value,
            "template_id": self.template_id,
            "role_ids": self.role_ids,
            "config": self.config,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_by": self.created_by,
            "participant_ids": self.participant_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        return cls(
            id=data["id"],
            name=data["name"],
            topic=data.get("topic", ""),
            state=SessionState(data.get("state", "created")),
            template_id=data.get("template_id", ""),
            role_ids=data.get("role_ids", []),
            config=data.get("config", {}),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data and isinstance(data["created_at"], str) else (data.get("created_at") or datetime.now()),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            created_by=data.get("created_by"),
            participant_ids=data.get("participant_ids", [])
        )

@dataclass
class SessionConfig:
    """会话配置"""
    max_turns: Optional[int] = None           # 最大回合数
    max_duration: Optional[int] = None       # 最大时长（秒）
    allow_skip: bool = True                  # 允许跳过
    enable_history: bool = True              # 启用历史
    enable_heartbeat: bool = True             # 启用心跳
    heartbeat_interval: float = 1.0           # 心跳间隔
    enable_mental_activity: bool = True      # 启用心理活动
    max_message_length: int = 2000            # 最大消息长度
    temperature: float = 0.7                 # LLM温度
    enable_rule_check: bool = True           # 启用规则检查
    
    def to_dict(self) -> Dict[str, Any]:
        ...

@dataclass
class SessionParticipant:
    """会话参与者"""
    participant_id: str
    role_id: str
    is_ai: bool = True
    joined_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        ...

@dataclass
class Turn:
    """会话回合"""
    id: str
    session_id: str
    turn_number: int
    participant_id: str
    message: str = ""
    mental_activity: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
```

## 三、会话消息

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    """消息类型"""
    TEXT = "text"                    # 文本消息
    ACTION = "action"               # 动作消息
    MENTAL = "mental"               # 心理活动
    SYSTEM = "system"               # 系统消息
    SPEECH = "speech"               # 发言消息

class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    PARTICIPANT = "participant"

@dataclass
class Message:
    """消息"""
    id: str
    session_id: str
    type: MessageType
    role: MessageRole
    content: str
    participant_id: Optional[str] = None
    turn_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        ...
```

## 四、会话上下文

```python
@dataclass
class SessionContext:
    """会话上下文"""
    session_id: str
    state: SessionState
    turn_count: int = 0
    participants: Dict[str, SessionParticipant] = field(default_factory=dict)
    current_turn_participant: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    def get_history_prompt(self, max_messages: int = 20) -> str:
        """获取历史提示"""
        ...

@dataclass
class SessionStats:
    """会话统计"""
    session_id: str
    total_turns: int = 0
    total_messages: int = 0
    participant_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rule_violations: int = 0
    rule_triggers: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        ...
```
