"""
Guardrails - Safety and validation mechanisms for agent execution.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Guardrails:
    """
    Implements guardrails to prevent unauthorized or unsafe operations.
    
    Includes:
    - Tool access control
    - Rate limiting
    - Input validation
    - Output verification
    - Boundary enforcement
    """
    
    def __init__(self, tools: Any):
        """
        Initialize guardrails.
        
        Args:
            tools: Tool registry
        """
        self.tools = tools
        self.rate_limiters: Dict[str, List[datetime]] = {}
        self.access_policies = self._load_access_policies()
    
    def _load_access_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load access control policies for tools."""
        # In production: load from config file or database
        return {
            "default": {
                "allowed_categories": ["market_data", "portfolio", "analytics", "database", "retrieval"],
                "max_concurrent": 5,
                "require_approval": False
            },
            "high_risk": {
                "allowed_tools": [],  # Explicitly list allowed high-risk tools
                "require_approval": True,
                "audit_required": True
            }
        }
    
    def validate_tool_access(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate that tool access is allowed.
        
        Args:
            tool_name: Name of tool to access
            tool_input: Tool input parameters
            context: Execution context
        
        Returns:
            True if access is allowed
        """
        tool = self.tools.get_tool(tool_name)
        if not tool:
            logger.error(f"Unknown tool: {tool_name}")
            return False
        
        # Check rate limits
        if not self._check_rate_limit(tool_name, tool.metadata.rate_limit):
            logger.warning(f"Rate limit exceeded for {tool_name}")
            return False
        
        # Check risk level
        if tool.metadata.risk_level == "high":
            if not self._validate_high_risk_access(tool_name, context):
                logger.warning(f"High-risk tool {tool_name} access denied")
                return False
        
        # Validate input parameters
        try:
            tool.validate_input(tool_input)
        except ValueError as e:
            logger.error(f"Invalid input for {tool_name}: {e}")
            return False
        
        logger.debug(f"Tool access validated: {tool_name}")
        return True
    
    def _check_rate_limit(
        self,
        tool_name: str,
        limit: Optional[int]
    ) -> bool:
        """
        Check if tool is within rate limit.
        
        Args:
            tool_name: Tool name
            limit: Maximum calls per minute
        
        Returns:
            True if within limit
        """
        if limit is None:
            return True
        
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Initialize or clean old entries
        if tool_name not in self.rate_limiters:
            self.rate_limiters[tool_name] = []
        
        # Remove old entries
        self.rate_limiters[tool_name] = [
            ts for ts in self.rate_limiters[tool_name]
            if ts > minute_ago
        ]
        
        # Check limit
        if len(self.rate_limiters[tool_name]) >= limit:
            return False
        
        # Record this call
        self.rate_limiters[tool_name].append(now)
        return True
    
    def _validate_high_risk_access(
        self,
        tool_name: str,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Validate access to high-risk tools.
        
        Args:
            tool_name: Tool name
            context: Execution context
        
        Returns:
            True if access granted
        """
        policy = self.access_policies.get("high_risk", {})
        allowed_tools = policy.get("allowed_tools", [])
        
        # Must be explicitly allowed
        if tool_name not in allowed_tools:
            return False
        
        # Additional checks can be added here
        # e.g., user permissions, time of day restrictions, etc.
        
        return True
    
    def validate_output(
        self,
        tool_name: str,
        output: Any
    ) -> bool:
        """
        Validate tool output.
        
        Args:
            tool_name: Tool that produced output
            output: Output to validate
        
        Returns:
            True if output is valid
        """
        # Basic validation
        if output is None:
            logger.warning(f"Tool {tool_name} returned None")
            return False
        
        # Type-specific validation can be added here
        
        return True
    
    def log_access(
        self,
        tool_name: str,
        input_params: Dict[str, Any],
        result: Any,
        user_context: Optional[Dict[str, Any]] = None
    ):
        """
        Log tool access for audit trail.
        
        Args:
            tool_name: Tool accessed
            input_params: Input parameters
            result: Execution result
            user_context: User context
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "input": str(input_params)[:200],  # Truncate for logging
            "success": result is not None,
            "user": user_context.get("user_id") if user_context else "anonymous"
        }
        
        logger.info(f"Audit: {audit_entry}")
        
        # In production: write to audit database
