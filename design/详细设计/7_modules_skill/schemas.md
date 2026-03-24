# Skill 模块数据结构

## 一、技能相关数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class SkillType(Enum):
    """技能类型"""
    SPEECH = "speech"              # 发言技能
    LOGIC = "logic"               # 逻辑技能
    EMOTION = "emotion"           # 情感技能
    MEMORY = "memory"             # 记忆技能
    RESEARCH = "research"          # 研究技能

class SkillTrigger(Enum):
    """触发方式"""
    AUTO = "auto"                 # 自动触发
    MANUAL = "manual"             # 手动触发
    CONDITION = "condition"       # 条件触发
    EVENT = "event"               # 事件触发

@dataclass
class Skill:
    """技能"""
    id: str
    name: str
    description: str
    skill_type: SkillType
    trigger: SkillTrigger
    config: Dict[str, Any] = field(default_factory=dict)
    prompt_template: str = ""
    enabled: bool = True
    priority: int = 0
    cooldown: float = 0.0         # 冷却时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SkillInstance:
    """技能实例"""
    skill: Skill
    participant_id: str
    session_id: str
    last_used: Optional[datetime] = None
    use_count: int = 0
    is_active: bool = True
    
    def can_use(self) -> bool:
        """检查是否可以触发"""
        if not self.is_active or not self.skill.enabled:
            return False
        
        if self.skill.cooldown > 0 and self.last_used:
            elapsed = (datetime.now() - self.last_used).total_seconds()
            return elapsed >= self.skill.cooldown
        
        return True
    
    def use(self) -> None:
        """使用技能"""
        self.last_used = datetime.now()
        self.use_count += 1

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    skill_id: str
    output: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None
```

## 二、技能触发条件

```python
@dataclass
class SkillCondition:
    """技能触发条件"""
    condition_type: str            # 条件类型: "message_contains", "turn_count", etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    probability: float = 1.0       # 触发概率

@dataclass
class SkillEvent:
    """技能事件配置"""
    event_type: str               # 监听的事件类型
    filter: Optional[Dict[str, Any]] = None  # 事件过滤条件
```

## 三、技能效果

```python
@dataclass
class SkillEffect:
    """技能效果"""
    effect_type: str              # 效果类型
    parameters: Dict[str, Any] = field(default_factory=dict)

class EffectType:
    """效果类型常量"""
    MODIFY_RESPONSE = "modify_response"       # 修改响应
    ADD_CONTEXT = "add_context"               # 添加上下文
    APPLY_BUFF = "apply_buff"               # 应用增益
    APPLY_DEBUFF = "apply_debuff"           # 应用减益
    TRIGGER_ACTION = "trigger_action"        # 触发动作
    SEND_MESSAGE = "send_message"           # 发送消息
