# 角色定义 (Role)

## 一、概述

Role是系统中AI角色的核心数据结构，定义了角色的基本属性、性格、心理配置和发言风格。

## 二、数据结构

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class RoleCategory(Enum):
    """角色类别"""
    DEBATER = "debater"              # 辩手
    MODERATOR = "moderator"          # 主持人/裁判
    GAME_ROLE = "game_role"          # 游戏角色
    TEACHER = "teacher"              # 老师
    CUSTOM = "custom"                # 自定义


@dataclass
class Role:
    """
    AI角色定义
    
    Attributes:
        id: 角色唯一标识
        name: 角色名称
        category: 角色类别
        description: 角色描述
        avatar: 头像URL
        base_personality: 基础性格特征
        system_prompt: 系统提示词
        mental_config: 心理配置
        emotional_model: 情绪模型
        speaking_style: 发言风格
        skills: 技能列表
        parameters: LLM参数配置
        variables: 模板变量
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    # 必需字段
    id: str
    name: str
    category: RoleCategory = RoleCategory.DEBATER
    description: str = ""
    
    # 可选字段
    avatar: Optional[str] = None
    
    # 性格和行为
    base_personality: Dict[str, float] = field(default_factory=lambda: {
        "logical": 0.5,
        "emotional": 0.5,
        "aggressive": 0.5,
        "cautious": 0.5
    })
    
    # 提示词配置
    system_prompt: str = ""
    
    # 心理和情绪配置
    mental_config: Optional["MentalConfig"] = None
    emotional_model: Optional["EmotionalModel"] = None
    
    # 发言风格
    speaking_style: Optional["SpeakingStyle"] = None
    
    # 技能配置
    skills: List[str] = field(default_factory=list)
    
    # LLM参数
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9
    })
    
    # 模板变量
    variables: Dict[str, str] = field(default_factory=dict)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """后置初始化"""
        # 转换枚举
        if isinstance(self.category, str):
            self.category = RoleCategory(self.category)
        
        # 更新时间戳
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value if isinstance(self.category, RoleCategory) else self.category,
            "description": self.description,
            "avatar": self.avatar,
            "base_personality": self.base_personality,
            "system_prompt": self.system_prompt,
            "mental_config": self.mental_config.to_dict() if self.mental_config else None,
            "emotional_model": self.emotional_model.to_dict() if self.emotional_model else None,
            "speaking_style": self.speaking_style.to_dict() if self.speaking_style else None,
            "skills": self.skills,
            "parameters": self.parameters,
            "variables": self.variables,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            category=data.get("category", "debater"),
            description=data.get("description", ""),
            avatar=data.get("avatar"),
            base_personality=data.get("base_personality", {}),
            system_prompt=data.get("system_prompt", ""),
            mental_config=MentalConfig.from_dict(data["mental_config"]) if data.get("mental_config") else None,
            emotional_model=EmotionalModel.from_dict(data["emotional_model"]) if data.get("emotional_model") else None,
            speaking_style=SpeakingStyle.from_dict(data["speaking_style"]) if data.get("speaking_style") else None,
            skills=data.get("skills", []),
            parameters=data.get("parameters", {}),
            variables=data.get("variables", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
```

## 三、JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Role",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "角色唯一标识"
    },
    "name": {
      "type": "string",
      "description": "角色名称"
    },
    "category": {
      "type": "string",
      "enum": ["debater", "moderator", "game_role", "teacher", "custom"],
      "description": "角色类别"
    },
    "description": {
      "type": "string",
      "description": "角色描述"
    },
    "avatar": {
      "type": "string",
      "format": "uri",
      "description": "头像URL"
    },
    "base_personality": {
      "type": "object",
      "description": "基础性格特征",
      "properties": {
        "logical": {"type": "number", "minimum": 0, "maximum": 1},
        "emotional": {"type": "number", "minimum": 0, "maximum": 1},
        "aggressive": {"type": "number", "minimum": 0, "maximum": 1},
        "cautious": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "system_prompt": {
      "type": "string",
      "description": "系统提示词"
    },
    "mental_config": {
      "$ref": "#/definitions/MentalConfig"
    },
    "emotional_model": {
      "$ref": "#/definitions/EmotionalModel"
    },
    "speaking_style": {
      "$ref": "#/definitions/SpeakingStyle"
    },
    "skills": {
      "type": "array",
      "items": {"type": "string"},
      "description": "技能列表"
    },
    "parameters": {
      "type": "object",
      "description": "LLM参数配置"
    },
    "variables": {
      "type": "object",
      "description": "模板变量"
    }
  }
}
```

## 四、使用示例

### 4.1 创建正方辩手
```python
role = Role(
    id="advocate_001",
    name="正方辩手",
    category=RoleCategory.DEBATER,
    description="逻辑严谨、善于论证的正方辩手",
    base_personality={
        "logical": 0.9,
        "emotional": 0.3,
        "aggressive": 0.6,
        "cautious": 0.4
    },
    system_prompt="你是一位逻辑严谨的正方辩手...",
    skills=["counter_argument", "logic_refinement"],
    parameters={
        "temperature": 0.7,
        "max_tokens": 800
    }
)
```

### 4.2 创建狼人角色
```python
role = Role(
    id="werewolf_001",
    name="狼人",
    category=RoleCategory.GAME_ROLE,
    description="隐藏在村民中的狼人",
    base_personality={
        "logical": 0.8,
        "emotional": 0.6,
        "aggressive": 0.7,
        "cautious": 0.9
    },
    mental_config=MentalConfig(
        skip_probability=0.4,
        enable_mental_activity=True,
        mental_activity_visibility=0.1  # 心理活动几乎不对外显示
    ),
    skills=["deception", "strategic_silence"]
)
```

### 4.3 从模板创建
```python
from app.modules.role.templates import BuiltinRoleTemplates

# 基于模板创建
role = Role.from_dict(BuiltinRoleTemplates.ADVOCATE)
role.id = "my_advocate"
role.name = "我的正方辩手"
```

## 五、字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 唯一标识，支持UUID |
| name | string | 是 | 角色显示名称 |
| category | enum | 否 | 角色类别 |
| description | string | 否 | 角色描述 |
| avatar | string | 否 | 头像URL |
| base_personality | object | 否 | 性格特征（0-1） |
| system_prompt | string | 否 | 系统提示词 |
| mental_config | object | 否 | 心理配置 |
| emotional_model | object | 否 | 情绪模型 |
| speaking_style | object | 否 | 发言风格 |
| skills | array | 否 | 技能ID列表 |
| parameters | object | 否 | LLM调用参数 |
| variables | object | 否 | 模板变量 |
| created_at | datetime | 否 | 创建时间 |
| updated_at | datetime | 否 | 更新时间 |
