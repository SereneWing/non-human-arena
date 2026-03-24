# AI代理定义 (AIAgent)

## 一、概述

AIAgent是会话中AI角色的运行时实体，关联角色定义并包含运行状态。

## 二、数据结构

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

@dataclass
class AIAgent:
    """
    AI代理
    
    Attributes:
        id: 代理唯一标识
        role_id: 关联的角色ID
        session_id: 所属会话ID
        name: 显示名称
        role: 角色定义
        emotional_state: 当前情绪状态
        skills: 技能列表
        message_count: 发言次数
        created_at: 创建时间
        last_speak_time: 最后发言时间
    """
    
    id: str
    role_id: str
    session_id: str
    name: str = ""
    role: Optional["Role"] = None
    emotional_state: Optional["EmotionalState"] = None
    skills: List["Skill"] = field(default_factory=list)
    message_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_speak_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "role_id": self.role_id,
            "session_id": self.session_id,
            "name": self.name,
            "role": self.role.to_dict() if self.role else None,
            "emotional_state": self.emotional_state.to_dict() if self.emotional_state else None,
            "skills": [s.to_dict() for s in self.skills],
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_speak_time": self.last_speak_time.isoformat() if self.last_speak_time else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAgent":
        """从字典创建"""
        return cls(
            id=data["id"],
            role_id=data["role_id"],
            session_id=data["session_id"],
            name=data.get("name", ""),
            role=Role.from_dict(data["role"]) if data.get("role") else None,
            emotional_state=EmotionalState.from_dict(data["emotional_state"]) if data.get("emotional_state") else None,
            skills=[Skill.from_dict(s) for s in data.get("skills", [])]
        )
```

## 三、AI决策 (AIDecision)

```python
class DecisionType(Enum):
    """决策类型"""
    SPEAK = "speak"                    # 发言
    SKIP = "skip"                      # 跳过
    WAIT = "wait"                      # 等待


@dataclass
class AIDecision:
    """
    AI决策
    
    Attributes:
        type: 决策类型
        should_speak: 是否应该发言
        reason: 决策原因
        context: 决策上下文
        confidence: 置信度
    """
    
    type: DecisionType = DecisionType.WAIT
    should_speak: bool = False
    reason: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value if isinstance(self.type, DecisionType) else self.type,
            "should_speak": self.should_speak,
            "reason": self.reason,
            "context": self.context,
            "confidence": self.confidence,
        }
```

## 四、心理活动 (MentalActivity)

```python
class MentalActivityType(Enum):
    """心理活动类型"""
    THINKING = "thinking"              # 思考
    FEELING = "feeling"                # 感受
    PLANNING = "planning"              # 计划
    RECALLING = "recalling"            # 回忆
    IDLE = "idle"                      # 空闲


@dataclass
class MentalActivity:
    """
    心理活动
    
    Attributes:
        id: 活动唯一标识
        agent_id: 所属代理ID
        type: 活动类型
        content: 活动内容
        timestamp: 时间戳
        visible: 是否对其他参与者可见
    """
    
    id: str
    agent_id: str
    type: MentalActivityType = MentalActivityType.IDLE
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    visible: bool = False
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.type, str):
            self.type = MentalActivityType(self.type)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "type": self.type.value if isinstance(self.type, MentalActivityType) else self.type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "visible": self.visible,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MentalActivity":
        """从字典创建"""
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            type=MentalActivityType(data.get("type", "idle")),
            content=data.get("content", ""),
            visible=data.get("visible", False)
        )
```

## 五、情绪状态 (EmotionalState)

```python
class EmotionType(Enum):
    """情绪类型"""
    HAPPY = "happy"                    # 开心
    SAD = "sad"                        # 伤心
    ANGRY = "angry"                    # 生气
    AFRAID = "afraid"                  # 害怕
    SURPRISED = "surprised"            # 惊讶
    NEUTRAL = "neutral"                # 中性


