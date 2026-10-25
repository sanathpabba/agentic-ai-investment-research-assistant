"""
Agent Orchestrator - Main controller for the agentic AI system.

This module implements the core orchestration logic that coordinates planning,
tool execution, validation, and response generation.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from .planner import TaskPlanner
from .executor import ToolExecutor
from .validator import ResultValidator
from ..tools.registry import ToolRegistry
from ..utils.state_manager import StateManager
from ..utils.observability import ObservabilityTracker
from ..utils.guardrails import Guardrails

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Response from agent execution."""
    answer: str
    tools_used: List[str]
    confidence: float
    execution_time: float
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    token_usage: Dict[str, int] = field(default_factory=dict)


@dataclass
class ExecutionStep:
    """Represents a single execution step in the agent workflow."""
    step_id: int
    action: str
    tool_name: str
    tool_input: Dict[str, Any]
    result: Optional[Any] = None
    status: str = "pending"  # pending, success, failed, skipped
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class AgentOrchestrator:
    """
    Main orchestrator for the agentic AI system.
    
    Coordinates planning, execution, validation, and response generation
    across multiple tools and workflows.
    """
    
    def __init__(
        self,
        tools: ToolRegistry,
        llm_provider: str = "openai",
        model_name: str = "gpt-4-turbo-preview",
        max_iterations: int = 10,
        enable_human_in_loop: bool = False,
        observability: Optional[ObservabilityTracker] = None
    ):
        """
        Initialize the agent orchestrator.
        
        Args:
            tools: Registry of available tools
            llm_provider: LLM provider (openai, anthropic)
            model_name: Model to use for reasoning
            max_iterations: Maximum planning/execution iterations
            enable_human_in_loop: Enable human approval gates
            observability: Observability tracker instance
        """
        self.tools = tools
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.enable_human_in_loop = enable_human_in_loop
        
        # Initialize components
        self.planner = TaskPlanner(
            llm_provider=llm_provider,
            model_name=model_name,
            tools=tools
        )
        self.executor = ToolExecutor(tools=tools)
        self.validator = ResultValidator()
        self.state_manager = StateManager()
        self.guardrails = Guardrails(tools=tools)
        self.observability = observability or ObservabilityTracker()
        
        logger.info(
            f"AgentOrchestrator initialized with {llm_provider}/{model_name}"
        )
    
    def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> AgentResponse:
        """
        Execute a user query using the agentic workflow.
        
        Args:
            query: User's analytical query
            context: Additional context (portfolio data, preferences, etc.)
            session_id: Session identifier for state management
        
        Returns:
            AgentResponse with answer and metadata
        """
        start_time = datetime.now()
        trace_id = self.observability.start_trace(query)
        
        try:
            logger.info(f"Starting execution for query: {query[:100]}...")
            
            # Load or create session state
            if session_id:
                state = self.state_manager.load_state(session_id)
            else:
                state = self.state_manager.create_state(query, context)
            
            # Step 1: Plan the task
            logger.info("Planning task...")
            plan = self.planner.create_plan(query, context, state)
            self.observability.log_event(trace_id, "planning_complete", {
                "num_steps": len(plan.steps),
                "approach": plan.strategy
            })
            
            # Step 2: Execute plan steps
            logger.info(f"Executing plan with {len(plan.steps)} steps...")
            execution_results = []
            
            for step in plan.steps:
                # Check guardrails
                if not self.guardrails.validate_tool_access(
                    step.tool_name,
                    step.tool_input,
                    context
                ):
                    logger.warning(f"Guardrail blocked: {step.tool_name}")
                    step.status = "blocked"
                    continue
                
                # Human approval if required
                if self.enable_human_in_loop and step.requires_approval:
                    approval = self._request_human_approval(step)
                    if not approval:
                        logger.info(f"Human rejected step: {step.action}")
                        step.status = "rejected"
                        continue
                
                # Execute tool
                try:
                    logger.info(f"Executing: {step.tool_name}")
                    result = self.executor.execute_tool(
                        step.tool_name,
                        step.tool_input,
                        state
                    )
                    step.result = result
                    step.status = "success"
                    
                    self.observability.log_tool_call(
                        trace_id,
                        step.tool_name,
                        step.tool_input,
                        result
                    )
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    step.status = "failed"
                    step.error = str(e)
                    
                    # Attempt retry with fallback
                    if step.allow_retry:
                        logger.info("Attempting retry...")
                        result = self._retry_with_fallback(step, state)
                        if result:
                            step.result = result
                            step.status = "success"
                
                execution_results.append(step)
                
                # Update state
                self.state_manager.update_state(
                    state.session_id,
                    step.tool_name,
                    step.result
                )
            
            # Step 3: Validate results
            logger.info("Validating results...")
            validation = self.validator.validate_execution(
                query,
                execution_results,
                context
            )
            
            if not validation.is_valid:
                logger.warning(f"Validation issues: {validation.issues}")
            
            # Step 4: Generate final response
            logger.info("Generating response...")
            answer = self.planner.synthesize_response(
                query,
                execution_results,
                validation
            )
            
            # Collect metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            tools_used = [s.tool_name for s in execution_results if s.status == "success"]
            
            self.observability.end_trace(trace_id, {
                "execution_time": execution_time,
                "tools_used": tools_used,
                "confidence": validation.confidence
            })
            
            response = AgentResponse(
                answer=answer,
                tools_used=tools_used,
                confidence=validation.confidence,
                execution_time=execution_time,
                intermediate_results={s.tool_name: s.result for s in execution_results},
                trace_id=trace_id,
                token_usage=self.observability.get_token_usage(trace_id)
            )
            
            logger.info(f"Execution complete in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Orchestrator execution failed: {e}", exc_info=True)
            self.observability.log_error(trace_id, str(e))
            raise
    
    def _request_human_approval(self, step: ExecutionStep) -> bool:
        """
        Request human approval for a step (simulation).
        
        In production, this would integrate with a UI or notification system.
        """
        # For demonstration, we auto-approve low-risk operations
        high_risk_tools = ["execute_trade", "modify_portfolio", "update_database"]
        
        if step.tool_name in high_risk_tools:
            logger.warning(f"High-risk operation requires approval: {step.tool_name}")
            # In real system: send notification, wait for response
            return False
        
        return True
    
    def _retry_with_fallback(
        self,
        step: ExecutionStep,
        state: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Retry failed step with fallback strategy.
        
        Attempts alternative tools or simplified inputs.
        """
        # Get alternative tools
        alternatives = self.tools.get_alternative_tools(step.tool_name)
        
        for alt_tool in alternatives:
            try:
                logger.info(f"Trying fallback: {alt_tool}")
                result = self.executor.execute_tool(
                    alt_tool,
                    step.tool_input,
                    state
                )
                return result
            except Exception as e:
                logger.warning(f"Fallback {alt_tool} failed: {e}")
                continue
        
        return None
    
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Get complete trace for a query execution."""
        return self.observability.get_trace(trace_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all executions."""
        return self.observability.get_metrics()
