# Architecture Guide

## System Overview

The Agentic AI Investment Research & Analytics Assistant is built on a multi-layered architecture that separates concerns and enables flexible, scalable analytical workflows.

## Core Components

### 1. Agent Orchestrator

**Location**: `src/agent/orchestrator.py`

The orchestrator is the central coordinator that manages the entire agent workflow:

```python
┌──────────────────────────────────────────┐
│        Agent Orchestrator                │
│                                          │
│  ┌────────┐  ┌─────────┐  ┌──────────┐ │
│  │Planner │─>│Executor │─>│Validator │ │
│  └────────┘  └─────────┘  └──────────┘ │
└──────────────────────────────────────────┘
```

**Responsibilities**:
- Coordinate planning, execution, and validation
- Manage state across tool calls
- Handle errors and retries
- Enforce guardrails
- Track observability metrics

**Key Methods**:
- `execute(query, context, session_id)` - Main execution entry point
- `_request_human_approval(step)` - Human-in-the-loop gates
- `_retry_with_fallback(step, state)` - Retry logic with alternatives

### 2. Task Planner

**Location**: `src/agent/planner.py`

Uses LLM reasoning to decompose queries into execution plans:

```python
User Query
    ↓
┌─────────────┐
│   Planner   │ ← Tool Registry
└─────────────┘
    ↓
Execution Plan
  - Step 1: Get market data
  - Step 2: Calculate metrics
  - Step 3: Compare benchmark
  - Step 4: Synthesize answer
```

**Planning Strategies**:
- **Sequential**: Steps execute in order (dependencies)
- **Parallel**: Independent steps execute concurrently
- **Adaptive**: Adjust based on intermediate results

**Key Methods**:
- `create_plan(query, context, state)` - Generate execution plan
- `synthesize_response(query, results, validation)` - Create final answer

### 3. Tool Executor

**Location**: `src/agent/executor.py`

Executes tool calls with retry logic:

```python
Tool Call Request
    ↓
┌──────────────┐
│   Executor   │
└──────────────┘
    ↓
  Retry with
  Exponential
  Backoff
    ↓
Tool Result
```

**Features**:
- Automatic retry (3 attempts)
- Exponential backoff (2, 4, 10 seconds)
- Error handling and logging

### 4. Result Validator

**Location**: `src/agent/validator.py`

Validates execution results for correctness:

**Validation Checks**:
- At least one step succeeded
- No critical failures
- Result types are valid
- Confidence scoring

**Confidence Calculation**:
```
confidence = success_rate × multiplier
- multiplier = 0.9 if no issues
- multiplier = 0.5 if issues present
```

## Tool System

### Tool Registry

**Location**: `src/tools/registry.py`

Central registry managing all tools:

```python
ToolRegistry
    ├── Market Data Tools
    │   ├── get_market_data
    │   └── get_historical_data
    ├── Portfolio Tools
    │   ├── portfolio_summary
    │   ├── portfolio_risk_metrics
    │   └── portfolio_allocation
    ├── Analytics Tools
    │   ├── calculate_sharpe_ratio
    │   ├── calculate_volatility
    │   └── calculate_returns
    └── Database Tools
        └── sql_query
```

### Tool Interface

**Base Class**: `src/tools/base.py`

All tools implement:
```python
class BaseTool(ABC):
    def execute(input_params, state) -> Any
    def validate_input(input_params) -> bool
```

**Tool Metadata**:
- Name and description
- Category (market_data, portfolio, analytics, etc.)
- Parameters (required/optional)
- Risk level (low, medium, high)
- Rate limits

## Utility Systems

### Guardrails

**Location**: `src/utils/guardrails.py`

Safety mechanisms:

1. **Access Control**
   - Tool category restrictions
   - Explicit allow lists for high-risk tools
   - Context-based permissions

2. **Rate Limiting**
   - Per-tool rate limits (calls/minute)
   - Time-window tracking
   - Automatic cleanup of old entries

3. **Input Validation**
   - Parameter validation
   - Type checking
   - SQL injection prevention

4. **Output Verification**
   - Null check
   - Type validation
   - Anomaly detection

### Observability

**Location**: `src/utils/observability.py`

Comprehensive tracking:

```python
Trace Structure
├── trace_id: unique identifier
├── query: original user query
├── start_time: execution start
├── end_time: execution completion
├── events: chronological event log
│   ├── planning_complete
│   ├── tool_call (multiple)
│   └── validation_complete
└── metrics
    ├── duration_seconds
    ├── tools_used
    ├── token_usage
    └── confidence
```

**Metrics Tracked**:
- Total queries processed
- Tool calls executed
- Token usage
- Error rates
- Average latency

### State Management

**Location**: `src/utils/state_manager.py`

Session state structure:

