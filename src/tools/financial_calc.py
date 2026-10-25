"""
Financial Calculation Tools - Tools for financial metrics and analytics.
"""

import logging
import math
from typing import Dict, Any, Optional, List
from .base import BaseTool, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)


class CalculateSharpeRatioTool(BaseTool):
    """Tool for calculating Sharpe ratio."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="calculate_sharpe_ratio",
            description="Calculate Sharpe ratio given returns and risk-free rate",
            category=ToolCategory.ANALYTICS,
            parameters={
                "returns": {
                    "type": "list",
                    "description": "List of periodic returns",
                    "required": True
                },
                "risk_free_rate": {
                    "type": "float",
                    "description": "Risk-free rate (annualized)",
                    "required": False,
                    "default": 0.02
                }
            },
            risk_level="low"
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate Sharpe ratio."""
        returns = input_params.get("returns", [])
        risk_free_rate = input_params.get("risk_free_rate", 0.02)
        
        if not returns:
            return 0.0
        
        # Calculate average return
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        # Annualize (assuming daily returns)
        annualized_return = avg_return * 252
        annualized_vol = std_dev * math.sqrt(252)
        
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_vol
        
        logger.info(f"Calculated Sharpe ratio: {sharpe_ratio:.4f}")
        return round(sharpe_ratio, 4)


class CalculateVolatilityTool(BaseTool):
    """Tool for calculating volatility."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="calculate_volatility",
            description="Calculate historical volatility from returns",
            category=ToolCategory.ANALYTICS,
            parameters={
                "returns": {
                    "type": "list",
                    "description": "List of periodic returns",
                    "required": True
                },
                "annualize": {
                    "type": "bool",
                    "description": "Whether to annualize the result",
                    "required": False,
                    "default": True
                }
            },
            risk_level="low"
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate volatility."""
        returns = input_params.get("returns", [])
        annualize = input_params.get("annualize", True)
        
        if not returns:
            return 0.0
        
        # Calculate standard deviation
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        vol = math.sqrt(variance)
        
        if annualize:
            vol = vol * math.sqrt(252)  # Assuming daily returns
        
        logger.info(f"Calculated volatility: {vol:.4f}")
        return round(vol, 4)


class CalculateReturnsTool(BaseTool):
    """Tool for calculating returns."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="calculate_returns",
            description="Calculate returns from price series",
            category=ToolCategory.ANALYTICS,
            parameters={
                "prices": {
                    "type": "list",
                    "description": "List of prices",
                    "required": True
                },
                "return_type": {
                    "type": "string",
                    "description": "Type of return (simple, log)",
                    "required": False,
                    "default": "simple"
                }
            },
            risk_level="low"
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """Calculate returns."""
        prices = input_params.get("prices", [])
        return_type = input_params.get("return_type", "simple")
        
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if return_type == "log":
                ret = math.log(prices[i] / prices[i-1])
            else:  # simple
                ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        logger.info(f"Calculated {len(returns)} {return_type} returns")
        return returns


class CalculateBetaTool(BaseTool):
    """Tool for calculating beta."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="calculate_beta",
            description="Calculate beta relative to a benchmark",
            category=ToolCategory.ANALYTICS,
            parameters={
                "portfolio_returns": {
                    "type": "list",
                    "description": "Portfolio returns",
                    "required": True
                },
                "benchmark_returns": {
                    "type": "list",
                    "description": "Benchmark returns",
                    "required": True
                }
            },
            risk_level="low"
        )
        super().__init__(metadata)
    
    def execute(
        self,
        input_params: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate beta."""
        portfolio_returns = input_params.get("portfolio_returns", [])
        benchmark_returns = input_params.get("benchmark_returns", [])
        
        if len(portfolio_returns) != len(benchmark_returns) or not portfolio_returns:
            return 1.0
        
        # Calculate covariance and variance
        n = len(portfolio_returns)
        port_mean = sum(portfolio_returns) / n
        bench_mean = sum(benchmark_returns) / n
        
        covariance = sum(
            (portfolio_returns[i] - port_mean) * (benchmark_returns[i] - bench_mean)
            for i in range(n)
        ) / n
        
        bench_variance = sum(
            (r - bench_mean) ** 2 for r in benchmark_returns
        ) / n
        
        if bench_variance == 0:
            return 1.0
        
        beta = covariance / bench_variance
        
        logger.info(f"Calculated beta: {beta:.4f}")
        return round(beta, 4)
