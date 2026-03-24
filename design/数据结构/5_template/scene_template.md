# 场景模板定义 (SceneTemplate)

## 一、概述

SceneTemplate是场景的模板定义，包含完整的场景配置（角色、规则、话题等）。

## 二、数据结构

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

@dataclass
class SceneTemplate:
    """
    场景模板
    
    Attributes:
        id: 模板唯一标识
        name: 模板名称
        description: 模板描述
        category: 模板类别
        topic: 预设话题
        topic_prompts: 话题提示
        role_templates: 角色模板列表
        rule_templates: 规则模板列表
        config: 场景配置
        metadata: 元数据
        is_builtin: 是否内置
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    id: str
    name: str
    description: str = ""
    category: str = "general"
    topic: str = ""
    topic_prompts: List[str] = field(default_factory=list)
    role_templates: List["RoleTemplate"] = field(default_factory=list)
    rule_templates: List["RuleTemplate"] = field(default_factory=list)
    config: "SceneConfig" = field(default_factory=SceneConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_builtin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "topic": self.topic,
            "topic_prompts": self.topic_prompts,
            "role_templates": [r.to_dict() if hasattr(r, "to_dict") else r for r in self.role_templates],
            "rule_templates": [r.to_dict() if hasattr(r, "to_dict") else r for r in self.rule_templates],
            "config": self.config.to_dict() if self.config else {},
            "metadata": self.metadata,
            "is_builtin": self.is_builtin,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneTemplate":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "general"),
            topic=data.get("topic", ""),
            topic_prompts=data.get("topic_prompts", []),
            role_templates=[RoleTemplate.from_dict(r) for r in data.get("role_templates", [])],
            rule_templates=[RuleTemplate.from_dict(r) for r in data.get("rule_templates", [])],
            config=SceneConfig.from_dict(data.get("config", {})) if data.get("config") else SceneConfig(),
            metadata=data.get("metadata", {}),
            is_builtin=data.get("is_builtin", False)
        )
```

## 三、场景配置 (SceneConfig)

```python
@dataclass
class SceneConfig:
    """
    场景配置
    
    Attributes:
        max_participants: 最大参与人数
        min_participants: 最小参与人数
        enable_heartbeat: 是否启用心跳
        heartbeat_interval: 心跳间隔（秒）
        enable_mental_activity: 是否启用心理活动
        max_message_length: 最大消息长度
        turn_order: 发言顺序（sequential, simultaneous, free）
        recording_enabled: 是否启用录制
    """
    
    max_participants: int = 10
    min_participants: int = 2
    enable_heartbeat: bool = True
    heartbeat_interval: float = 10.0
    enable_mental_activity: bool = True
    max_message_length: int = 2000
    turn_order: str = "sequential"  # sequential, simultaneous, free
    recording_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "max_participants": self.max_participants,
            "min_participants": self.min_participants,
            "enable_heartbeat": self.enable_heartbeat,
            "heartbeat_interval": self.heartbeat_interval,
            "enable_mental_activity": self.enable_mental_activity,
            "max_message_length": self.max_message_length,
            "turn_order": self.turn_order,
            "recording_enabled": self.recording_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneConfig":
        """从字典创建"""
        return cls(
            max_participants=data.get("max_participants", 10),
            min_participants=data.get("min_participants", 2),
            enable_heartbeat=data.get("enable_heartbeat", True),
            heartbeat_interval=data.get("heartbeat_interval", 10.0),
            enable_mental_activity=data.get("enable_mental_activity", True),
            max_message_length=data.get("max_message_length", 2000),
            turn_order=data.get("turn_order", "sequential"),
            recording_enabled=data.get("recording_enabled", True)
        )
```

## 四、角色模板 (RoleTemplate)

```python
@dataclass
class RoleTemplate:
    """
    角色模板
    
    Attributes:
        id: 模板唯一标识
        name: 模板名称
        description: 模板描述
        category: 角色类别
        base_personality: 基础性格
        system_prompt: 系统提示词模板
        speaking_style: 发言风格模板
        skills: 技能列表模板
        variables: 模板变量
        is_builtin: 是否内置
    """
    
    id: str
    name: str
    description: str = ""
    category: str = "custom"
    base_personality: Dict[str, float] = field(default_factory=lambda: {
        "logical": 0.5,
        "emotional": 0.5,
        "aggressive": 0.5,
        "cautious": 0.5
    })
    system_prompt: str = ""
    speaking_style: Optional["SpeakingStyleTemplate"] = None
    skills: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    is_builtin: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "base_personality": self.base_personality,
            "system_prompt": self.system_prompt,
            "speaking_style": self.speaking_style.to_dict() if self.speaking_style else None,
            "skills": self.skills,
            "variables": self.variables,
            "is_builtin": self.is_builtin
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleTemplate":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "custom"),
            base_personality=data.get("base_personality", {}),
            system_prompt=data.get("system_prompt", ""),
            speaking_style=SpeakingStyleTemplate.from_dict(data["speaking_style"]) if data.get("speaking_style") else None,
            skills=data.get("skills", []),
            variables=data.get("variables", {}),
            is_builtin=data.get("is_builtin", False)
        )
    
    def apply_variables(self, variables: Dict[str, str]) -> "RoleTemplate":
        """应用变量替换"""
        result = RoleTemplate(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category,
            base_personality=self.base_personality.copy(),
            system_prompt=self._render_string(self.system_prompt, variables),
            speaking_style=self.speaking_style,
            skills=self.skills.copy(),
            variables={**self.variables, **variables},
            is_builtin=self.is_builtin
        )
        return result
    
    def _render_string(self, text: str, variables: Dict[str, str]) -> str:
        """替换模板变量"""
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", value)
        return text


@dataclass
class SpeakingStyleTemplate:
    """发言风格模板"""
    formality: float = 0.5
    length_preference: str = "medium"
    tone: str = "neutral"
    vocabulary: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "formality": self.formality,
            "length_preference": self.length_preference,
            "tone": self.tone,
            "vocabulary": self.vocabulary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpeakingStyleTemplate":
        """从字典创建"""
        return cls(
            formality=data.get("formality", 0.5),
            length_preference=data.get("length_preference", "medium"),
            tone=data.get("tone", "neutral"),
            vocabulary=data.get("vocabulary", [])
        )
```

## 五、内置场景模板

```python
class BuiltinSceneTemplates:
    """内置场景模板"""
    
    STANDARD_DEBATE = SceneTemplate(
        id="scene.standard_debate",
        name="标准辩论",
        description="传统的正反方辩论场景",
        category="debate",
        topic="请设置辩题",
        topic_prompts=[
            "AI是否应该取代人类工作",
            "电子竞技是否应该成为奥运项目",
            "人类是否应该开发人工智能武器"
        ],
        role_templates=[
            RoleTemplate(
                id="role.advocate",
                name="正方辩手",
                description="支持辩题的辩手",
                category="debater",
                base_personality={
                    "logical": 0.8,
                    "emotional": 0.3,
                    "aggressive": 0.6,
                    "cautious": 0.4
                },
                system_prompt="你是一位逻辑严谨的正方辩手。",
                is_builtin=True
            ),
            RoleTemplate(
                id="role.opponent",
                name="反方辩手",
                description="反对辩题的辩手",
                category="debater",
                base_personality={
                    "logical": 0.8,
                    "emotional": 0.3,
                    "aggressive": 0.6,
                    "cautious": 0.4
                },
                system_prompt="你是一位逻辑严谨的反方辩手。",
                is_builtin=True
            )
        ],
        rule_templates=[],
        config=SceneConfig(
            max_participants=2,
            min_participants=2,
            turn_order="sequential"
        ),
        is_builtin=True
    )
    
    WEREWOLF_GAME = SceneTemplate(
        id="scene.werewolf",
        name="狼人杀",
        description="经典的狼人杀游戏场景",
        category="game",
        topic="狼人杀游戏",
        role_templates=[
            RoleTemplate(
                id="role.werewolf",
                name="狼人",
                description="隐藏在村民中的狼人",
                category="game_role",
                base_personality={
                    "logical": 0.8,
                    "emotional": 0.6,
                    "aggressive": 0.7,
                    "cautious": 0.9
                },
                is_builtin=True
            ),
            RoleTemplate(
                id="role.villager",
                name="村民",
                description="普通村民",
                category="game_role",
                base_personality={
                    "logical": 0.5,
                    "emotional": 0.5,
                    "aggressive": 0.3,
                    "cautious": 0.5
                },
                is_builtin=True
            )
        ],
        is_builtin=True
    )
```

## 六、JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SceneTemplate",
  "type": "object",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "模板唯一标识"
    },
    "name": {
      "type": "string",
      "description": "模板名称"
    },
    "description": {
      "type": "string",
      "description": "模板描述"
    },
    "category": {
      "type": "string",
      "description": "模板类别"
    },
    "topic": {
      "type": "string",
      "description": "预设话题"
    },
    "topic_prompts": {
      "type": "array",
      "items": {"type": "string"},
      "description": "话题提示列表"
    },
    "role_templates": {
      "type": "array",
      "items": {"$ref": "#/definitions/RoleTemplate"},
      "description": "角色模板列表"
    },
    "rule_templates": {
      "type": "array",
      "items": {"$ref": "#/definitions/RuleTemplate"},
      "description": "规则模板列表"
    },
    "config": {
      "$ref": "#/definitions/SceneConfig"
    },
    "metadata": {
      "type": "object",
      "description": "元数据"
    },
    "is_builtin": {
      "type": "boolean",
      "description": "是否内置"
    }
  },
  "definitions": {
    "RoleTemplate": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "category": {"type": "string"},
        "base_personality": {"type": "object"},
        "system_prompt": {"type": "string"},
        "skills": {"type": "array", "items": {"type": "string"}},
        "variables": {"type": "object"}
      }
    },
    "RuleTemplate": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "triggers": {"type": "array"},
        "constraints": {"type": "array"},
        "consequences": {"type": "array"}
      }
    },
    "SceneConfig": {
      "type": "object",
      "properties": {
        "max_participants": {"type": "integer"},
        "min_participants": {"type": "integer"},
        "enable_heartbeat": {"type": "boolean"},
        "heartbeat_interval": {"type": "number"},
        "enable_mental_activity": {"type": "boolean"},
        "max_message_length": {"type": "integer"},
        "turn_order": {"type": "string"}
      }
    }
  }
}
```

## 七、使用示例

### 7.1 创建自定义场景

```python
scene = SceneTemplate(
    id="scene.custom_debate",
    name="我的辩论场景",
    description="自定义辩论场景",
    category="debate",
    topic="是否应该发展核电",
    role_templates=[
        RoleTemplate(
            id="role.support",
            name="支持方",
            system_prompt="你支持发展核电。",
            variables={"position": "支持"}
        ),
        RoleTemplate(
            id="role.oppose",
            name="反对方",
            system_prompt="你反对发展核电。",
            variables={"position": "反对"}
        )
    ],
    config=SceneConfig(
        max_participants=2,
        enable_mental_activity=True
    )
)
```

### 7.2 使用内置场景

```python
scene = BuiltinSceneTemplates.STANDARD_DEBATE

# 应用变量
advocate = scene.role_templates[0].apply_variables({
    "topic": "AI是否应该取代人类工作"
})
```
