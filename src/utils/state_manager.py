"""
State Manager - Manages conversation and execution state.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """State for a conversation session."""
    session_id: str
    created_at: datetime
    query_history: list = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateManager:
    """
    Manages state across agent executions.
    
    Provides:
    - Session management
    - Context persistence
    - History tracking
    - State updates
    """
    
    def __init__(self):
        """Initialize state manager."""
        self.sessions: Dict[str, SessionState] = {}
    
    def create_state(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SessionState:
        """
        Create new session state.
        
        Args:
            query: Initial query
            context: Initial context
        
        Returns:
            New SessionState
        """
        session_id = str(uuid.uuid4())
        
        state = SessionState(
            session_id=session_id,
            created_at=datetime.now(),
            query_history=[query],
            context=context or {}
        )
        
        self.sessions[session_id] = state
        logger.info(f"Created session {session_id}")
        
        return state
    
    def load_state(self, session_id: str) -> Optional[SessionState]:
        """
        Load existing session state.
        
        Args:
            session_id: Session ID
        
        Returns:
            SessionState if found
        """
        return self.sessions.get(session_id)
    
    def update_state(
        self,
        session_id: str,
        tool_name: str,
        result: Any
    ):
        """
        Update state with tool result.
        
        Args:
            session_id: Session ID
            tool_name: Tool that was executed
            result: Tool result
        """
        if session_id not in self.sessions:
            logger.error(f"Unknown session: {session_id}")
            return
        
        state = self.sessions[session_id]
        state.tool_results[tool_name] = result
        
        logger.debug(f"Updated state for session {session_id}")
    
    def add_query(
        self,
        session_id: str,
        query: str
    ):
        """
        Add query to session history.
        
        Args:
            session_id: Session ID
            query: User query
        """
        if session_id not in self.sessions:
            logger.error(f"Unknown session: {session_id}")
            return
        
        state = self.sessions[session_id]
        state.query_history.append(query)
    
    def get_context(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get session context.
        
        Args:
            session_id: Session ID
        
        Returns:
            Context dict
        """
        if session_id not in self.sessions:
            return {}
        
        return self.sessions[session_id].context
    
    def update_context(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ):
        """
        Update session context.
        
        Args:
            session_id: Session ID
            updates: Context updates
        """
        if session_id not in self.sessions:
            logger.error(f"Unknown session: {session_id}")
            return
        
        state = self.sessions[session_id]
        state.context.update(updates)
    
    def clear_session(self, session_id: str):
        """
        Clear a session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
