"""Session state machine implementation."""
from __future__ import annotations

from typing import Dict, List, Optional

from modules.session.models.session import SessionState


class SessionStateMachine:
    """Session state machine for managing session lifecycle."""
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[SessionState, List[SessionState]] = {
        SessionState.CREATED: [SessionState.INITIALIZING],
        SessionState.INITIALIZING: [SessionState.WAITING, SessionState.ERROR],
        SessionState.WAITING: [SessionState.RUNNING, SessionState.CANCELLED],
        SessionState.RUNNING: [SessionState.PAUSED, SessionState.ENDING, SessionState.ERROR],
        SessionState.PAUSED: [SessionState.RUNNING, SessionState.CANCELLED],
        SessionState.ENDING: [SessionState.COMPLETED, SessionState.CANCELLED],
        SessionState.ERROR: [SessionState.WAITING, SessionState.CANCELLED],
        SessionState.COMPLETED: [],  # Terminal state
        SessionState.CANCELLED: [],  # Terminal state
    }
    
    # Terminal states
    TERMINAL_STATES: List[SessionState] = [
        SessionState.COMPLETED,
        SessionState.CANCELLED,
    ]
    
    def can_transition(
        self,
        from_state: SessionState,
        to_state: SessionState,
    ) -> bool:
        """Check if transition is valid."""
        valid_targets = self.VALID_TRANSITIONS.get(from_state, [])
        return to_state in valid_targets
    
    def get_next_states(self, from_state: SessionState) -> List[SessionState]:
        """Get valid next states."""
        return self.VALID_TRANSITIONS.get(from_state, [])
    
    def is_terminal(self, state: SessionState) -> bool:
        """Check if state is terminal."""
        return state in self.TERMINAL_STATES
    
    def is_valid_state(self, state: SessionState) -> bool:
        """Check if state is valid."""
        return state in SessionState
    
    def get_transition_error_message(
        self,
        from_state: SessionState,
        to_state: SessionState,
    ) -> str:
        """Get error message for invalid transition."""
        valid_states = self.get_next_states(from_state)
        if not valid_states:
            return f"Cannot transition from terminal state {from_state.value}"
        return (
            f"Cannot transition from {from_state.value} to {to_state.value}. "
            f"Valid transitions: {[s.value for s in valid_states]}"
        )
    
    def validate_transition(
        self,
        from_state: SessionState,
        to_state: SessionState,
    ) -> tuple[bool, Optional[str]]:
        """Validate transition and return error message if invalid."""
        if not self.can_transition(from_state, to_state):
            error_msg = self.get_transition_error_message(from_state, to_state)
            return False, error_msg
        return True, None
