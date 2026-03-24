# 会话定义 (Session)

## 一、概述

Session是会话的核心数据结构，定义了会话的基本信息、参与者和配置。

## 二、数据结构

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class SessionState(Enum):
    """会话状态"""
    CREATED = "created"              # 已创建
    INITIALIZING = "initializing"   # 初始化中
    WAITING = "waiting"             # 等待开始
    RUNNING = "running"             # 运行中
    PAUSED = "paused"               # 已暂停
    ENDING = "ending"               # 结束中
    ENDED = "ended"                 # 已结束
    ERROR = "error"                 # 错误状态


@dataclass
class Session:
    """
    会话定义
    
    Attributes:
        id: 会话唯一标识
        topic: 话题
        description: 描述
        state: 会话状态
        config: 会话配置
        participants: 参与者列表
        metadata: 元数据
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    id: str
    topic: str = ""
    description: str = ""
    state: SessionState = SessionState.CREATED
    config: "SessionConfig" = None
    participants: List["Participant"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.state, str):
            self.state = SessionState(self.state)
        if self.config is None:
            self.config = SessionConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "state": self.state.value if isinstance(self.state, SessionState) else self.state,
            "config": self.config.to_dict() if self.config else {},
            "participants": [p.to_dict() if hasattr(p, "to_dict") else p for p in self.participants],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """从字典创建"""
        return cls(
            id=data["id"],
            topic=data.get("topic", ""),
            description=data.get("description", ""),
            state=SessionState(data.get("state", "created")),
            config=SessionConfig.from_dict(data.get("config", {})) if data.get("config") else None,
            participants=[Participant.from_dict(p) for p in data.get("participants", [])],
            metadata=data.get("metadata", {})
        )
```

## 三、会话配置 (SessionConfig)

```python
@dataclass
class SessionConfig:
    """
    会话配置
    
    Attributes:
        max_turns: 最大轮数
        turn_timeout: 轮次超时时间（秒）
        enable_heartbeat: 是否启用心跳
        heartbeat_interval: 心跳间隔（秒）
        enable_mental_activity: 是否启用心理活动
        max_message_length: 最大消息长度
        auto_start: 是否自动开始
    """
    
    max_turns: int = 0                    # 0表示无限制
    turn_timeout: int = 300               # 5分钟
    enable_heartbeat: bool = True
    heartbeat_interval: float = 10.0
    enable_mental_activity: bool = True
    max_message_length: int = 2000
    auto_start: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "max_turns": self.max_turns,
            "turn_timeout": self.turn_timeout,
            "enable_heartbeat": self.enable_heartbeat,
            "heartbeat_interval": self.heartbeat_interval,
            "enable_mental_activity": self.enable_mental_activity,
            "max_message_length": self.max_message_length,
            "auto_start": self.auto_start
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionConfig":
        """从字典创建"""
        return cls(
            max_turns=data.get("max_turns", 0),
            turn_timeout=data.get("turn_timeout", 300),
            enable_heartbeat=data.get("enable_heartbeat", True),
            heartbeat_interval=data.get("heartbeat_interval", 10.0),
            enable_mental_activity=data.get("enable_mental_activity", True),
            max_message_length=data.get("max_message_length", 2000),
            auto_start=data.get("auto_start", False)
        )
```

## 四、参与者 (Participant)

```python
class ParticipantType(Enum):
    """参与者类型"""
    HUMAN = "human"                      # 人类用户
    AI = "ai"                            # AI角色


@dataclass
class Participant:
    """
    参与者
    
    Attributes:
        id: 参与者唯一标识
        session_id: 所属会话ID
        role_id: 关联的角色ID（AI时）
        name: 显示名称
        type: 参与者类型
        metadata: 元数据
        created_at: 创建时间
    """
    
    id: str
    session_id: str
    role_id: Optional[str] = None
    name: str = ""
    type: ParticipantType = ParticipantType.AI
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.type, str):
            self.type = ParticipantType(self.type)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role_id": self.role_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, ParticipantType) else self.type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Participant":
        """从字典创建"""
        return cls(
            id=data["id"],
            session_id=data.get("session_id", ""),
            role_id=data.get("role_id"),
            name=data.get("name", ""),
            type=ParticipantType(data.get("type", "ai")),
            metadata=data.get("metadata", {})
        )
```

## 五、消息 (Message)

```python
class MessageType(Enum):
    """消息类型"""
    TEXT = "text"                        # 文本消息
    SYSTEM = "system"                   # 系统消息
    MENTAL = "mental"                   # 心理活动
    ACTION = "action"                   # 动作消息


@dataclass
class Message:
    """
    消息
    
    Attributes:
        id: 消息唯一标识
        session_id: 所属会话ID
        sender_id: 发送者ID
        content: 消息内容
        type: 消息类型
        metadata: 元数据
        timestamp: 时间戳
    """
    
    id: str
    session_id: str
    sender_id: str
    content: str
    type: MessageType = MessageType.TEXT
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.type, str):
            self.type = MessageType(self.type)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建"""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            sender_id=data["sender_id"],
            content=data["content"],
            type=MessageType(data.get("type", "text")),
            metadata=data.get("metadata", {})
        )
