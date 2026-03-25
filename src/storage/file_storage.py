"""
文件存储模块
负责将对话历史保存到txt文件
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from ..agents.conversation import Conversation, Message


class FileStorage:
    """文件存储管理器"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.conversations_dir = self.storage_dir / "conversations"
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    def save_conversation(self, conversation: Conversation) -> str:
        """保存对话到文件"""
        filepath = self.conversations_dir / f"{conversation.id}.txt"
        
        lines = [
            "=" * 50,
            f"对话记录 - {conversation.id}",
            f"创建时间: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50,
            "",
            f"角色1: {conversation.agent1.name}",
            f"  性格: {conversation.agent1.personality}",
            f"  描述: {conversation.agent1.description}",
            "",
            f"角色2: {conversation.agent2.name}",
            f"  性格: {conversation.agent2.personality}",
            f"  描述: {conversation.agent2.description}",
            "",
            "=" * 50,
            "对话内容",
            "=" * 50,
            ""
        ]
        
        for msg in conversation.messages:
            time_str = msg.timestamp.strftime('%H:%M:%S')
            speaker = "用户" if msg.is_user else msg.agent_name
            lines.append(f"[{time_str}] {speaker}: {msg.content}")
        
        lines.extend([
            "",
            "=" * 50,
            f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 50
        ])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)
    
    def load_conversation(self, conv_id: str) -> Optional[str]:
        """加载对话文件"""
        filepath = self.conversations_dir / f"{conv_id}.txt"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def list_conversations(self) -> List[dict]:
        """列出所有对话文件"""
        result = []
        for filepath in self.conversations_dir.glob("*.txt"):
            stat = filepath.stat()
            result.append({
                "id": filepath.stem,
                "filename": filepath.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return sorted(result, key=lambda x: x["modified"], reverse=True)
    
    def delete_conversation(self, conv_id: str) -> bool:
        """删除对话文件"""
        filepath = self.conversations_dir / f"{conv_id}.txt"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def append_to_conversation(self, conversation: Conversation) -> None:
        """追加消息到对话文件"""
        filepath = self.conversations_dir / f"{conversation.id}.txt"
        
        if not filepath.exists():
            # 如果文件不存在，先创建
            self.save_conversation(conversation)
            return
        
        # 追加最后一条消息
        if conversation.messages:
            last_msg = conversation.messages[-1]
            time_str = last_msg.timestamp.strftime('%H:%M:%S')
            speaker = "用户" if last_msg.is_user else last_msg.agent_name
            line = f"\n[{time_str}] {speaker}: {last_msg.content}"
            
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(line)
