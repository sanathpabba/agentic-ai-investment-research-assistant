# Agentic AI Investment Research & Analytics Assistant

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

A production-ready **Agentic AI system** designed to autonomously coordinate multiple analytical steps for investment research questions. Instead of relying on single LLM prompts, this system implements a sophisticated agent workflow capable of:

- **Planning** complex analytical tasks
- **Selecting** appropriate tools dynamically
- **Retrieving** supporting information via RAG
- **Executing** financial calculations
- **Validating** intermediate results
- **Generating** consolidated analytical responses

This project demonstrates how agentic systems can evolve traditional analytics from static dashboards toward **goal-oriented AI-assisted decision support**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query Interface                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestrator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Planner    │─▶│   Executor   │─▶│  Validator   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Tool Layer   │ │  RAG System  │ │  Guardrails  │
│              │ │              │ │              │
│ • Market Data│ │ • Vector DB  │ │ • Access Ctrl│
│ • Portfolio  │ │ • Retrieval  │ │ • Rate Limits│
│ • SQL Query  │ │ • Embedding  │ │ • Validation │
│ • Analytics  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Observability Layer                        │
│  • Agent Traces  • Token Usage  • Latency  • Quality       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### Agentic AI Capabilities
- **Self-directed Planning**: Breaks down complex queries into analytical steps
- **Dynamic Tool Selection**: Chooses appropriate tools based on context
- **State Management**: Maintains conversation and task context
- **Retry Logic**: Handles failures gracefully with intelligent retries
- **Human-in-the-Loop**: Approval gates for high-risk operations

### Tool Ecosystem
1. **Market Data Tools**
   - Real-time price retrieval
   - Historical data analysis
   - Market indicators

2. **Portfolio Analytics**
   - Holdings analysis
   - Performance calculation
   - Allocation insights

3. **SQL Query Engine**
   - Structured data querying
   - Complex aggregations
   - Time-series analysis

4. **Financial Calculations**
   - Risk metrics (Sharpe, Sortino, Beta)
   - Return analysis
   - Volatility measures

5. **RAG System**
   - Document retrieval
   - Knowledge augmentation
   - Context enrichment

6. **Benchmark Comparison**
   - Index comparison
   - Peer analysis
   - Relative performance

7. **Risk Analysis**
   - VaR calculations
   - Stress testing
   - Scenario analysis

8. **Investment Screening**
   - Criteria-based filtering
   - Multi-factor scoring
   - Opportunity identification

### Guardrails & Safety
- **Access Control**: Tool-level permissions
- **Validation Gates**: Output verification
- **Rate Limiting**: API protection
- **Audit Logging**: Complete traceability
- **Boundary Enforcement**: Prevents unauthorized actions

### Observability
- **Agent Traces**: Complete execution path tracking
- **Tool Call Logging**: All tool invocations recorded
- **Token Usage Monitoring**: Cost tracking per query
- **Latency Metrics**: Performance profiling
- **Quality Scoring**: Output validation metrics

## 📋 Technical Stack

| Category | Technologies |
|----------|-------------|
| **Core Language** | Python 3.9+ |
| **LLM Integration** | OpenAI API, Anthropic Claude |
| **Agent Framework** | LangChain, Custom Orchestrator |
| **Data Platform** | Databricks, Apache Spark |
| **Database** | SQL (Databricks SQL), Vector DB (FAISS/ChromaDB) |
| **APIs** | REST APIs, Financial Data APIs |
| **RAG** | LangChain, Vector Search, Embeddings |
| **Observability** | MLflow, Custom Logging |
| **Version Control** | Git, GitHub |

## 🔧 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)
- API keys for LLM providers

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd project1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file with:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
DATABRICKS_HOST=your_databricks_host
DATABRICKS_TOKEN=your_databricks_token

# MLflow
MLFLOW_TRACKING_URI=databricks
```

## 📚 Usage

### Basic Example

```python
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

# Initialize the agent
tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)

# Execute a query
query = "What is my portfolio's Sharpe ratio compared to S&P 500?"
response = agent.execute(query)

print(response.answer)
print(f"Tools used: {response.tools_used}")
print(f"Confidence: {response.confidence}")
```

### Advanced Workflow

```python
from src.workflows.research_workflow import InvestmentResearchWorkflow

