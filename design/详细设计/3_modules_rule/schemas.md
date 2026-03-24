# 规则模块数据结构

## 一、规则数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum

class RuleType(Enum):
    """规则类型"""
    DEBATE = "debate"           # 辩论规则
    GAME = "game"               # 游戏规则
    NEGOTIATION = "negotiation" # 谈判规则
    TEACHING = "teaching"       # 教学规则
    ROLEPLAY = "roleplay"       # 角色扮演规则
    CUSTOM = "custom"            # 自定义规则

class ConstraintType(Enum):
    """约束类型"""
    MESSAGE_LENGTH = "message_length"    # 消息长度
    WORD_COUNT = "word_count"          # 词数限制
    KEYWORD_REQUIRED = "keyword_required"  # 必须包含关键词
    KEYWORD_FORBIDDEN = "keyword_forbidden"  # 禁止关键词
    TIMING = "timing"                  # 时机约束
    CUSTOM = "custom"                  # 自定义约束

class TriggerType(Enum):
    """触发器类型"""
    EVENT = "event"               # 事件触发
    CONDITION = "condition"       # 条件触发
    TIMER = "timer"               # 定时触发

class ConsequenceType(Enum):
    """后果类型"""
    SEND_MESSAGE = "send_message"         # 发送消息
    MODIFY_BEHAVIOR = "modify_behavior"   # 修改行为
    APPLY_PENALTY = "apply_penalty"       # 应用惩罚
    END_SESSION = "end_session"           # 结束会话
    SKIP_TURN = "skip_turn"               # 跳过回合
    CUSTOM = "custom"                     # 自定义后果
```

## 二、约束定义

```python
@dataclass
class Constraint:
    """约束条件"""
    id: str
    type: ConstraintType
    target: str = "participant"           # 约束目标
    condition: str = ""                  # 条件表达式
    error_message: str = ""              # 违反时的错误信息
    enabled: bool = True
    priority: int = 0                     # 优先级
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Constraint":
        ...

@dataclass
class ConstraintResult:
    """约束评估结果"""
    satisfied: bool
    violation: Optional[Dict[str, Any]] = None
    constraint_id: Optional[str] = None
```

## 三、触发器定义

```python
@dataclass
class Trigger:
    """触发器"""
    id: str
    type: TriggerType
    event_type: Optional[str] = None      # 事件类型（EVENT类型）
    condition: str = "true"               # 触发条件
    consequence: "Consequence" = None     # 触发的后果
    enabled: bool = True
    cooldown: float = 0                   # 冷却时间（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trigger":
        ...

@dataclass
class TriggerResult:
    """触发器执行结果"""
    trigger: Trigger
    triggered: bool
    event: Optional[Any] = None
    execution_time: Optional[datetime] = None
```

## 四、后果定义

```python
@dataclass
class Consequence:
    """后果定义"""
    id: str
    action: ConsequenceType
    params: Dict[str, Any] = field(default_factory=dict)
    delay: float = 0                      # 延迟执行（秒）
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Consequence":
        ...

@dataclass
class ConsequenceResult:
    """后果执行结果"""
    success: bool
    action: ConsequenceType
    details: Optional[str] = None
    execution_time: Optional[datetime] = None
```

## 五、规则模板

```python
@dataclass
class RuleTemplate:
    """规则模板"""
    id: str
    name: str
    type: RuleType
    description: str = ""
    category: str = "general"
    constraints: List[Constraint] = field(default_factory=list)
    triggers: List[Trigger] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleTemplate":
        ...
    
    def create_runtime_rule(self, session_id: str) -> "Rule":
        """根据模板创建运行时规则"""
        ...

@dataclass
class Rule:
    """运行时规则"""
    id: str
    template_id: str
    session_id: str
    name: str
    constraints: List[Constraint] = field(default_factory=list)
    triggers: List[Trigger] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_template(cls, template: RuleTemplate, session_id: str) -> "Rule":
        """从模板创建"""
        ...
```

## 六、规则检查结果

```python
@dataclass
class RuleCheckResult:
    """规则检查结果"""
    session_id: str
    satisfied_rules: List[Rule] = field(default_factory=list)
    violated_rules: List[Rule] = field(default_factory=list)
    triggered_rules: List[Rule] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "satisfied_count": len(self.satisfied_rules),
            "violated_count": len(self.violated_rules),
            "triggered_count": len(self.triggered_rules),
            "timestamp": self.timestamp.isoformat()
        }
```
