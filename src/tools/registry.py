"""
Tool Registry - Central registry for all available tools.
"""

import logging
from typing import Dict, Optional, List
from .base import BaseTool, ToolCategory

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry managing all available tools."""
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[ToolCategory, List[str]] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize and register all tools."""
        from .market_data import GetMarketDataTool, GetHistoricalDataTool
        from .portfolio import (
            PortfolioSummaryTool,
            PortfolioRiskMetricsTool,
            PortfolioAllocationTool
        )
        from .financial_calc import (
            CalculateSharpeRatioTool,
            CalculateVolatilityTool,
            CalculateReturnsTool
        )
        from .sql_query import SQLQueryTool
        
        # Register market data tools
        self.register(GetMarketDataTool())
        self.register(GetHistoricalDataTool())
        
        # Register portfolio tools
        self.register(PortfolioSummaryTool())
        self.register(PortfolioRiskMetricsTool())
        self.register(PortfolioAllocationTool())
        
        # Register financial calculation tools
        self.register(CalculateSharpeRatioTool())
        self.register(CalculateVolatilityTool())
        self.register(CalculateReturnsTool())
        
        # Register SQL tool
        self.register(SQLQueryTool())
        
        logger.info(f"Initialized {len(self._tools)} tools")
    
    def register(self, tool: BaseTool):
        """
        Register a tool.
        
        Args:
            tool: Tool instance to register
        """
        self._tools[tool.name] = tool
        
        # Add to category index
        category = tool.metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(tool.name)
        
        logger.debug(f"Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            Tool instance or None
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """
        Get all tools in a category.
        
        Args:
            category: Tool category
        
        Returns:
            List of tools in category
        """
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names]
    
    def get_alternative_tools(self, tool_name: str) -> List[str]:
        """
        Get alternative tools that can serve similar purposes.
        
        Args:
            tool_name: Name of the original tool
        
        Returns:
            List of alternative tool names
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return []
        
        # Get other tools in same category
        category_tools = self._categories.get(tool.metadata.category, [])
        alternatives = [t for t in category_tools if t != tool_name]
        
        return alternatives
    
    def list_tools(self) -> List[str]:
        """List all tool names."""
        return list(self._tools.keys())
