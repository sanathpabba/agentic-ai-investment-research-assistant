"""
Basic Usage Example

Demonstrates basic agent usage for investment research queries.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry


def example_portfolio_analysis():
    """Example: Analyze portfolio risk metrics."""
    print("=" * 60)
    print("Example 1: Portfolio Risk Analysis")
    print("=" * 60)
    
    # Initialize agent
    tools = ToolRegistry()
    agent = AgentOrchestrator(
        tools=tools,
        llm_provider="openai",
        model_name="gpt-4-turbo-preview"
    )
    
    # Execute query
    query = "What is my portfolio's Sharpe ratio and how does it compare to S&P 500?"
    
    print(f"\nQuery: {query}\n")
    print("Executing agent workflow...\n")
    
    try:
        response = agent.execute(query)
        
        print("Results:")
        print("-" * 60)
        print(f"Answer: {response.answer}")
        print(f"\nTools Used: {', '.join(response.tools_used)}")
        print(f"Confidence: {response.confidence:.2%}")
        print(f"Execution Time: {response.execution_time:.2f}s")
        print(f"Trace ID: {response.trace_id}")
        
        print("\nIntermediate Results:")
        for tool, result in response.intermediate_results.items():
            print(f"  - {tool}: {str(result)[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")


def example_market_screening():
    """Example: Screen stocks with specific criteria."""
    print("\n" + "=" * 60)
    print("Example 2: Market Screening")
    print("=" * 60)
    
    tools = ToolRegistry()
    agent = AgentOrchestrator(
        tools=tools,
        llm_provider="openai",
        model_name="gpt-4-turbo-preview"
    )
    
    query = """
    Find technology stocks with:
    - Market cap > $10B
    - P/E ratio < 25
    - Revenue growth > 15%
    Calculate risk metrics for the top 5
    """
    
    print(f"\nQuery: {query}\n")
    print("Executing agent workflow...\n")
    
    try:
        response = agent.execute(query)
        
        print("Results:")
        print("-" * 60)
        print(f"Answer: {response.answer}")
        print(f"\nTools Used: {', '.join(response.tools_used)}")
        print(f"Confidence: {response.confidence:.2%}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_risk_analysis():
    """Example: Comprehensive risk analysis."""
    print("\n" + "=" * 60)
    print("Example 3: Risk Analysis")
    print("=" * 60)
    
    tools = ToolRegistry()
    agent = AgentOrchestrator(
        tools=tools,
        llm_provider="openai",
        model_name="gpt-4-turbo-preview"
    )
    
    query = "Calculate my portfolio's volatility, beta, and max drawdown over the last year"
    
    print(f"\nQuery: {query}\n")
    print("Executing agent workflow...\n")
    
    try:
        response = agent.execute(query)
        
        print("Results:")
        print("-" * 60)
        print(f"Answer: {response.answer}")
        print(f"\nRisk Metrics:")
        if "portfolio_risk_metrics" in response.intermediate_results:
            metrics = response.intermediate_results["portfolio_risk_metrics"]
            for metric, value in metrics.items():
                print(f"  - {metric}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_context():
    """Example: Query with additional context."""
    print("\n" + "=" * 60)
    print("Example 4: Query with Context")
    print("=" * 60)
    
    tools = ToolRegistry()
    agent = AgentOrchestrator(
        tools=tools,
        llm_provider="openai",
        model_name="gpt-4-turbo-preview"
    )
    
    # Provide context about portfolio
    context = {
        "portfolio_id": "my_portfolio_001",
        "risk_tolerance": "moderate",
        "investment_horizon": "10 years",
        "target_return": 0.08  # 8% annual return
    }
    
    query = "How is my portfolio performing relative to my target return?"
    
    print(f"\nQuery: {query}")
    print(f"Context: {context}\n")
    print("Executing agent workflow...\n")
    
    try:
        response = agent.execute(query, context=context)
        
        print("Results:")
        print("-" * 60)
        print(f"Answer: {response.answer}")
        print(f"\nTools Used: {', '.join(response.tools_used)}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_observability():
    """Example: Access observability data."""
    print("\n" + "=" * 60)
    print("Example 5: Observability")
    print("=" * 60)
    
    tools = ToolRegistry()
    agent = AgentOrchestrator(
        tools=tools,
        llm_provider="openai",
        model_name="gpt-4-turbo-preview"
    )
    
    query = "Get my portfolio summary and allocation breakdown"
    
    print(f"\nQuery: {query}\n")
    
    try:
        response = agent.execute(query)
        
        print("Results:")
        print("-" * 60)
        print(f"Answer: {response.answer}\n")
        
        # Access trace data
        print("Observability Data:")
        print("-" * 60)
        trace = agent.get_trace(response.trace_id)
        
        print(f"Trace ID: {trace['trace_id']}")
        print(f"Query: {trace['query']}")
        print(f"Duration: {trace['metrics'].get('duration_seconds', 0):.2f}s")
        
        print(f"\nEvents ({len(trace['events'])} total):")
        for i, event in enumerate(trace['events'][:5], 1):
            print(f"  {i}. {event['type']}: {event['data']}")
        
        # Global metrics
        print("\nGlobal Metrics:")
        metrics = agent.get_metrics()
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Agentic AI Investment Research Assistant - Examples")
    print("=" * 60)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("\nWarning: OPENAI_API_KEY not set. Examples will use mock data.")
        print("Set environment variable: export OPENAI_API_KEY=your_key\n")
    
    # Run examples
    examples = [
        example_portfolio_analysis,
        example_market_screening,
        example_risk_analysis,
        example_with_context,
        example_observability
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nExample failed: {e}")
        
        print("\n" + "-" * 60)
        input("Press Enter to continue...")
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