# Create workflow with human-in-the-loop
workflow = InvestmentResearchWorkflow(
    human_approval_required=True,
    risk_threshold=0.8
)

# Execute complex research task
query = """
Analyze tech stocks with:
1. Market cap > $10B
2. P/E ratio < 25
3. Revenue growth > 15%
Then calculate risk metrics and compare to QQQ
"""

result = workflow.execute(query)
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/test_agent.py
```

## 📊 Project Structure

```
project1/
├── src/
│   ├── agent/              # Agent core logic
│   │   ├── orchestrator.py # Main agent controller
│   │   ├── planner.py      # Task planning
│   │   ├── executor.py     # Tool execution
│   │   └── validator.py    # Result validation
│   ├── tools/              # Tool implementations
│   │   ├── market_data.py
│   │   ├── portfolio.py
│   │   ├── sql_query.py
│   │   ├── financial_calc.py
│   │   └── registry.py
│   ├── rag/                # RAG system
│   │   ├── retriever.py
│   │   ├── embeddings.py
│   │   └── vector_store.py
│   ├── workflows/          # Predefined workflows
│   │   └── research_workflow.py
│   └── utils/              # Utilities
│       ├── guardrails.py
│       ├── observability.py
│       └── state_manager.py
├── config/                 # Configuration files
├── data/                   # Sample data
├── tests/                  # Test suites
├── docs/                   # Documentation
├── examples/               # Usage examples
└── requirements.txt
```

## 📖 Documentation

Detailed documentation is available in the `docs/` directory:

- [Architecture Guide](docs/ARCHITECTURE.md) - Deep dive into system design
- [Tool Development](docs/TOOLS.md) - How to create custom tools
- [Workflow Guide](docs/WORKFLOWS.md) - Building agent workflows
- [RAG Implementation](docs/RAG.md) - RAG system details
- [Guardrails](docs/GUARDRAILS.md) - Safety and validation
- [Observability](docs/OBSERVABILITY.md) - Monitoring and tracing
- [API Reference](docs/API.md) - Complete API documentation

## 🎓 Key Concepts Demonstrated

### 1. Agentic AI Patterns
- **ReAct (Reasoning + Acting)**: Agent reasons about actions before execution
- **Plan-and-Execute**: Separates planning from execution
- **Tool Use**: Dynamic tool selection and invocation
- **Memory Management**: Maintains context across interactions

### 2. Workflow Orchestration
- Multi-step analytical pipelines
- Conditional branching based on intermediate results
- Error handling and recovery
- State persistence

### 3. Human-in-the-Loop
- Approval gates for high-risk actions
- Interactive clarification requests
- Override mechanisms
- Audit trails

### 4. Guardrails
- Input validation
- Output verification
- Tool access control
- Rate limiting
- Anomaly detection

### 5. Observability
- Structured logging
- Distributed tracing
- Metrics collection
- Cost tracking
- Quality monitoring

## 🔍 Example Queries

The agent can handle complex analytical queries such as:

1. **Risk Analysis**
   ```
   "Calculate the 95% VaR for my portfolio and stress test against a 20% market crash"
   ```

2. **Screening**
   ```
   "Find dividend stocks with yield > 4%, payout ratio < 60%, and 5-year dividend growth"
   ```

3. **Comparison**
   ```
   "Compare my tech allocation to NASDAQ 100 and calculate tracking error"
   ```

4. **Multi-Step Analysis**
   ```
   "Identify undervalued healthcare stocks, calculate their intrinsic value using DCF, 
    and rank by margin of safety"
   ```

## 🛣️ Roadmap

- [ ] Multi-agent collaboration (specialist agents)
- [ ] Real-time streaming responses
- [ ] Advanced caching strategies
- [ ] GraphRAG implementation
- [ ] Custom model fine-tuning
- [ ] Web UI dashboard

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Sanath Pabba**
- LinkedIn: [sanathpabba](https://www.linkedin.com/in/sanathpabba/)
- GitHub: [@sanathpabba](https://github.com/sanathpabba)

## 🙏 Acknowledgments

- Built with LangChain framework
- Databricks for data platform
- OpenAI and Anthropic for LLM capabilities
- Financial data providers

## 📞 Contact

For questions or feedback, please open an issue or reach out via LinkedIn.

---

**Note**: This is a demonstration project showcasing agentic AI concepts. Use appropriate risk management and validation for production financial applications.
