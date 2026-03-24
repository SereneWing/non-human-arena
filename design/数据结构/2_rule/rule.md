# 规则定义 (Rule)

## 一、概述

Rule是规则执行时的实例，包含规则模板的具体配置和运行时状态。

## 二、数据结构

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class RuleType(Enum):
    """规则类型"""
    DEBATE = "debate"              # 辩论规则
    GAME = "game"                  # 游戏规则
    MODERATION = "moderation"      # 主持规则
    CUSTOM = "custom"             # 自定义规则


@dataclass
class Rule:
    """
    规则定义
    
    Attributes:
        id: 规则唯一标识
        name: 规则名称
        type: 规则类型
        description: 规则描述
        triggers: 触发器列表
        constraints: 约束条件列表
        consequences: 结果动作列表
        priority: 优先级
        enabled: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    id: str
    name: str
    type: RuleType = RuleType.DEBATE
    description: str = ""
    triggers: List["Trigger"] = field(default_factory=list)
    constraints: List["Constraint"] = field(default_factory=list)
    consequences: List["Consequence"] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_template(cls, template: "RuleTemplate") -> "Rule":
        """从模板创建规则实例"""
        return cls(
            id=f"rule_{uuid.uuid4().hex[:8]}",
            name=template.name,
            type=template.type,
            description=template.description,
            triggers=[Trigger.from_dict(t) for t in template.triggers],
            constraints=[Constraint.from_dict(c) for c in template.constraints],
            consequences=[Consequence.from_dict(c) for c in template.consequences],
            priority=template.priority,
            enabled=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, RuleType) else self.type,
            "description": self.description,
            "triggers": [t.to_dict() if hasattr(t, "to_dict") else t for t in self.triggers],
            "constraints": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.constraints],
            "consequences": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.consequences],
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
```

## 三、约束条件 (Constraint)

```python
@dataclass
class Constraint:
    """
    约束条件
    
    Attributes:
        type: 约束类型
        target: 目标（participant, all, role_id）
        condition: 条件表达式
        error_message: 错误消息
        params: 额外参数
    """
    
    type: str
    target: str = "participant"
    condition: str = "true"
    error_message: str = "Constraint violated"
    params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Constraint":
        """从字典创建"""
        return cls(
            type=data.get("type", "unknown"),
            target=data.get("target", "participant"),
            condition=data.get("condition", "true"),
            error_message=data.get("error_message", "Constraint violated"),
            params=data.get("params", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type,
            "target": self.target,
            "condition": self.condition,
            "error_message": self.error_message,
            "params": self.params
        }


# 预定义约束类型
class ConstraintType:
    """约束类型常量"""
    MESSAGE_LENGTH = "message_length"        # 消息长度
    MESSAGE_COUNT = "message_count"          # 发言次数
    TIME_INTERVAL = "time_interval"          # 时间间隔
    KEYWORD = "keyword"                       # 关键词
    REGEX = "regex"                          # 正则表达式
    CUSTOM = "custom"                         # 自定义
```

## 四、触发器 (Trigger)

```python
@dataclass
class Trigger:
    """
    触发器
    
    Attributes:
        event_type: 事件类型
        condition: 触发条件
        params: 额外参数
    """
    
    event_type: str
    condition: str = "true"
    params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trigger":
        """从字典创建"""
        return cls(
            event_type=data.get("event_type", ""),
            condition=data.get("condition", "true"),
            params=data.get("params", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_type": self.event_type,
            "condition": self.condition,
            "params": self.params
        }
```

## 五、结果动作 (Consequence)

```python
from typing import Union
from dataclasses import dataclass

@dataclass
class Consequence:
    """
    结果动作
    
    Attributes:
        action: 动作类型
        params: 动作参数
    """
    
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Consequence":
        """从字典创建"""
        return cls(
            action=data.get("action", ""),
            params=data.get("params", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "action": self.action,
            "params": self.params
        }


# 预定义动作类型
class ConsequenceAction:
    """动作类型常量"""
    SKIP = "skip"                             # 跳过
    PENALTY = "penalty"                       # 扣分
    BROADCAST = "broadcast"                   # 广播消息
    WARN = "warn"                             # 警告
    MUTE = "mute"                             # 禁言
    KICK = "kick"                            # 踢出
    CUSTOM = "custom"                        # 自定义


@dataclass
class ConsequenceSkip:
    """跳过动作参数"""
    reason: str = ""
    skip_turn: int = 1


@dataclass
class ConsequencePenalty:
    """扣分动作参数"""
    target: str = ""
    points: int = 0
    reason: str = ""


@dataclass
class ConsequenceBroadcast:
    """广播动作参数"""
    message: str = ""
    to: str = "all"
```

## 六、规则模板 (RuleTemplate)

```python
@dataclass
class RuleTemplate:
    """
    规则模板
    
    模板是规则的预定义配置，可以在创建规则时继承。
    """
    
    id: str
    name: str
    type: RuleType = RuleType.DEBATE
    description: str = ""
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    consequences: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True
    is_builtin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, RuleType) else self.type,
            "description": self.description,
            "triggers": self.triggers,
            "constraints": self.constraints,
            "consequences": self.consequences,
            "priority": self.priority,
            "enabled": self.enabled,
            "is_builtin": self.is_builtin,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleTemplate":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=RuleType(data.get("type", "debate")),
            description=data.get("description", ""),
            triggers=data.get("triggers", []),
            constraints=data.get("constraints", []),
            consequences=data.get("consequences", []),
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            is_builtin=data.get("is_builtin", False)
        )
```

## 七、JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Rule",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "规则唯一标识"
    },
    "name": {
      "type": "string",
      "description": "规则名称"
    },
    "type": {
      "type": "string",
      "enum": ["debate", "game", "moderation", "custom"],
      "description": "规则类型"
    },
    "description": {
      "type": "string",
      "description": "规则描述"
    },
    "triggers": {
      "type": "array",
      "description": "触发器列表",
      "items": {
        "type": "object",
        "properties": {
          "event_type": {"type": "string"},
          "condition": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    },
    "constraints": {
      "type": "array",
      "description": "约束条件列表",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "target": {"type": "string"},
          "condition": {"type": "string"},
          "error_message": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    },
    "consequences": {
      "type": "array",
      "description": "结果动作列表",
      "items": {
        "type": "object",
        "properties": {
          "action": {"type": "string"},
          "params": {"type": "object"}
        }
      }
    },
    "priority": {
      "type": "integer",
      "description": "优先级"
    },
    "enabled": {
      "type": "boolean",
      "description": "是否启用"
    }
  }
}
```

## 八、使用示例

### 8.1 创建发言长度限制规则

```python
rule = Rule(
    id="rule_001",
    name="发言长度限制",
    description="限制每次发言不超过500字",
    triggers=[
        Trigger(
            event_type="message.received",
            condition="true"
        )
    ],
    constraints=[
        Constraint(
            type="message_length",
            target="participant",
            condition="len <= 500",
            error_message="发言不能超过500字"
        )
    ],
    consequences=[
        Consequence(
            action="broadcast",
            params={"message": "警告：发言超过限制"}
        )
    ]
)
```

### 8.2 创建禁止关键词规则

```python
rule = Rule(
    id="rule_002",
    name="文明用语规则",
    description="禁止使用不文明用语",
    triggers=[
        Trigger(
            event_type="message.received",
            condition="true"
        )
    ],
    constraints=[
        Constraint(
            type="keyword",
            target="participant",
            params={"keywords": ["脏话", "骂人"]},
            error_message="请使用文明用语"
        )
    ],
    consequences=[
        Consequence(
            action="warn",
            params={"message": "请注意文明用语"}
        )
    ]
)
```
