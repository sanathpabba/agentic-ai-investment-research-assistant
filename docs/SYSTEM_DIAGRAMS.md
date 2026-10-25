# System Diagrams & Visualizations

This document provides visual representations of the system architecture, data flows, and component interactions.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Agent Execution Flow](#agent-execution-flow)
3. [Tool Ecosystem](#tool-ecosystem)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Component Interactions](#component-interactions)
6. [Deployment Architecture](#deployment-architecture)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                             │
│                   (CLI / API / Web / Notebook)                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Query + Context
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATOR                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Planner    │─>│   Executor   │─>│  Validator   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐         │
│  │           State Manager (Session Context)            │         │
│  └──────────────────────────────────────────────────────┘         │
└───────────┬───────────────────────────────┬───────────────────────┘
            │                               │
            │ Tool Calls                    │ Guardrails
            ▼                               ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│     TOOL REGISTRY         │  │      GUARDRAILS          │
│                           │  │  • Access Control        │
│ • Market Data Tools       │  │  • Rate Limiting         │
│ • Portfolio Tools         │  │  • Input Validation      │
│ • Analytics Tools         │  │  • Audit Logging         │
│ • Database Tools          │  └──────────────────────────┘
└───────────┬───────────────┘
            │
            │ External Calls
            ▼
┌───────────────────────────────────────────────────────────┐
│                  EXTERNAL SYSTEMS                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │   LLM    │  │ Market   │  │Portfolio │  │Database  ││
│  │   APIs   │  │   APIs   │  │   APIs   │  │  (SQL)   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└───────────────────────────────────────────────────────────┘
            │
            │ Events & Metrics
            ▼
┌───────────────────────────────────────────────────────────┐
│                 OBSERVABILITY LAYER                       │
│  • Execution Traces    • Token Usage                      │
│  • Tool Call Logs      • Performance Metrics              │
│  • Error Tracking      • Quality Scores                   │
└───────────────────────────────────────────────────────────┘
```

## Agent Execution Flow

### Request Processing Pipeline

```
User Query
    │
    ▼
┌────────────────────────────────────┐
│  1. Session Management             │
│  • Load/Create Session             │
│  • Retrieve Context                │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  2. Task Planning                  │
│  • LLM Reasoning                   │
│  • Tool Selection                  │
│  • Dependency Analysis             │
│  • Strategy Selection              │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  3. Plan Validation                │
│  • Check Tool Availability         │
│  • Validate Dependencies           │
│  • Estimate Duration               │
└─────────────┬──────────────────────┘
              │
              ▼
         ╔════════════════════╗
         ║  For Each Step     ║
         ╚════════┬═══════════╝
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌────────────────┐    ┌────────────────┐
│  4a. Guardrail │    │  4b. Approval  │
│      Check     │    │    (if needed) │
└────┬───────────┘    └────┬───────────┘
     │ Pass              │ Approved
     ▼                   ▼
┌────────────────────────────────────┐
│  5. Tool Execution                 │
│  • Call Tool                       │
│  • Handle Errors                   │
│  • Retry if Failed                 │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  6. Result Validation              │
│  • Type Check                      │
│  • Null Check                      │
│  • Anomaly Detection               │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  7. State Update                   │
│  • Store Result                    │
│  • Update Context                  │
│  • Log Event                       │
└─────────────┬──────────────────────┘
              │
         ╔════════════════════╗
         ║  End Loop          ║
         ╚════════┬═══════════╝
                  │
                  ▼
┌────────────────────────────────────┐
│  8. Aggregate Validation           │
│  • Check Success Rate              │
│  • Calculate Confidence            │
│  • Identify Issues                 │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  9. Response Synthesis             │
│  • LLM Synthesis                   │
│  • Format Answer                   │
│  • Add Metadata                    │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│  10. Observability Logging         │
│  • End Trace                       │
│  • Update Metrics                  │
│  • Store Artifacts                 │
└─────────────┬──────────────────────┘
              │
              ▼
        Final Response
```

## Tool Ecosystem

### Tool Categories & Relationships

```
                    ┌──────────────────┐
                    │  Tool Registry   │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Market Data  │ │  Portfolio   │ │  Analytics   │
    │              │ │              │ │              │
    │ • Current    │ │ • Summary    │ │ • Sharpe     │
    │ • Historical │ │ • Risk       │ │ • Volatility │
    │ • Indicators │ │ • Allocation │ │ • Returns    │
    └──────────────┘ └──────────────┘ └──────────────┘
            │                │                │
            └────────────────┼────────────────┘
                             │
                        ┌────▼────┐
                        │Database │
                        │SQL Query│
                        └─────────┘
```

### Tool Execution with Retries

```
Tool Request
     │
     ▼
┌─────────────────┐
│ Validate Input  │
│ • Check params  │
│ • Type check    │
└────┬────────────┘
     │ Valid
     ▼
┌─────────────────┐
│ Execute Tool    │◄────┐
│ Attempt 1       │     │
└────┬────────────┘     │
     │                  │
     ├─ Success ────────┼────> Return Result
     │                  │
     └─ Failed          │
         │              │
         ▼              │
    ┌─────────────┐    │
    │Wait 2s      │    │
    └─────┬───────┘    │
          │            │
          ▼            │
    ┌─────────────┐    │
    │Retry (2)    │────┘
    └─────┬───────┘
          │
          ├─ Success ────────> Return Result
          │
          └─ Failed
              │
              ▼
         ┌─────────────┐
         │Wait 4s      │
         └─────┬───────┘
               │
               ▼
         ┌─────────────┐
         │Retry (3)    │
         └─────┬───────┘
               │
               ├─ Success ────> Return Result
               │
               └─ Failed
                   │
                   ▼
              Try Fallback
              Tool (if available)
                   │
                   ├─ Success ──> Return Result
                   │
                   └─ Failed ───> Raise Error
```

## Data Flow Diagrams

### Planning Phase

```
User Query ──────┐
                 │
Context ─────────┼─────> LLM Planner
                 │          │
Tool Descriptions┘          │
                            ▼
                   ┌─────────────────┐
                   │  Structured     │
                   │  JSON Plan      │
                   └────┬────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Step 1  │    │ Step 2  │    │ Step 3  │
   │ Tool A  │    │ Tool B  │    │ Tool C  │
   │ Input X │    │ Input Y │    │ Input Z │
   └─────────┘    └─────────┘    └─────────┘
```

### Execution Phase

```
Plan Steps
    │
    ▼
┌───────────────────────┐
│  Sequential Executor  │
└───────────┬───────────┘
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Tool 1 │ │ Tool 2 │ │ Tool 3 │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Result 1│ │Result 2│ │Result 3│
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               │
               ▼
        ┌──────────────┐
        │ State Update │
        └──────────────┘
               │
               ▼
        ┌──────────────┐
        │  Validation  │
        └──────────────┘
```

### Synthesis Phase

```
All Results ──────┐
                  │
Original Query ───┼───> LLM Synthesizer
                  │          │
Context ──────────┘          │
                             ▼
                    ┌────────────────┐
                    │ Natural Lang.  │
                    │    Answer      │
                    └────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Add Metadata  │
                    │ • Tools Used   │
                    │ • Confidence   │
                    │ • Duration     │
                    └────────────────┘
```

## Component Interactions

### Agent + Guardrails Interaction

```
┌──────────────┐          ┌──────────────┐
│              │  1. Check│              │
│  Orchestr... │─────────>│  Guardrails  │
│              │   Access │              │
└──────┬───────┘          └───────┬──────┘
       │                          │
       │                  2. Approved/Denied
       │<─────────────────────────┘
       │
       ▼
  3. Execute Tool
       │
       ▼
┌──────────────┐
│     Tool     │
└──────┬───────┘
       │
       │ 4. Result
       ▼
┌──────────────┐          ┌──────────────┐
│              │ 5. Log   │              │
│  Orchestr... │─────────>│  Guardrails  │
│              │   Audit  │              │
└──────────────┘          └──────────────┘
```

### State Management Flow

```
┌──────────────┐
│   Session    │
│   Created    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Tool Call 1 │────>│ State Update │
└──────────────┘     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Session     │
                     │  State       │
                     │  v1          │
                     └──────┬───────┘
                            │
┌──────────────┐            │
│  Tool Call 2 │────────────┼────> ┌──────────────┐
└──────────────┘            │      │ State Update │
                            │      └──────┬───────┘
                            │             │
                            ▼             ▼
                     ┌──────────────┐
                     │  Session     │
                     │  State       │
                     │  v2          │
                     └──────────────┘
```

## Deployment Architecture

### Cloud Deployment (AWS Example)

```
                    ┌─────────────────┐
                    │    Users        │
                    └────────┬────────┘
                             │
                             │ HTTPS
                             ▼
                    ┌─────────────────┐
                    │  API Gateway    │
                    └────────┬────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────┐
│                    VPC                             │
│                                                    │
│  ┌──────────────┐         ┌──────────────┐       │
│  │   Lambda     │         │     ECS      │       │
│  │   Function   │   or    │   Service    │       │
│  │              │         │              │       │
│  │ Agent Code   │         │ Docker Image │       │
│  └──────┬───────┘         └──────┬───────┘       │
│         │                        │               │
│         └────────┬───────────────┘               │
│                  │                               │
│         ┌────────┼────────────┐                 │
│         │        │            │                 │
│         ▼        ▼            ▼                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │Secrets  │ │DynamoDB │ │ElastiC. │          │
│  │Manager  │ │(State)  │ │(Logs)   │          │
│  └─────────┘ └─────────┘ └─────────┘          │
│                                                 │
└─────────────────────────────────────────────────┘
                  │
                  │ Outbound to:
                  ▼
         ┌─────────────────┐
         │  External APIs  │
         │  • OpenAI       │
         │  • Market Data  │
         └─────────────────┘
```

### Databricks Deployment

```
┌─────────────────────────────────────────────┐
│         Databricks Workspace               │
│                                             │
│  ┌───────────────────────────────────┐     │
│  │        MLflow Tracking            │     │
│  │  • Experiments                    │     │
│  │  • Models                         │     │
│  │  • Artifacts                      │     │
│  └───────────────────────────────────┘     │
│                                             │
│  ┌───────────────────────────────────┐     │
│  │     Model Serving Endpoint        │     │
│  │                                   │     │
│  │  ┌─────────────────────────┐     │     │
│  │  │  Investment Agent       │     │     │
│  │  │  Model (v1)             │     │     │
│  │  └─────────────────────────┘     │     │
│  └───────────────────────────────────┘     │
│                                             │
│  ┌───────────────────────────────────┐     │
│  │     Databricks SQL Warehouse     │     │
│  │  • Portfolio Data                │     │
│  │  • Transaction History           │     │
│  └───────────────────────────────────┘     │
│                                             │
│  ┌───────────────────────────────────┐     │
│  │        Delta Lake Storage         │     │
│  │  • Raw Data                       │     │
│  │  • Processed Data                │     │
│  │  • Results                        │     │
│  └───────────────────────────────────┘     │
│                                             │
└─────────────────────────────────────────────┘
```

### Monitoring Stack

```
┌──────────────────────────────────────────┐
│           Application Layer              │
│  ┌────────────────────────────────┐     │
│  │   Agent Orchestrator           │     │
│  │   • Logs Events                │     │
│  │   • Emits Metrics              │     │
│  └───────┬────────────────────────┘     │
│          │                               │
└──────────┼───────────────────────────────┘
           │
           │ Push Logs & Metrics
           │
           ▼
┌──────────────────────────────────────────┐
│        Observability Layer               │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Log Aggreg.  │  │  Metrics     │    │
│  │ (ELK/Cloud)  │  │ (Prometheus) │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   Dashboards    │             │
│         │  (Grafana/Cloud)│             │
│         └─────────────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │    Alerting     │             │
│         │ (PagerDuty/SNS) │             │
│         └─────────────────┘             │
│                                          │
└──────────────────────────────────────────┘
```

## Trace Visualization

### Sample Execution Trace

```
Query: "Calculate my portfolio's Sharpe ratio"

Timeline:
│
├─ 00:00.000  Query Received
│              └─ Context: {"portfolio_id": "001"}
│
├─ 00:00.050  Planning Started
│              └─ LLM: GPT-4
│
├─ 00:01.200  Planning Complete
│              └─ Steps: 3
│
├─ 00:01.250  Step 1: portfolio_summary
│              ├─ Guardrail Check: ✓ Passed
│              ├─ Execution: 150ms
│              └─ Result: Portfolio data retrieved
│
├─ 00:01.450  Step 2: get_historical_data
│              ├─ Guardrail Check: ✓ Passed
│              ├─ Execution: 200ms
│              └─ Result: 252 data points
│
├─ 00:01.700  Step 3: calculate_sharpe_ratio
│              ├─ Guardrail Check: ✓ Passed
│              ├─ Execution: 50ms
│              └─ Result: 1.45
│
├─ 00:01.750  Validation
│              └─ Confidence: 0.92
│
├─ 00:01.800  Synthesis Started
│
├─ 00:02.500  Synthesis Complete
│              └─ Answer Generated
│
└─ 00:02.550  Query Complete
               ├─ Duration: 2.55s
               ├─ Tools Used: 3
               └─ Tokens: 850

Result: "Your portfolio's Sharpe ratio is 1.45, indicating
strong risk-adjusted returns. This is above the typical
threshold of 1.0 for good performance."
```

## Error Handling Flow

```
Tool Execution
     │
     ▼
┌─────────────┐
│  Try Call   │
└─────┬───────┘
      │
      ├─ Success ──────────────────> Continue
      │
      └─ Error
          │
          ▼
     ┌─────────────┐
     │Log Error    │
     └─────┬───────┘
           │
           ▼
     ┌─────────────┐
     │Check Retry  │
     │Policy       │
     └─────┬───────┘
           │
           ├─ Retry ────────> Wait + Retry
           │
           └─ No Retry
               │
               ▼
          ┌─────────────┐
          │Try Fallback │
          │Tool         │
          └─────┬───────┘
                │
                ├─ Success ──> Continue
                │
                └─ Failed
                    │
                    ▼
               ┌─────────────┐
               │Mark Step    │
               │Failed       │
               └─────┬───────┘
                     │
                     ▼
                Continue with
                Remaining Steps
```

---

These diagrams provide a comprehensive visual understanding of the system's architecture, flows, and interactions. For implementation details, refer to the Architecture Guide and code documentation.
