"""
Task Planner - Breaks down complex queries into executable steps.

Uses LLM reasoning to create multi-step analytical plans.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PlanStrategy(Enum):
    """Planning strategies for different query types."""
    SEQUENTIAL = "sequential"  # Execute steps in order
    PARALLEL = "parallel"  # Execute independent steps in parallel
    ADAPTIVE = "adaptive"  # Adjust based on intermediate results


@dataclass
class PlanStep:
    """A single step in the execution plan."""
    step_id: int
    action: str
    tool_name: str
    tool_input: Dict[str, Any]
    depends_on: List[int] = field(default_factory=list)
    requires_approval: bool = False
    allow_retry: bool = True
    priority: int = 1


@dataclass
class ExecutionPlan:
    """Complete execution plan for a query."""
    query: str
    strategy: PlanStrategy
    steps: List[PlanStep]
    estimated_duration: float = 0.0
    confidence: float = 1.0


class TaskPlanner:
    """
    Plans analytical tasks by decomposing queries into tool calls.
    
    Uses LLM reasoning to understand user intent and create
    optimal execution sequences.
    """
    
    SYSTEM_PROMPT = """You are an expert investment analyst AI that plans analytical workflows.

Given a user query, break it down into a sequence of tool calls that will answer the question.

Available tools:
{tool_descriptions}

Create a step-by-step plan that:
1. Identifies required data sources
2. Performs necessary calculations
3. Retrieves supporting information
4. Validates intermediate results
5. Synthesizes a comprehensive answer