@dataclass
class EmotionalState:
    """
    情绪状态
    
    Attributes:
        agent_id: 所属代理ID
        primary: 主要情绪
        intensity: 情绪强度（0-1）
        trigger: 触发原因
        timestamp: 时间戳
        history: 历史情绪记录
    """
    
    agent_id: str
    primary: EmotionType = EmotionType.NEUTRAL
    intensity: float = 0.5
    trigger: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.primary, str):
            self.primary = EmotionType(self.primary)
    
    def to_dict(self) Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "primary": self.primary.value if isinstance(self.primary, EmotionType) else self.primary,
            "intensity": self.intensity,
            "trigger": self.trigger,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "history": self.history,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalState":
        """从字典创建"""
        return cls(
            agent_id=data["agent_id"],
            primary=EmotionType(data.get("primary", "neutral")),
            intensity=data.get("intensity", 0.5),
            trigger=data.get("trigger", ""),
            history=data.get("history", [])
        )
```

## 六、技能 (Skill)

```python
class SkillType(Enum):
    """技能类型"""
    DEBATE = "debate"                  # 辩论技能
    PERSUASION = "persuasion"          # 说服技能
    ANALYSIS = "analysis"              # 分析技能
    COUNTER = "counter"               # 反驳技能
    CUSTOM = "custom"                  # 自定义技能


@dataclass
class SkillCondition:
    """技能前置条件"""
    field: str
    operator: str  # exists, equals, contains, greater_than, less_than
    value: Any = None


@dataclass
class Skill:
    """
    技能
    
    Attributes:
        id: 技能唯一标识
        name: 技能名称
        type: 技能类型
        description: 技能描述
        preconditions: 前置条件
        parameters: 技能参数
        enabled: 是否启用
    """
    
    id: str
    name: str
    type: SkillType = SkillType.CUSTOM
    description: str = ""
    preconditions: List[SkillCondition] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def __post_init__(self):
        """后置初始化"""
        if isinstance(self.type, str):
            self.type = SkillType(self.type)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, SkillType) else self.type,
            "description": self.description,
            "preconditions": [
                {"field": p.field, "operator": p.operator, "value": p.value}
                for p in self.preconditions
            ],
            "parameters": self.parameters,
            "enabled": self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=SkillType(data.get("type", "custom")),
            description=data.get("description", ""),
            preconditions=[
                SkillCondition(
                    field=p["field"],
                    operator=p["operator"],
                    value=p.get("value")
                )
                for p in data.get("preconditions", [])
            ],
            parameters=data.get("parameters", {})
        )


@dataclass
class SkillResult:
    """技能执行结果"""
    skill_id: str
    success: bool
    result: Any = None
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "skill_id": self.skill_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
        }
```

## 七、JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AIAgent",
  "type": "object",
  "required": ["id", "role_id", "session_id"],
  "properties": {
    "id": {"type": "string"},
    "role_id": {"type": "string"},
    "session_id": {"type": "string"},
    "name": {"type": "string"},
    "role": {"$ref": "#/definitions/Role"},
    "emotional_state": {"$ref": "#/definitions/EmotionalState"},
    "skills": {
      "type": "array",
      "items": {"$ref": "#/definitions/Skill"}
    },
    "message_count": {"type": "integer"},
    "last_speak_time": {"type": "string", "format": "date-time"}
  },
  "definitions": {
    "Role": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "category": {"type": "string"},
        "base_personality": {"type": "object"}
      }
    },
    "EmotionalState": {
      "type": "object",
      "properties": {
        "primary": {"type": "string"},
        "intensity": {"type": "number"},
        "trigger": {"type": "string"}
      }
    },
    "Skill": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "description": {"type": "string"},
        "preconditions": {"type": "array"},
        "parameters": {"type": "object"},
        "enabled": {"type": "boolean"}
      }
    }
  }
}
```

## 八、使用示例

### 8.1 创建AI代理

```python
agent = AIAgent(
    id="agent_001",
    role_id="advocate_001",
    session_id="session_001",
    name="正方辩手",
    role=role,
    emotional_state=EmotionalState(
        agent_id="agent_001",
        primary=EmotionType.NEUTRAL,
        intensity=0.5
    ),
    skills=[
        Skill(
            id="counter_argument",
            name="反驳技巧",
            type=SkillType.COUNTER,
            description="擅长反驳对方论点"
        )
    ]
)
```

### 8.2 创建心理活动

```python
activity = MentalActivity(
    id="mental_001",
    agent_id="agent_001",
    type=MentalActivityType.THINKING,
    content="我需要找到更有说服力的例子来支持我的观点...",
    visible=True
)
```

### 8.3 更新情绪

```python
state = EmotionalState(
    agent_id="agent_001",
    primary=EmotionType.HAPPY,
    intensity=0.7,
    trigger="agreement"
)
```
