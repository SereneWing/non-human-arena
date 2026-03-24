# 历史模块服务层

## 一、历史服务接口

```python
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime

class IHistoryService(Protocol):
    """历史服务接口"""
    
    async def save_session(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存会话历史"""
        ...
    
    async def get_session_history(
        self,
        session_id: str
    ) -> Optional["SessionHistory"]:
        """获取会话历史"""
        ...
    
    async def export_history(
        self,
        session_id: str,
        config: ExportConfig
    ) -> str:
        """导出历史"""
        ...
    
    async def list_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List["SessionHistory"]:
        """列出会话历史"""
        ...
    
    async def delete_session_history(
        self,
        session_id: str
    ) -> bool:
        """删除会话历史"""
        ...
    
    async def get_stats(
        self,
        user_id: Optional[str] = None
    ) -> HistoryStats:
        """获取统计信息"""
        ...

class IHistoryExporter(Protocol):
    """历史导出器接口"""
    
    def export(
        self,
        history: SessionHistory,
        config: ExportConfig
    ) -> str:
        """导出历史"""
        ...
```

## 二、历史服务实现

```python
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

class HistoryService:
    """历史服务"""
    
    def __init__(
        self,
        repository: IHistoryRepository,
        exporters: Dict[ExportFormat, IHistoryExporter]
    ):
        self.repository = repository
        self.exporters = exporters
    
    async def save_session(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存会话历史"""
        # 构建历史记录
        history = SessionHistory(
            id=generate_id(),
            session_id=session_id,
            session_name=metadata.get("name", "未命名会话") if metadata else "未命名会话",
            messages=[
                MessageRecord(
                    id=msg.get("id", generate_id()),
                    session_id=session_id,
                    participant_id=msg.get("participant_id", ""),
                    participant_name=msg.get("participant_name", ""),
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    type=msg.get("type", "text"),
                    mental_activity=msg.get("mental_activity"),
                    timestamp=datetime.fromisoformat(msg["timestamp"]) if "timestamp" in msg else datetime.now(),
                    metadata=msg.get("metadata", {})
                )
                for msg in messages
            ],
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return await self.repository.save(history)
    
    async def get_session_history(
        self,
        session_id: str
    ) -> Optional[SessionHistory]:
        """获取会话历史"""
        return await self.repository.get_by_session_id(session_id)
    
    async def export_history(
        self,
        session_id: str,
        config: ExportConfig
    ) -> str:
        """导出历史"""
        history = await self.repository.get_by_session_id(session_id)
        if not history:
            raise ValueError(f"会话历史不存在: {session_id}")
        
        exporter = self.exporters.get(config.format)
        if not exporter:
            raise ValueError(f"不支持的导出格式: {config.format}")
        
        return exporter.export(history, config)
    
    async def list_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[SessionHistory]:
        """列出会话历史"""
        return await self.repository.list(skip=skip, limit=limit, user_id=user_id)
    
    async def delete_session_history(self, session_id: str) -> bool:
        """删除会话历史"""
        return await self.repository.delete_by_session_id(session_id)
    
    async def get_stats(self, user_id: Optional[str] = None) -> HistoryStats:
        """获取统计信息"""
        sessions = await self.repository.list(user_id=user_id, limit=1000)
        
        total_messages = sum(len(s.messages) for s in sessions)
        total_turns = sum(len(s.turns) for s in sessions)
        
        # 统计标签
        tag_counts: Dict[str, int] = {}
        for session in sessions:
            for tag in session.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        popular_tags = [
            {"tag": tag, "count": count}
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return HistoryStats(
            total_sessions=len(sessions),
            total_messages=total_messages,
            total_turns=total_turns,
            avg_messages_per_session=total_messages / len(sessions) if sessions else 0,
            avg_turns_per_session=total_turns / len(sessions) if sessions else 0,
            popular_tags=popular_tags
        )
```

## 三、导出器实现