Output your plan as a structured JSON with steps, each containing:
- action: description of what this step does
- tool_name: name of the tool to use
- tool_input: parameters for the tool
- depends_on: list of step IDs this depends on
- requires_approval: whether human approval is needed
"""
    
    def __init__(
        self,
        llm_provider: str,
        model_name: str,
        tools: Any
    ):
        """
        Initialize the task planner.
        
        Args:
            llm_provider: LLM provider (openai, anthropic)
            model_name: Model to use
            tools: Tool registry
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.tools = tools
        
        # Initialize LLM client
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM client based on provider."""
        if self.llm_provider == "openai":
            from openai import OpenAI
            self.llm_client = OpenAI()
        elif self.llm_provider == "anthropic":
            from anthropic import Anthropic
            self.llm_client = Anthropic()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def create_plan(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan for a query.
        
        Args:
            query: User's analytical query
            context: Additional context
            state: Current conversation state
        
        Returns:
            ExecutionPlan with steps to execute
        """
        logger.info(f"Creating plan for: {query[:100]}...")
        
        # Get tool descriptions
        tool_descriptions = self._format_tool_descriptions()
        
        # Build prompt
        prompt = self._build_planning_prompt(query, context, tool_descriptions)
        
        # Get plan from LLM
        try:
            if self.llm_provider == "openai":
                plan_response = self._call_openai(prompt)
            else:
                plan_response = self._call_anthropic(prompt)
            
            # Parse plan
            plan = self._parse_plan_response(query, plan_response)
            
            logger.info(f"Created plan with {len(plan.steps)} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Fallback to simple plan
            return self._create_fallback_plan(query, context)
    
    def _build_planning_prompt(
        self,
        query: str,
        context: Optional[Dict[str, Any]],
        tool_descriptions: str
    ) -> str:
        """Build the planning prompt."""
        prompt = self.SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions)
        prompt += f"\n\nUser Query: {query}\n"
        
        if context:
            prompt += f"\nAvailable Context:\n{self._format_context(context)}\n"
        
        prompt += "\nProvide a detailed execution plan:"
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API for planning."""
        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API for planning."""
        response = self.llm_client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.content[0].text
    
    def _parse_plan_response(
        self,
        query: str,
        response: str
    ) -> ExecutionPlan:
        """Parse LLM response into ExecutionPlan."""
        import json
        
        try:
            plan_data = json.loads(response)
            steps = []
            
            for i, step_data in enumerate(plan_data.get("steps", [])):
                step = PlanStep(
                    step_id=i,
                    action=step_data.get("action", ""),
                    tool_name=step_data.get("tool_name", ""),
                    tool_input=step_data.get("tool_input", {}),
                    depends_on=step_data.get("depends_on", []),
                    requires_approval=step_data.get("requires_approval", False),
                    allow_retry=step_data.get("allow_retry", True)
                )
                steps.append(step)
            
            strategy = PlanStrategy(
                plan_data.get("strategy", PlanStrategy.SEQUENTIAL.value)
            )
            
            return ExecutionPlan(
                query=query,
                strategy=strategy,
                steps=steps,
                confidence=plan_data.get("confidence", 0.9)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse plan: {e}")
            return self._create_fallback_plan(query, None)
    
    def _create_fallback_plan(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> ExecutionPlan:
        """
        Create a simple fallback plan when LLM planning fails.
        
        Uses keyword matching to select relevant tools.
        """
        logger.warning("Using fallback plan")
        
        steps = []
        query_lower = query.lower()
        
        # Simple keyword-based tool selection
        if "sharpe" in query_lower or "risk" in query_lower:
            steps.append(PlanStep(
                step_id=0,
                action="Calculate portfolio risk metrics",
                tool_name="portfolio_risk_metrics",
                tool_input={"metrics": ["sharpe_ratio", "volatility"]}
            ))
        
        if "price" in query_lower or "stock" in query_lower:
            steps.append(PlanStep(
                step_id=len(steps),
                action="Get market data",
                tool_name="get_market_data",
                tool_input={"symbols": self._extract_symbols(query)}
            ))
        
        if "benchmark" in query_lower or "compare" in query_lower:
            steps.append(PlanStep(
                step_id=len(steps),
                action="Compare to benchmark",
                tool_name="benchmark_comparison",
                tool_input={"benchmark": "SPY"}
            ))
        
        # Default step if no matches
        if not steps:
            steps.append(PlanStep(
                step_id=0,
                action="Get portfolio summary",
                tool_name="portfolio_summary",
                tool_input={}
            ))
        
        return ExecutionPlan(
            query=query,
            strategy=PlanStrategy.SEQUENTIAL,
            steps=steps,
            confidence=0.6
        )
    
    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for prompt."""
        descriptions = []
        for tool_name, tool in self.tools.get_all_tools().items():
            desc = f"- {tool_name}: {tool.description}"
            descriptions.append(desc)
        return "\n".join(descriptions)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for prompt."""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query (simple version)."""
        import re
        # Look for uppercase sequences (common for tickers)
        symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        return symbols[:10]  # Limit to 10
    
    def synthesize_response(
        self,
        query: str,
        execution_results: List[Any],
        validation: Any
    ) -> str:
        """
        Synthesize final response from execution results.
        
        Args:
            query: Original user query
            execution_results: Results from all steps
            validation: Validation results
        
        Returns:
            Natural language answer
        """
        # Collect successful results
        results_text = []
        for step in execution_results:
            if step.status == "success" and step.result:
                results_text.append(f"{step.action}: {step.result}")
        
        # Build synthesis prompt
        prompt = f"""Given the user query and execution results, provide a comprehensive answer.

Query: {query}

Execution Results:
{chr(10).join(results_text)}

Validation Confidence: {validation.confidence:.2f}

Provide a clear, analytical answer that directly addresses the user's question.
Include specific numbers and insights from the results.
"""
        
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a financial analyst providing investment insights."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content
            else:
                response = self.llm_client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Response synthesis failed: {e}")
            # Fallback to simple summary
            return self._simple_summary(execution_results)
    
    def _simple_summary(self, execution_results: List[Any]) -> str:
        """Create a simple summary when LLM synthesis fails."""
        summary_parts = []
        for step in execution_results:
            if step.status == "success":
                summary_parts.append(f"✓ {step.action}")
        
        return "Analysis complete:\n" + "\n".join(summary_parts)
