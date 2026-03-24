# 模板模块数据结构

## 一、模板类型

```python
from enum import Enum

class TemplateType(Enum):
    """模板类型"""
    SESSION = "session"           # 会话模板
    ROLE = "role"                 # 角色模板
    RULE = "rule"                 # 规则模板
    PROMPT = "prompt"             # 提示词模板
    SCENE = "scene"               # 场景模板

class TemplateFormat(Enum):
    """模板格式"""
    MARKDOWN = "markdown"         # Markdown格式
    JINJA2 = "jinja2"             # Jinja2模板
    JSON = "json"                 # JSON格式
    YAML = "yaml"                 # YAML格式
```

## 二、模板数据模型

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

@dataclass
class Template:
    """模板"""
    id: str
    name: str
    type: TemplateType
    content: str
    description: str = ""
    version: str = "1.0"
    variables: List[str] = field(default_factory=list)  # 变量列表
    default_values: Dict[str, Any] = field(default_factory=dict)  # 默认值
    format: TemplateFormat = TemplateFormat.JINJA2
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "content": self.content,
            "description": self.description,
            "version": self.version,
            "variables": self.variables,
            "default_values": self.default_values,
            "format": self.format.value,
            "category": self.category,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=TemplateType(data["type"]),
            content=data["content"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            variables=data.get("variables", []),
            default_values=data.get("default_values", {}),
            format=TemplateFormat(data.get("format", "jinja2")),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            created_by=data.get("created_by")
        )

@dataclass
class TemplateVariable:
    """模板变量"""
    name: str
    type: str = "string"           # string, number, boolean, array, object
    description: str = ""
    required: bool = True
    default: Any = None
    options: List[Any] = field(default_factory=list)  # 可选值
    validation: Optional[str] = None  # 正则表达式
    
    def to_dict(self) -> Dict[str, Any]:
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateVariable":
        ...
```

## 三、模板渲染结果

```python
@dataclass
class RenderResult:
    """渲染结果"""
    success: bool
    content: str
    rendered_variables: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "rendered_variables": self.rendered_variables,
            "errors": self.errors,
            "warnings": self.warnings
        }

@dataclass
class TemplateMetadata:
    """模板元数据"""
    author: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    rating: float = 0.0
    downloads: int = 0
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        ...
```
