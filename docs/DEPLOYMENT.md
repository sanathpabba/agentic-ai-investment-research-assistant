# Deployment Guide

This guide covers deploying the Agentic AI Investment Research Assistant to production environments.

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Databricks Deployment](#databricks-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Production Checklist](#production-checklist)

## Deployment Options

### 1. Local Development
- Best for: Development and testing
- Complexity: Low
- Scalability: Limited

### 2. Cloud Platforms
- Best for: Production workloads
- Options: AWS, Azure, GCP
- Complexity: Medium
- Scalability: High

### 3. Databricks
- Best for: Data-intensive workflows
- Integration: Native Databricks integration
- Complexity: Medium
- Scalability: Very High

### 4. Container Platforms
- Best for: Kubernetes, Cloud Run
- Complexity: Medium-High
- Scalability: Very High

## Local Deployment

### Prerequisites

```bash
- Python 3.9+
- Virtual environment
- API keys configured
```

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
pytest tests/

# Start application
python examples/basic_usage.py
```

### Running as a Service

Create a simple Flask API wrapper:

```python
# app.py
from flask import Flask, request, jsonify
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

app = Flask(__name__)

# Initialize agent
tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query')
    context = data.get('context', {})
    
    response = agent.execute(query_text, context=context)
    
    return jsonify({
        'answer': response.answer,
        'confidence': response.confidence,
        'tools_used': response.tools_used,
        'execution_time': response.execution_time
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Run the API:
```bash
python app.py
```

Test it:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Get my portfolio summary"}'
```

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS Lambda + API Gateway

1. **Create Lambda Function**

```bash
# Install dependencies to deployment package
pip install -r requirements.txt -t package/
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip -r src/
```

2. **Lambda Handler**

```python
# lambda_handler.py
import json
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    query = body.get('query')
    
    response = agent.execute(query)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'answer': response.answer,
            'confidence': response.confidence
        })
    }
```

3. **Deploy with AWS CLI**

```bash
# Create function
aws lambda create-function \
  --function-name investment-agent \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://deployment.zip

# Set environment variables
aws lambda update-function-configuration \
  --function-name investment-agent \
  --environment Variables="{OPENAI_API_KEY=your-key}"
```

#### Option 2: AWS ECS/Fargate

1. **Create Dockerfile**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

2. **Build and Push**

```bash
# Build image
docker build -t investment-agent .

# Tag for ECR
docker tag investment-agent:latest \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/investment-agent:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/investment-agent:latest
```

3. **Deploy to ECS**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name investment-agent-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster investment-agent-cluster \
  --service-name investment-agent-service \
  --task-definition investment-agent:1 \
  --desired-count 2
```

### Azure Deployment

#### Azure Functions

1. **Create Function App**

```bash
func init InvestmentAgent --python
cd InvestmentAgent
```

2. **Create HTTP Function**

```bash
func new --name QueryAgent --template "HTTP trigger"
```

3. **Implement Function**

```python
# QueryAgent/__init__.py
import azure.functions as func
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)

def main(req: func.HttpRequest) -> func.HttpResponse:
    query = req.params.get('query') or req.get_json().get('query')
    
    response = agent.execute(query)
    
    return func.HttpResponse(
        json.dumps({
            'answer': response.answer,
            'confidence': response.confidence
        }),
        mimetype="application/json"
    )
```

4. **Deploy**

```bash
func azure functionapp publish investment-agent-app
```

### GCP Deployment

#### Cloud Run

1. **Create Dockerfile** (same as AWS ECS example)

2. **Build and Deploy**

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/investment-agent

# Deploy to Cloud Run
gcloud run deploy investment-agent \
  --image gcr.io/PROJECT_ID/investment-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Databricks Deployment

### MLflow Deployment

1. **Log Model**

```python
import mlflow
from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

mlflow.set_experiment("/Users/your_email/investment_agent")

with mlflow.start_run():
    tools = ToolRegistry()
    agent = AgentOrchestrator(tools=tools)
    
    # Log parameters
    mlflow.log_param("llm_provider", "openai")
    mlflow.log_param("model_name", "gpt-4-turbo-preview")
    
    # Log model
    mlflow.pyfunc.log_model(
        "agent_model",
        python_model=agent,
        artifacts={"tools": "src/tools"}
    )
```

2. **Register Model**

```python
model_uri = f"runs:/{run.info.run_id}/agent_model"
mlflow.register_model(model_uri, "InvestmentAgent")
```

3. **Deploy as Endpoint**

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create serving endpoint
client.serving_endpoints.create(
    name="investment-agent",
    config={
        "served_models": [{
            "model_name": "InvestmentAgent",
            "model_version": "1",
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }]
    }
)
```

### Databricks Job

1. **Create Notebook**

```python
# investment_agent_job.py
%pip install -r requirements.txt

