"""
Tool Executor - Executes tool calls with error handling and retries.
"""

import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tool calls with retry logic and error handling."""
    
    def __init__(self, tools: Any):
        """
        Initialize tool executor.
        
        Args:
            tools: Tool registry
        """
        self.tools = tools
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a tool with retry logic.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            state: Current execution state
        
        Returns:
            Tool execution result
        """
        logger.info(f"Executing tool: {tool_name}")
        
        # Get tool from registry
        tool = self.tools.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute tool
        try:
            result = tool.execute(tool_input, state)
            logger.info(f"Tool {tool_name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise
