# Quick Start Guide

Get started with the Agentic AI Investment Research Assistant in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- OpenAI or Anthropic API key

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd project1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Minimum required: OPENAI_API_KEY or ANTHROPIC_API_KEY
nano .env  # or use your preferred editor
```

Example `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

## Basic Usage

### Python Script

Create a file `my_agent.py`:

```python
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

# Initialize
tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)

# Execute query
query = "What is my portfolio's Sharpe ratio?"
response = agent.execute(query)

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence:.2%}")
```

Run it:
```bash
python my_agent.py
```

### Interactive Python

```python
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

tools = ToolRegistry()
agent = AgentOrchestrator(
    tools=tools,
    llm_provider="openai",
    model_name="gpt-4-turbo-preview"
)

# Portfolio analysis
response = agent.execute(
    "Calculate my portfolio's risk metrics and compare to S&P 500"
)
print(response.answer)

# Market screening
response = agent.execute(
    "Find dividend stocks with yield > 4% and P/E < 15"
)
print(response.answer)

# Multi-step analysis
response = agent.execute(
    "Get my current allocation, calculate Sharpe ratio, and suggest rebalancing"
)
print(response.answer)
```

## Example Queries

### Portfolio Analysis
```python
query = """
Analyze my portfolio:
1. Current allocation by sector
2. Risk metrics (Sharpe, volatility, beta)
3. Comparison to S&P 500 benchmark
"""
response = agent.execute(query)
```

### Stock Screening
```python
query = """
Screen for technology stocks with:
- Market cap > $10B
- P/E ratio < 25
- Revenue growth > 15%
- Dividend yield > 0%
"""
response = agent.execute(query)
```

### Risk Analysis
```python
query = """
Calculate:
1. Portfolio volatility (1 year)
2. Maximum drawdown
3. 95% Value at Risk
4. Stress test against 20% market drop
"""
response = agent.execute(query)
```

## Running Examples

The project includes several pre-built examples:

```bash
# Run all examples
python examples/basic_usage.py

# Or import specific examples in Python
from examples.basic_usage import example_portfolio_analysis
example_portfolio_analysis()
```

## Accessing Results

### Basic Response
```python
response = agent.execute(query)

# Answer text
print(response.answer)

# Tools that were used
print(response.tools_used)  # ['portfolio_summary', 'calculate_sharpe_ratio']

# Confidence score
print(response.confidence)  # 0.85

# Execution time
print(response.execution_time)  # 2.3 seconds
```

### Intermediate Results
```python
# Access results from individual tools
for tool, result in response.intermediate_results.items():
    print(f"{tool}: {result}")
```

### Observability Data
```python
# Get execution trace
trace = agent.get_trace(response.trace_id)

# View events
for event in trace['events']:
    print(f"{event['type']}: {event['data']}")

# Get metrics
metrics = agent.get_metrics()
print(f"Total queries: {metrics['total_queries']}")
print(f"Average latency: {metrics['avg_latency']:.2f}s")
```

## Configuration Options

### Agent Configuration

```python
agent = AgentOrchestrator(
    tools=tools,
    llm_provider="openai",  # or "anthropic"
    model_name="gpt-4-turbo-preview",
    max_iterations=10,  # Max planning iterations
    enable_human_in_loop=False,  # Human approval gates
    observability=custom_tracker  # Custom observability
)
```

### Query with Context

```python
context = {
    "portfolio_id": "my_portfolio",
    "risk_tolerance": "moderate",
    "investment_horizon": "10 years"
}

response = agent.execute(query, context=context)
```

### Session Management

```python
# Create session
session_id = "session_001"
response1 = agent.execute(query1, session_id=session_id)

# Continue in same session (maintains context)
response2 = agent.execute(query2, session_id=session_id)
```

## Available Tools

The agent has access to these tools:

### Market Data
- `get_market_data` - Current prices and market data
- `get_historical_data` - Historical price series

### Portfolio
- `portfolio_summary` - Complete portfolio summary
- `portfolio_risk_metrics` - Risk calculations
- `portfolio_allocation` - Allocation breakdown

### Analytics
- `calculate_sharpe_ratio` - Sharpe ratio calculation
- `calculate_volatility` - Volatility metrics
- `calculate_returns` - Return calculations
- `calculate_beta` - Beta vs benchmark

### Database
- `sql_query` - SQL queries (read-only)

## Troubleshooting

### API Key Issues

```python
# Check if API key is loaded
import os
print(os.getenv("OPENAI_API_KEY"))

# Set programmatically
os.environ["OPENAI_API_KEY"] = "your-key"
```

### Import Errors

```python
# Add project to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Mock Data

If you see mock data, it means:
- API keys aren't configured (uses fallback)
- Tool implementations are using mock data

To use real data:
1. Configure API keys in `.env`
2. Replace tool implementations with real API calls

### Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run agent
response = agent.execute(query)
```

## Next Steps

1. **Read Architecture Guide**: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
2. **Explore Tools**: Check tool implementations in `src/tools/`
3. **Customize Workflows**: See [`docs/WORKFLOWS.md`](WORKFLOWS.md)
4. **Add Your Tools**: Follow guide in [`docs/TOOLS.md`](TOOLS.md)
5. **Review Examples**: Study `examples/basic_usage.py`

## Common Patterns

### Error Handling

```python
try:
    response = agent.execute(query)
    if response.confidence < 0.7:
        print("Warning: Low confidence result")
except Exception as e:
    print(f"Execution failed: {e}")
```

### Batch Processing

```python
queries = [
    "Get portfolio summary",
    "Calculate risk metrics",
    "Compare to benchmark"
]

for query in queries:
    response = agent.execute(query, session_id="batch_001")
    print(f"{query}: {response.answer}")
```

### Custom Tool Selection

```python
# Get specific tool
tool = tools.get_tool("portfolio_summary")

# Execute directly
result = tool.execute({}, state=None)
```

## Performance Tips

1. **Use Sessions**: Reuse sessions to cache results
2. **Parallel Queries**: Independent queries can run in parallel
3. **Limit Iterations**: Set lower `max_iterations` for simple queries
4. **Tool Selection**: Be specific in queries to avoid unnecessary tool calls

## Support

- Documentation: `docs/` directory
- Examples: `examples/` directory
- Issues: Open GitHub issue
- Questions: Check documentation first

## Resources

- [Architecture Guide](ARCHITECTURE.md) - Deep dive into system design
- [API Reference](API.md) - Complete API documentation
- [Tool Development](TOOLS.md) - Creating custom tools
- [Workflows](WORKFLOWS.md) - Building complex workflows
