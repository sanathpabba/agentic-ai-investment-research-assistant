"""
Observability - Tracking and monitoring for agent execution.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    """A single event in an execution trace."""
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]


@dataclass
class ExecutionTrace:
    """Complete trace of an agent execution."""
    trace_id: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[TraceEvent] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class ObservabilityTracker:
    """
    Tracks agent execution for observability.
    
    Provides:
    - Execution traces
    - Tool call logging
    - Token usage tracking
    - Latency monitoring
    - Error tracking
    """
    
    def __init__(self):
        """Initialize observability tracker."""
        self.traces: Dict[str, ExecutionTrace] = {}
        self.global_metrics: Dict[str, Any] = {
            "total_queries": 0,
            "total_tool_calls": 0,
            "total_tokens": 0,
            "total_errors": 0,
            "avg_latency": 0.0
        }
    
    def start_trace(self, query: str) -> str:
        """
        Start a new execution trace.
        
        Args:
            query: User query
        
        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())
        
        trace = ExecutionTrace(
            trace_id=trace_id,
            query=query,
            start_time=datetime.now()
        )
        
        self.traces[trace_id] = trace
        self.global_metrics["total_queries"] += 1
        
        logger.info(f"Started trace {trace_id}")
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        final_metrics: Optional[Dict[str, Any]] = None
    ):
        """
        End an execution trace.
        
        Args:
            trace_id: Trace ID
            final_metrics: Final metrics to record
        """
        if trace_id not in self.traces:
            logger.error(f"Unknown trace ID: {trace_id}")
            return
        
        trace = self.traces[trace_id]
        trace.end_time = datetime.now()
        
        if final_metrics:
            trace.metrics.update(final_metrics)
        
        # Calculate duration
        duration = (trace.end_time - trace.start_time).total_seconds()
        trace.metrics["duration_seconds"] = duration
        
        # Update global metrics
        self._update_global_metrics(trace)
        
        logger.info(f"Ended trace {trace_id} (duration: {duration:.2f}s)")
    
    def log_event(
        self,
        trace_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """
        Log an event in a trace.
        
        Args:
            trace_id: Trace ID
            event_type: Type of event
            data: Event data
        """
        if trace_id not in self.traces:
            logger.error(f"Unknown trace ID: {trace_id}")
            return
        
        event = TraceEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            data=data
        )
        
        self.traces[trace_id].events.append(event)
        logger.debug(f"Logged event {event_type} for trace {trace_id}")
    
    def log_tool_call(
        self,
        trace_id: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        result: Any
    ):
        """
        Log a tool call.
        
        Args:
            trace_id: Trace ID
            tool_name: Tool name
            tool_input: Tool input
            result: Tool result
        """
        self.log_event(trace_id, "tool_call", {
            "tool": tool_name,
            "input": str(tool_input)[:200],  # Truncate
            "success": result is not None
        })
        
        self.global_metrics["total_tool_calls"] += 1
    
    def log_error(
        self,
        trace_id: str,
        error: str
    ):
        """
        Log an error.
        
        Args:
            trace_id: Trace ID
            error: Error message
        """
        self.log_event(trace_id, "error", {
            "error": error
        })
        
        self.global_metrics["total_errors"] += 1
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete trace data.
        
        Args:
            trace_id: Trace ID
        
        Returns:
            Trace data as dict
        """
        if trace_id not in self.traces:
            return None
        
        trace = self.traces[trace_id]
        
        return {
            "trace_id": trace.trace_id,
            "query": trace.query,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.event_type,
                    "data": e.data
                }
                for e in trace.events
            ],
            "metrics": trace.metrics
        }
    
    def get_token_usage(self, trace_id: str) -> Dict[str, int]:
        """
        Get token usage for a trace.
        
        Args:
            trace_id: Trace ID
        
        Returns:
            Token usage stats
        """
        # Mock token counting
        # In production: track actual LLM token usage
        return {
            "prompt_tokens": 500,
            "completion_tokens": 300,
            "total_tokens": 800
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get global metrics.
        
        Returns:
            Aggregated metrics
        """
        return self.global_metrics.copy()
    
    def _update_global_metrics(self, trace: ExecutionTrace):
        """Update global metrics from completed trace."""
        if "duration_seconds" in trace.metrics:
            # Update average latency
            total_queries = self.global_metrics["total_queries"]
            old_avg = self.global_metrics["avg_latency"]
            new_duration = trace.metrics["duration_seconds"]
            
            self.global_metrics["avg_latency"] = (
                (old_avg * (total_queries - 1) + new_duration) / total_queries
            )
        
        # Update token counts
        if "token_usage" in trace.metrics:
            self.global_metrics["total_tokens"] += trace.metrics["token_usage"].get("total_tokens", 0)
    
    def export_traces(
        self,
        output_format: str = "json"
    ) -> str:
        """
        Export all traces.
        
        Args:
            output_format: Export format (json, csv)
        
        Returns:
            Exported data as string
        """
        if output_format == "json":
            import json
            traces_data = [
                self.get_trace(trace_id)
                for trace_id in self.traces.keys()
            ]
            return json.dumps(traces_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
