"""Event handlers registration."""
from __future__ import annotations

import logging

from core.event_bus import EventBus, get_event_bus
from events.base import (
    RoleCreatedEvent,
    RoleUpdatedEvent,
    RoleDeletedEvent,
    SessionCreatedEvent,
    SessionStartedEvent,
    SessionEndedEvent,
)

logger = logging.getLogger(__name__)


async def on_role_created(event: RoleCreatedEvent) -> None:
    """Handle role created event."""
    logger.info(f"Role created: {event.name} (id: {event.role_id})")


async def on_role_updated(event: RoleUpdatedEvent) -> None:
    """Handle role updated event."""
    logger.info(f"Role updated: {event.name} (id: {event.role_id})")
    logger.debug(f"Changes: {event.changes}")


async def on_role_deleted(event: RoleDeletedEvent) -> None:
    """Handle role deleted event."""
    logger.info(f"Role deleted: {event.name} (id: {event.role_id})")


async def on_session_created(event: SessionCreatedEvent) -> None:
    """Handle session created event."""
    logger.info(f"Session created: {event.name} (id: {event.session_id})")
    logger.debug(f"Topic: {event.topic}, Participants: {event.participant_ids}")


async def on_session_started(event: SessionStartedEvent) -> None:
    """Handle session started event."""
    logger.info(f"Session started: {event.session_id}")


async def on_session_ended(event: SessionEndedEvent) -> None:
    """Handle session ended event."""
    logger.info(f"Session ended: {event.session_id}, reason: {event.reason}")


def register_handlers(event_bus: EventBus) -> None:
    """Register all event handlers."""
    event_bus.subscribe(
        RoleCreatedEvent,
        on_role_created,
        subscriber_name="role_handler",
    )
    event_bus.subscribe(
        RoleUpdatedEvent,
        on_role_updated,
        subscriber_name="role_handler",
    )
    event_bus.subscribe(
        RoleDeletedEvent,
        on_role_deleted,
        subscriber_name="role_handler",
    )
    event_bus.subscribe(
        SessionCreatedEvent,
        on_session_created,
        subscriber_name="session_handler",
    )
    event_bus.subscribe(
        SessionStartedEvent,
        on_session_started,
        subscriber_name="session_handler",
    )
    event_bus.subscribe(
        SessionEndedEvent,
        on_session_ended,
        subscriber_name="session_handler",
    )
    logger.info("Event handlers registered")
