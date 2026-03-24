"""History service implementation."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from modules.history.models.history import HistoryRecord
from modules.history.schemas import ExportFormat, HistoryExportResponse


class HistoryService:
    """History service implementation."""
    
    async def export_session(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
        format: ExportFormat = ExportFormat.JSON,
    ) -> HistoryExportResponse:
        """Export session history."""
        if format == ExportFormat.JSON:
            content = json.dumps(messages, indent=2, ensure_ascii=False)
        elif format == ExportFormat.MARKDOWN:
            content = self._export_markdown(messages)
        elif format == ExportFormat.HTML:
            content = self._export_html(messages)
        else:
            content = json.dumps(messages, indent=2, ensure_ascii=False)
        
        return HistoryExportResponse(
            session_id=session_id,
            format=format,
            content=content,
            created_at=datetime.now(),
        )
    
    def _export_markdown(self, messages: List[Dict[str, Any]]) -> str:
        """Export to markdown format."""
        lines = ["# Session History\n"]
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            created_at = msg.get("created_at", "")
            
            lines.append(f"## {role}")
            lines.append(f"*({created_at})*\n")
            lines.append(content)
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def _export_html(self, messages: List[Dict[str, Any]]) -> str:
        """Export to HTML format."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>Session History</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            ".message { margin-bottom: 20px; padding: 10px; border-radius: 5px; }",
            ".role { font-weight: bold; }",
            ".timestamp { color: #666; font-size: 0.9em; }",
            ".content { margin-top: 5px; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Session History</h1>",
        ]
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            created_at = msg.get("created_at", "")
            
            html.append(f"<div class='message'>")
            html.append(f"<div class='role'>{role}</div>")
            html.append(f"<div class='timestamp'>{created_at}</div>")
            html.append(f"<div class='content'>{content}</div>")
            html.append(f"</div>")
        
        html.extend(["</body>", "</html>"])
        
        return "\n".join(html)


from datetime import datetime
