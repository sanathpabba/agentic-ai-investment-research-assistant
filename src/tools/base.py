"""
Base Tool Interface - Abstract base class for all tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Categories of tools."""
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    ANALYTICS = "analytics"
    DATABASE = "database"
    RETRIEVAL = "retrieval"
    SCREENING = "screening"


@dataclass
class ToolMetadata:
    """Metadata about a tool."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    risk_level: str = "low"  # low, medium, high
    requires_approval: bool = False
    rate_limit: Optional[int] = None  # calls per minute


class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    def __init__(self, metadata: ToolMetadata):
        """
        Initialize tool.
        
        Args:
            metadata: Tool metadata
        """
        self.metadata = metadata
    
    @abstractmethod
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute the tool.
        
        Args:
            input_params: Input parameters
            state: Current execution state
        
        Returns:
            Tool execution result
        """
        pass
    
    def validate_input(self, input_params: Dict[str, Any]) -> bool:
        """
        Validate input parameters.
        
        Args:
            input_params: Parameters to validate
        
        Returns:
            True if valid
        """
        required_params = [
            k for k, v in self.metadata.parameters.items()
            if v.get("required", False)
        ]
        
        for param in required_params:
            if param not in input_params:
                raise ValueError(f"Missing required parameter: {param}")
        
        return True
    
    @property
    def name(self) -> str:
        """Get tool name."""
        return self.metadata.name
    
    @property
    def description(self) -> str:
        """Get tool description."""
        return self.metadata.description
