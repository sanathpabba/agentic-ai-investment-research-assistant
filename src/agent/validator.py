"""
Result Validator - Validates execution results for correctness and completeness.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation process."""
    is_valid: bool
    confidence: float
    issues: List[str]
    warnings: List[str]


class ResultValidator:
    """Validates results from tool executions."""
    
    def validate_execution(
        self,
        query: str,
        execution_results: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate execution results.
        
        Args:
            query: Original query
            execution_results: List of execution steps
            context: Additional context
        
        Returns:
            ValidationResult with validation status
        """
        issues = []
        warnings = []
        
        # Check if any steps succeeded
        successful_steps = [s for s in execution_results if s.status == "success"]
        if not successful_steps:
            issues.append("No steps completed successfully")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                issues=issues,
                warnings=warnings
            )
        
        # Check for critical failures
        critical_failures = [
            s for s in execution_results 
            if s.status == "failed" and not s.allow_retry
        ]
        if critical_failures:
            issues.append(f"{len(critical_failures)} critical steps failed")
        
        # Validate result types
        for step in successful_steps:
            if step.result is None:
                warnings.append(f"Step {step.step_id} returned None")
        
        # Calculate confidence
        success_rate = len(successful_steps) / len(execution_results)
        confidence = success_rate * 0.9 if not issues else success_rate * 0.5
        
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            issues=issues,
            warnings=warnings
        )
