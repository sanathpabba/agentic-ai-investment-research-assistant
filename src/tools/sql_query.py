"""
SQL Query Tool - Tool for querying structured data.
"""

import logging
from typing import Dict, Any, Optional
from .base import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)


class SQLQueryTool(BaseTool):
    """Tool for executing SQL queries."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="sql_query",
            description="Execute SQL query against portfolio database",
            category=ToolCategory.DATABASE,
            parameters={
                "query": {
                    "type": "string",
                    "description": "SQL query to execute",
                    "required": True
                },
                "limit": {
                    "type": "int",
                    "description": "Maximum rows to return",
                    "required": False,
                    "default": 100
                }
            },
            risk_level="medium",
            requires_approval=False
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute SQL query."""
        query = input_params.get("query", "")
        limit = input_params.get("limit", 100)
        
        logger.info(f"Executing SQL query: {query[:100]}...")
        
        # Validate query is read-only
        if not self._is_read_only(query):
            raise ValueError("Only SELECT queries are allowed")
        
        # Mock query execution
        # In production: connect to actual database (Databricks SQL, PostgreSQL, etc.)
        
        # Return mock results based on query keywords
        if "holdings" in query.lower():
            return {
                "columns": ["symbol", "shares", "avg_cost", "current_value"],
                "rows": [
                    ["AAPL", 100, 145.50, 17500],
                    ["MSFT", 150, 320.00, 52500],
                    ["GOOGL", 50, 2650.00, 14000],
                ],
                "row_count": 3
            }
        elif "transactions" in query.lower():
            return {
                "columns": ["date", "symbol", "type", "shares", "price"],
                "rows": [
                    ["2024-01-10", "AAPL", "BUY", 50, 175.00],
                    ["2024-01-05", "MSFT", "BUY", 75, 350.00],
                ],
                "row_count": 2
            }
        else:
            return {
                "columns": ["result"],
                "rows": [["Query executed successfully"]],
                "row_count": 1
            }
    
    def _is_read_only(self, query: str) -> bool:
        """Check if query is read-only."""
        query_upper = query.upper().strip()
        
        # Check for write operations
        write_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
        for keyword in write_keywords:
            if keyword in query_upper:
                return False
        
        return True
