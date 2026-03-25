"""
AI角色模块
定义AI角色的数据结构
"""

from dataclasses import dataclass, field
from typing import List
from ..llm.adapter import ChatMessage


@dataclass
class Agent:
    """AI角色"""
    id: str
    name: str
    personality: str  # 性格描述
    description: str = ""  # 详细描述
    avatar: str = ""  # 头像（可选）
    
    def get_system_prompt(self) -> str:
        """生成系统提示词"""
        return f"""你是 {self.name}，一个具有以下性格特点的角色：

{self.personality}

{self.description}

请用符合你性格的方式与其他角色对话。"""
    
    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        """从字典创建Agent"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            personality=data.get("personality", ""),
            description=data.get("description", ""),
            avatar=data.get("avatar", "")
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "personality": self.personality,
            "description": self.description,
            "avatar": self.avatar
        }