```python
import json
from typing import Dict, Any
from datetime import datetime

class JSONExporter:
    """JSON导出器"""
    
    def export(self, history: SessionHistory, config: ExportConfig) -> str:
        """导出为JSON"""
        data = {
            "id": history.id,
            "session_id": history.session_id,
            "session_name": history.session_name,
            "messages": [
                self._format_message(msg, config)
                for msg in history.messages[:config.max_messages or len(history.messages)]
            ],
            "summary": history.summary,
            "tags": history.tags,
            "created_at": history.created_at.isoformat(),
            "updated_at": history.updated_at.isoformat()
        }
        
        if config.include_metadata:
            data["metadata"] = history.metadata
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_message(self, msg: MessageRecord, config: ExportConfig) -> Dict[str, Any]:
        """格式化消息"""
        result = {}
        
        if config.include_participants:
            result["participant"] = msg.participant_name
            result["role"] = msg.role
        
        result["content"] = msg.content
        
        if config.include_mental_activity and msg.mental_activity:
            result["mental_activity"] = msg.mental_activity
        
        if config.include_timestamps:
            result["timestamp"] = msg.timestamp.isoformat()
        
        if config.include_metadata and msg.metadata:
            result["metadata"] = msg.metadata
        
        return result


class MarkdownExporter:
    """Markdown导出器"""
    
    def export(self, history: SessionHistory, config: ExportConfig) -> str:
        """导出为Markdown"""
        lines = [
            f"# {history.session_name}",
            "",
            f"**会话ID**: {history.session_id}",
            f"**创建时间**: {history.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if history.tags:
            lines.append(f"**标签**: {', '.join(history.tags)}")
            lines.append("")
        
        if history.summary:
            lines.append(f"## 摘要")
            lines.append(history.summary)
            lines.append("")
        
        lines.append("## 对话记录")
        lines.append("")
        
        for msg in history.messages[:config.max_messages or len(history.messages)]:
            lines.append(self._format_message(msg, config))
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_message(self, msg: MessageRecord, config: ExportConfig) -> str:
        """格式化消息"""
        parts = []
        
        if config.include_participants:
            parts.append(f"**{msg.participant_name}**")
        
        if config.include_timestamps:
            parts.append(f"`{msg.timestamp.strftime('%H:%M:%S')}`")
        
        lines = [" ".join(parts)]
        
        if msg.mental_activity and config.include_mental_activity:
            lines.append(f"> 💭 {msg.mental_activity}")
        
        lines.append(msg.content)
        
        return "\n".join(lines)


class HTMLExporter:
    """HTML导出器"""
    
    def export(self, history: SessionHistory, config: ExportConfig) -> str:
        """导出为HTML"""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{history.session_name}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            ".message { margin-bottom: 20px; padding: 10px; border-radius: 8px; }",
            ".user { background-color: #e6f7ff; }",
            ".assistant { background-color: #f5f5f5; }",
            ".system { background-color: #fff7e6; text-align: center; }",
            ".mental { font-style: italic; color: #666; }",
            ".timestamp { font-size: 0.8em; color: #999; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{history.session_name}</h1>",
            f"<p><strong>会话ID</strong>: {history.session_id}</p>",
            f"<p><strong>创建时间</strong>: {history.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]
        
        for msg in history.messages[:config.max_messages or len(history.messages)]:
            html_parts.append(self._format_message(msg, config))
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _format_message(self, msg: MessageRecord, config: ExportConfig) -> str:
        """格式化消息"""
        role_class = msg.role.lower()
        parts = [f'<div class="message {role_class}">']
        
        if config.include_participants:
            parts.append(f'<strong>{msg.participant_name}</strong>')
        
        if config.include_timestamps:
            parts.append(f'<span class="timestamp">{msg.timestamp.strftime("%H:%M:%S")}</span>')
        
        if msg.mental_activity and config.include_mental_activity:
            parts.append(f'<div class="mental">💭 {msg.mental_activity}</div>')
        
        parts.append(f'<div>{msg.content}</div>')
        parts.append('</div>')
        
        return "\n".join(parts)


class HistoryExporterFactory:
    """导出器工厂
    
    说明:
    - JSON, MARKDOWN, HTML: 已实现
    - TEXT, XML: 可选功能，如需支持请实现对应导出器
    """
    
    _exporters: Dict[ExportFormat, IHistoryExporter] = {
        ExportFormat.JSON: JSONExporter(),
        ExportFormat.MARKDOWN: MarkdownExporter(),
        ExportFormat.HTML: HTMLExporter(),
        # ExportFormat.TEXT: TextExporter(),  # 可选：纯文本导出
        # ExportFormat.XML: XMLExporter(),     # 可选：XML导出
    }
    
    @classmethod
    def get_exporter(cls, format: ExportFormat) -> IHistoryExporter:
        """获取导出器"""
        exporter = cls._exporters.get(format)
        if not exporter:
            raise ValueError(f"不支持的导出格式: {format.value}，当前支持的格式: {[f.value for f in cls._exporters.keys()]}")
        return exporter


# ==================== 可选导出器（按需实现） ====================

class TextExporter:
    """纯文本导出器（可选）"""
    
    def export(self, history: SessionHistory, config: ExportConfig) -> str:
        """导出为纯文本"""
        lines = [
            history.session_name,
            "=" * len(history.session_name),
            "",
            f"会话ID: {history.session_id}",
            f"创建时间: {history.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        for msg in history.messages[:config.max_messages or len(history.messages)]:
            lines.append(f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.participant_name}: {msg.content}")
        
        return "\n".join(lines)


class XMLExporter:
    """XML导出器（可选）"""
    
    def export(self, history: SessionHistory, config: ExportConfig) -> str:
        """导出为XML"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<session id="{history.session_id}" name="{self._escape(history.session_name)}">',
            f'  <created_at>{history.created_at.isoformat()}</created_at>',
            '  <messages>'
        ]
        
        for msg in history.messages[:config.max_messages or len(history.messages)]:
            lines.append('    <message>')
            lines.append(f'      <participant>{self._escape(msg.participant_name)}</participant>')
            lines.append(f'      <role>{msg.role}</role>')
            lines.append(f'      <content><![CDATA[{msg.content}]]></content>')
            lines.append(f'      <timestamp>{msg.timestamp.isoformat()}</timestamp>')
            lines.append('    </message>')
        
        lines.extend([
            '  </messages>',
            '</session>'
        ])
        
        return "\n".join(lines)
    
    def _escape(self, text: str) -> str:
        """转义XML特殊字符"""
        return text.replace("&", "&").replace("<", "<").replace(">", ">").replace('"', """)
```
