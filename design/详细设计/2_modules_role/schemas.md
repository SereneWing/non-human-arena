# 角色模块数据结构

## 一、角色数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class RoleCategory(Enum):
    """角色类别"""
    DEBATER = "debater"           # 辩手
    MEDIATOR = "mediator"         # 调解员
    NARRATOR = "narrator"         # 旁白
    JUDGE = "judge"               # 裁判
    PLAYER = "player"             # 游戏玩家
    TEACHER = "teacher"           # 老师
    STUDENT = "student"           # 学生
    CUSTOM = "custom"             # 自定义

@dataclass
class Role:
    """角色"""
    id: str
    name: str
    category: RoleCategory
    description: str = ""
    avatar: Optional[str] = None
    base_personality: Dict[str, float] = field(default_factory=dict)  # 0.0-1.0
    system_prompt: str = ""
    mental_config: Optional["MentalConfig"] = None
    emotional_model: Optional["EmotionalModel"] = None
    speaking_style: Optional["SpeakingStyle"] = None
    skills: List[str] = field(default_factory=list)  # 技能ID列表
    parameters: Dict[str, Any] = field(default_factory=dict)  # LLM参数
    variables: Dict[str, Any] = field(default_factory=dict)  # 模板变量
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """从字典创建"""
        ...
```

## 二、心理配置

```python
@dataclass
class MentalConfig:
    """心理配置"""
    enable_mental_activity: bool = True      # 是否启用心理活动
    skip_probability: float = 0.1            # 跳过发言概率
    mental_activity_visibility: float = 0.3   # 心理活动可见度
    max_activities: int = 50                 # 最大存储心理活动数
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MentalConfig":
        ...
```

## 三、情绪模型

```python
@dataclass
class EmotionalModel:
    """情绪模型"""
    dimensions: List[str] = field(default_factory=list)  # 情绪维度
    initial_emotion: str = "neutral"                    # 初始情绪
    max_intensity: float = 1.0                          # 最大强度
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalModel":
        ...
```

## 四、发言风格

```python
@dataclass
class SpeakingStyle:
    """发言风格"""
    formality: float = 0.5           # 正式程度 0.0-1.0
    length_preference: str = "medium"  # short/medium/long
    tone: str = "neutral"            # 语气
    vocabulary_level: str = "normal"  # simple/normal/sophisticated
    use_emoji: bool = False          # 是否使用表情
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpeakingStyle":
        ...
```

## 五、角色模板

```python
@dataclass
class RoleTemplate:
    """角色模板"""
    id: str
    name: str
    category: RoleCategory
    description: str = ""
    base_role: Role = None           # 基础角色定义
    variable_fields: List[str] = field(default_factory=list)  # 可变字段
    fixed_fields: List[str] = field(default_factory=list)      # 固定字段
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleTemplate":
        ...
```

## 六、数据验证

```python
class RoleValidator:
    """角色数据验证器"""
    
    @staticmethod
    def validate_personality(personality: Dict[str, float]) -> List[str]:
        """验证性格特征"""
        errors = []
        for trait, value in personality.items():
            if not isinstance(value, (int, float)):
                errors.append(f"性格特征 '{trait}' 必须是数字")
            elif not 0 <= value <= 1:
                errors.append(f"性格特征 '{trait}' 必须在 0-1 范围内")
        return errors
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any]) -> List[str]:
        """验证LLM参数"""
        errors = []
        if "temperature" in params:
            if not 0 <= params["temperature"] <= 2:
                errors.append("temperature 必须在 0-2 范围内")
        if "max_tokens" in params:
            if params["max_tokens"] <= 0:
                errors.append("max_tokens 必须大于 0")
        return errors
    
    @classmethod
    def validate(cls, role_data: Dict[str, Any]) -> List[str]:
        """验证完整角色数据"""
        errors = []
        
        if not role_data.get("name"):
            errors.append("角色名称不能为空")
        
        errors.extend(cls.validate_personality(
            role_data.get("base_personality", {})
        ))
        
        errors.extend(cls.validate_parameters(
            role_data.get("parameters", {})
        ))
        
        return errors
```
