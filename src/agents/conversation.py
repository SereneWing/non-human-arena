"""
对话管理模块
管理对话会话和消息历史
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from .agent import Agent
from ..llm.adapter import ChatMessage


@dataclass
class Message:
    """对话消息"""
    id: str
    agent_id: str
    agent_name: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_user: bool = False  # 是否是用户消息
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "is_user": self.is_user
        }


@dataclass
class Conversation:
    """对话会话"""
    id: str
    agent1: Agent
    agent2: Agent
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_auto_mode: bool = False
    current_turn: str = "agent1"  # agent1 或 agent2
    
    def add_message(self, message: Message) -> None:
        """添加消息"""
        self.messages.append(message)
    
    def get_context_messages(self, max_history: int = 10) -> List[ChatMessage]:
        """获取上下文消息（用于LLM调用）"""
        recent_messages = self.messages[-max_history:] if len(self.messages) > max_history else self.messages
        
        result = []
        for msg in recent_messages:
            role = "user" if msg.is_user else "assistant"
            result.append(ChatMessage(role=role, content=f"[{msg.agent_name}]: {msg.content}"))
        
        return result
    
    def build_prompt(self, speaker: Agent, other: Agent) -> str:
        """构建对话提示词"""
        context = self.get_context_messages()
        
        prompt_parts = [
            f"你是 {speaker.name}，你的对手是 {other.name}。",
            f"你的性格是：{speaker.personality}",
            "",
            "对话历史："
        ]
        
        if context:
            for msg in context:
                prompt_parts.append(msg.content)
        else:
            prompt_parts.append("（暂无历史对话）")
        
        prompt_parts.extend([
            "",
            f"请以 {speaker.name} 的身份，根据你的性格特点，针对以上对话继续发表你的观点。",
            "注意：要简洁、有观点、有个性。"
        ])
        
        return "\n".join(prompt_parts)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent1": self.agent1.to_dict(),
            "agent2": self.agent2.to_dict(),
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "is_auto_mode": self.is_auto_mode,
            "current_turn": self.current_turn
        }


class ConversationManager:
    """对话管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._conversations: Dict[str, Conversation] = {}
    
    def create_conversation(self, agent1: Agent, agent2: Agent) -> Conversation:
        """创建新对话"""
        import uuid
        conv_id = str(uuid.uuid4())[:8]
        conversation = Conversation(
            id=conv_id,
            agent1=agent1,
            agent2=agent2
        )
        self._conversations[conv_id] = conversation
        return conversation
    
    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """获取对话"""
        return self._conversations.get(conv_id)
    
    def delete_conversation(self, conv_id: str) -> bool:
        """删除对话"""
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            return True
        return False
    
    def list_conversations(self) -> List[dict]:
        """列出所有对话（摘要）"""
        return [
            {
                "id": conv.id,
                "agent1_name": conv.agent1.name,
                "agent2_name": conv.agent2.name,
                "message_count": len(conv.messages),
                "created_at": conv.created_at.isoformat()
            }
            for conv in self._conversations.values()
        ]


# 全局对话管理器实例
conversation_manager = ConversationManager()