```

## 六、会话上下文 (SessionContext)

```python
@dataclass
class SessionContext:
    """
    会话上下文
    
    包含会话的完整运行时状态。
    """
    
    session: Session
    participants: List[Participant]
    messages: List[Message]
    
    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """获取参与者"""
        for p in self.participants:
            if p.id == participant_id:
                return p
        return None
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """获取最近的消息"""
        return self.messages[-count:] if self.messages else []
    
    def add_participant(self, participant: Participant) -> None:
        """添加参与者"""
        if participant.id not in [p.id for p in self.participants]:
            self.participants.append(participant)
    
    def remove_participant(self, participant_id: str) -> None:
        """移除参与者"""
        self.participants = [p for p in self.participants if p.id != participant_id]
```

## 七、JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Session",
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "description": "会话唯一标识"
    },
    "topic": {
      "type": "string",
      "description": "话题"
    },
    "description": {
      "type": "string",
      "description": "描述"
    },
    "state": {
      "type": "string",
      "enum": ["created", "initializing", "waiting", "running", "paused", "ending", "ended", "error"],
      "description": "会话状态"
    },
    "config": {
      "$ref": "#/definitions/SessionConfig"
    },
    "participants": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Participant"
      }
    },
    "metadata": {
      "type": "object",
      "description": "元数据"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "更新时间"
    }
  },
  "definitions": {
    "SessionConfig": {
      "type": "object",
      "properties": {
        "max_turns": {"type": "integer"},
        "turn_timeout": {"type": "integer"},
        "enable_heartbeat": {"type": "boolean"},
        "heartbeat_interval": {"type": "number"},
        "enable_mental_activity": {"type": "boolean"},
        "max_message_length": {"type": "integer"},
        "auto_start": {"type": "boolean"}
      }
    },
    "Participant": {
      "type": "object",
      "required": ["id", "session_id"],
      "properties": {
        "id": {"type": "string"},
        "session_id": {"type": "string"},
        "role_id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string", "enum": ["human", "ai"]},
        "metadata": {"type": "object"}
      }
    }
  }
}
```

## 八、使用示例

### 8.1 创建会话

```python
session = Session(
    id="session_001",
    topic="AI是否应该取代人类工作",
    description="一场关于AI对就业影响的辩论",
    config=SessionConfig(
        max_turns=20,
        enable_heartbeat=True,
        heartbeat_interval=10.0
    ),
    participants=[
        Participant(
            id="p_001",
            session_id="session_001",
            role_id="advocate_001",
            name="正方辩手",
            type=ParticipantType.AI
        ),
        Participant(
            id="p_002",
            session_id="session_001",
            role_id="opponent_001",
            name="反方辩手",
            type=ParticipantType.AI
        )
    ]
)
```

### 8.2 创建消息

```python
message = Message(
    id="msg_001",
    session_id="session_001",
    sender_id="p_001",
    content="我认为AI的发展将会创造更多就业机会...",
    type=MessageType.TEXT
)
```

### 8.3 获取会话上下文

```python
context = SessionContext(
    session=session,
    participants=session.participants,
    messages=[message]
)

# 获取参与者
participant = context.get_participant("p_001")

# 获取最近消息
recent = context.get_recent_messages(5)
```
