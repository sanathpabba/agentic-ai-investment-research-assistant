"""
Market Data Tools - Tools for retrieving market data.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .base import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)


class GetMarketDataTool(BaseTool):
    """Tool for retrieving current market data."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="get_market_data",
            description="Get current market data for one or more symbols (price, volume, change)",
            category=ToolCategory.MARKET_DATA,
            parameters={
                "symbols": {
                    "type": "list",
                    "description": "List of stock symbols",
                    "required": True
                }
            },
            risk_level="low",
            rate_limit=60
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute market data retrieval.
        
        Args:
            input_params: Must contain 'symbols' list
            state: Current state
        
        Returns:
            Dict mapping symbols to market data
        """
        self.validate_input(input_params)
        symbols = input_params["symbols"]
        
        logger.info(f"Fetching market data for {len(symbols)} symbols")
        
        # In production, this would call real APIs (yfinance, Alpha Vantage, etc.)
        # For demonstration, return mock data
        results = {}
        for symbol in symbols:
            results[symbol] = {
                "price": 150.00 + hash(symbol) % 100,
                "change": (hash(symbol) % 10) - 5,
                "change_percent": ((hash(symbol) % 10) - 5) / 100,
                "volume": 1000000 + hash(symbol) % 500000,
                "timestamp": datetime.now().isoformat()
            }
        
        return results


class GetHistoricalDataTool(BaseTool):
    """Tool for retrieving historical market data."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="get_historical_data",
            description="Get historical price data for analysis",
            category=ToolCategory.MARKET_DATA,
            parameters={
                "symbols": {
                    "type": "list",
                    "description": "List of stock symbols",
                    "required": True
                },
                "period": {
                    "type": "string",
                    "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)",
                    "required": False,
                    "default": "1y"
                }
            },
            risk_level="low",
            rate_limit=30
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute historical data retrieval.
        
        Args:
            input_params: Must contain 'symbols', optional 'period'
            state: Current state
        
        Returns:
            Dict with historical data
        """
        self.validate_input(input_params)
        symbols = input_params["symbols"]
        period = input_params.get("period", "1y")
        
        logger.info(f"Fetching {period} historical data for {symbols}")
        
        # Mock historical data
        # In production: use yfinance, pandas_datareader, etc.
        results = {}
        for symbol in symbols:
            # Generate mock price series
            prices = []
            base_price = 100 + hash(symbol) % 50
            for i in range(252):  # ~1 year of trading days
                price = base_price + (i * 0.1) + (hash(f"{symbol}{i}") % 10)
                prices.append(price)
            
            results[symbol] = {
                "prices": prices,
                "start_date": (datetime.now() - timedelta(days=365)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "data_points": len(prices)
            }
        
        return results