from src.agent.orchestrator import AgentOrchestrator
from src.tools.registry import ToolRegistry

# Get parameters
dbutils.widgets.text("query", "")
query = dbutils.widgets.get("query")

# Execute
tools = ToolRegistry()
agent = AgentOrchestrator(tools=tools)
response = agent.execute(query)

# Save results
results_df = spark.createDataFrame([{
    'query': query,
    'answer': response.answer,
    'confidence': response.confidence
}])
results_df.write.mode("append").saveAsTable("investment_agent_results")
```

2. **Schedule Job**

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# Create job
client.jobs.create(
    name="Investment Agent Daily Analysis",
    tasks=[{
        "task_key": "run_analysis",
        "notebook_task": {
            "notebook_path": "/Users/your_email/investment_agent_job",
            "base_parameters": {"query": "Daily portfolio analysis"}
        },
        "new_cluster": {
            "spark_version": "13.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 2
        }
    }],
    schedule={
        "quartz_cron_expression": "0 0 9 * * ?",
        "timezone_id": "America/New_York"
    }
)
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY examples/ ./examples/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  investment-agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### Build and Run

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Production Checklist

### Security

- [ ] API keys stored in secrets manager (AWS Secrets Manager, Azure Key Vault)
- [ ] HTTPS/TLS enabled
- [ ] Authentication implemented
- [ ] Authorization/RBAC configured
- [ ] Input validation enabled
- [ ] Rate limiting active
- [ ] Audit logging enabled
- [ ] Network security groups configured
- [ ] Secrets rotation implemented

### Scalability

- [ ] Horizontal scaling configured
- [ ] Load balancer deployed
- [ ] Auto-scaling policies set
- [ ] Caching layer added (Redis)
- [ ] Database connection pooling
- [ ] Async task processing
- [ ] CDN for static assets

### Monitoring

- [ ] Health checks configured
- [ ] Metrics collection (Prometheus, CloudWatch)
- [ ] Log aggregation (ELK, CloudWatch Logs)
- [ ] Alerting rules defined
- [ ] Dashboards created
- [ ] Distributed tracing (Jaeger, X-Ray)
- [ ] Error tracking (Sentry)

### Performance

- [ ] Response time < 5s for 95% of requests
- [ ] Throughput targets met
- [ ] Database queries optimized
- [ ] LLM calls cached when possible
- [ ] Batch processing for bulk operations

### Reliability

- [ ] Multi-region deployment
- [ ] Backup and disaster recovery plan
- [ ] Failover mechanisms
- [ ] Circuit breakers implemented
- [ ] Retry policies configured
- [ ] Dead letter queues for failed tasks

### Compliance

- [ ] Data encryption at rest and in transit
- [ ] PII handling compliant
- [ ] Audit logs retained
- [ ] Access logs available
- [ ] GDPR/CCPA compliance verified

### Documentation

- [ ] API documentation published
- [ ] Runbooks created
- [ ] Architecture diagrams updated
- [ ] Deployment procedures documented
- [ ] Troubleshooting guides available

## Monitoring & Observability

### CloudWatch (AWS)

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Log metric
cloudwatch.put_metric_data(
    Namespace='InvestmentAgent',
    MetricData=[{
        'MetricName': 'QueryLatency',
        'Value': response.execution_time,
        'Unit': 'Seconds'
    }]
)
```

### Application Insights (Azure)

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient('instrumentation-key')

# Track event
tc.track_event('QueryExecuted', {
    'confidence': response.confidence,
    'tools_used': len(response.tools_used)
})
tc.flush()
```

### Cloud Monitoring (GCP)

```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

# Write time series data
series = monitoring_v3.TimeSeries()
series.metric.type = 'custom.googleapis.com/investment_agent/query_latency'
# ... configure series
client.create_time_series(name=project_name, time_series=[series])
```

## Cost Optimization

### LLM Costs

1. **Use cheaper models for simple tasks**
2. **Cache responses for similar queries**
3. **Batch multiple queries**
4. **Implement request throttling**

### Infrastructure Costs

1. **Use spot instances (AWS) / preemptible VMs (GCP)**
2. **Enable auto-scaling with scale-to-zero**
3. **Use reserved instances for base load**
4. **Optimize container images**

## Troubleshooting

### Common Issues

**Issue**: High latency
- **Solution**: Add caching, optimize LLM calls, use parallel execution

**Issue**: API rate limits
- **Solution**: Implement exponential backoff, use multiple API keys

**Issue**: Out of memory
- **Solution**: Increase container memory, optimize data structures

**Issue**: Cold starts (serverless)
- **Solution**: Implement warm-up, use provisioned concurrency

## Next Steps

1. Choose deployment platform
2. Follow platform-specific guide above
3. Complete production checklist
4. Set up monitoring
5. Run load tests
6. Deploy to production