```python
SessionState
├── session_id: unique session identifier
├── created_at: creation timestamp
├── query_history: all queries in session
├── tool_results: cached tool results
├── context: session context data
└── metadata: additional metadata
```

**State Persistence**:
- In-memory for current implementation
- Can extend to Redis, database, etc.
- Supports multi-turn conversations

## Data Flow

### Complete Execution Flow

```
1. User Query
      ↓
2. Create/Load Session State
      ↓
3. Task Planning (LLM)
      ↓
4. For each step in plan:
   a. Check Guardrails
   b. Request Approval (if needed)
   c. Execute Tool
   d. Validate Result
   e. Update State
   f. Log Observability Event
      ↓
5. Validate All Results
      ↓
6. Synthesize Response (LLM)
      ↓
7. Return AgentResponse
```

### Tool Execution Flow

```
Tool Request
    ↓
Validate Access (Guardrails)
    ↓
Check Rate Limit
    ↓
Validate Input Parameters
    ↓
Execute Tool (with retries)
    ↓
Validate Output
    ↓
Log Audit Trail
    ↓
Return Result
```

## Integration Points

### LLM Integration

Currently supports:
- **OpenAI**: GPT-4 Turbo, GPT-3.5
- **Anthropic**: Claude 3

Integration points:
1. **Planning**: `TaskPlanner._call_openai()` / `_call_anthropic()`
2. **Synthesis**: `TaskPlanner.synthesize_response()`

### External Data Sources

Mock implementations provided. To integrate real sources:

1. **Market Data**: Replace `market_data.py` with yfinance, Alpha Vantage
2. **Portfolio Data**: Connect to portfolio management API/database
3. **SQL Database**: Connect to Databricks SQL, PostgreSQL, etc.

## Extension Points

### Adding New Tools

1. Create tool class extending `BaseTool`
2. Implement `execute()` method
3. Define `ToolMetadata`
4. Register in `ToolRegistry._initialize_tools()`

Example:
```python
from src.tools.base import BaseTool, ToolMetadata, ToolCategory

class MyNewTool(BaseTool):
    def __init__(self):
        metadata = ToolMetadata(
            name="my_new_tool",
            description="What this tool does",
            category=ToolCategory.ANALYTICS,
            parameters={"param1": {"type": "string", "required": True}},
            risk_level="low"
        )
        super().__init__(metadata)
    
    def execute(self, input_params, state=None):
        # Implementation
        return result
```

### Custom Planning Strategies

Extend `TaskPlanner.create_plan()` with custom logic for specific query types.

### Advanced Guardrails

Add custom validation in `Guardrails.validate_tool_access()`:
- Time-based restrictions
- User role checks
- Budget limits
- Compliance rules

## Performance Considerations

### Optimization Strategies

1. **Parallel Execution**: Use `PlanStrategy.PARALLEL` for independent tools
2. **Caching**: Cache tool results in `StateManager`
3. **Rate Limit Management**: Batch requests where possible
4. **LLM Token Optimization**: Use efficient prompts, structured outputs

### Scalability

Current architecture supports:
- Horizontal scaling of tool executors
- Stateless request handling
- Distributed state storage (Redis, etc.)
- Async tool execution

## Security

### Current Implementations

1. **Input Validation**: All tools validate parameters
2. **SQL Injection Prevention**: Read-only query validation
3. **Rate Limiting**: Per-tool limits
4. **Audit Logging**: All tool access logged

### Production Recommendations

1. Add authentication/authorization
2. Encrypt sensitive data at rest
3. Use secure credential management (e.g., AWS Secrets Manager)
4. Implement network security (VPC, firewalls)
5. Add HTTPS/TLS for APIs

## Monitoring

### Key Metrics to Track

1. **Performance**
   - Query latency (p50, p95, p99)
   - Tool execution time
   - LLM response time

2. **Usage**
   - Queries per hour/day
   - Tool call distribution
   - Token consumption

3. **Quality**
   - Validation confidence scores
   - Error rates
   - Retry frequency

4. **Cost**
   - LLM token costs
   - API call costs
   - Infrastructure costs

### Alerting

Set up alerts for:
- High error rates (> 5%)
- Slow queries (> 30s)
- Rate limit violations
- Unusual token usage

## Future Enhancements

### Planned Features

1. **Multi-Agent Collaboration**: Specialist agents for different domains
2. **GraphRAG**: Knowledge graph integration
3. **Streaming Responses**: Real-time output generation
4. **Model Fine-tuning**: Custom models for planning
5. **Advanced Caching**: Semantic caching for similar queries
6. **Distributed Execution**: Celery/Ray for parallel tool execution

### Research Directions

1. **Self-Improving Agents**: Learn from past executions
2. **Automated Tool Discovery**: Dynamic tool registration
3. **Explainable AI**: Detailed reasoning traces
4. **Multi-Modal Support**: Image/chart analysis
