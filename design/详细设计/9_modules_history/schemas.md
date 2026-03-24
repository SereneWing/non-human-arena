# 历史模块数据结构

> ⚠️ **重要**: 本模块定义了历史相关的数据结构。
> **消息模型说明**: `MessageRecord` 是会话消息的历史记录版本，
> 基于 `4_modules_session/schemas.md` 中的 `Message` 模型扩展，
> 添加了 `participant_id`、`participant_name` 等历史查询所需的字段。
> 数据转换应在 `HistoryService` 中完成。

## 一、历史数据类型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class ExportFormat(Enum):
    """导出格式"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"
    XML = "xml"

class HistoryType(Enum):
    """历史类型"""
    SESSION = "session"           # 会话历史
    CONVERSATION = "conversation" # 对话历史
    AUDIT = "audit"               # 审计日志
```

## 二、历史记录数据模型

```python
@dataclass
class HistoryRecord:
    """历史记录"""
    id: str
    session_id: str
    type: HistoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryRecord":
        """从字典创建"""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            type=HistoryType(data["type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            created_by=data.get("created_by")
        )
```

## 三、会话历史

```python
@dataclass
class SessionHistory:
    """会话历史"""
    id: str
    session_id: str
    session_name: str
    messages: List["MessageRecord"] = field(default_factory=list)
    turns: List["TurnRecord"] = field(default_factory=list)
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "session_name": self.session_name,
            "messages": [m.to_dict() for m in self.messages],
            "turns": [t.to_dict() for t in self.turns],
            "summary": self.summary,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@dataclass
class MessageRecord:
    """消息记录"""
    id: str
    session_id: str
    participant_id: str
    participant_name: str
    role: str
    content: str
    type: str = "text"
    mental_activity: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "participant_name": self.participant_name,
            "role": self.role,
            "content": self.content,
            "type": self.type,
            "mental_activity": self.mental_activity,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class TurnRecord:
    """回合记录"""
    id: str
    session_id: str
    turn_number: int
    participant_id: str
    participant_name: str
    message: str
    mental_activity: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "participant_id": self.participant_id,
            "participant_name": self.participant_name,
            "message": self.message,
            "mental_activity": self.mental_activity,
            "action": self.action,
            "timestamp": self.timestamp.isoformat()
        }
```

## 四、导出配置

```python
@dataclass
class ExportConfig:
    """导出配置"""
    format: ExportFormat = ExportFormat.JSON
    include_metadata: bool = True
    include_mental_activity: bool = True
    include_timestamps: bool = True
    include_participants: bool = True
    max_messages: Optional[int] = None  # 限制消息数量
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    template: Optional[str] = None  # 自定义模板
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "format": self.format.value,
            "include_metadata": self.include_metadata,
            "include_mental_activity": self.include_mental_activity,
            "include_timestamps": self.include_timestamps,
            "include_participants": self.include_participants,
            "max_messages": self.max_messages,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "template": self.template
        }
```

## 五、统计信息

```python
@dataclass
class HistoryStats:
    """历史统计"""
    total_sessions: int = 0
    total_messages: int = 0
    total_turns: int = 0
    total_participants: int = 0
    avg_messages_per_session: float = 0.0
    avg_turns_per_session: float = 0.0
    popular_tags: List[Dict[str, Any]] = field(default_factory=list)
    session_duration_stats: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_sessions": self.total_sessions,
            "total_messages": self.total_messages,
            "total_turns": self.total_turns,
            "total_participants": self.total_participants,
            "avg_messages_per_session": self.avg_messages_per_session,
            "avg_turns_per_session": self.avg_turns_per_session,
            "popular_tags": self.popular_tags,
            "session_duration_stats": self.session_duration_stats
        }
```
