"""Helper utilities."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def timestamp_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO string to datetime."""
    return datetime.fromisoformat(ts)
