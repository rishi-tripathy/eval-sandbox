from pydantic import BaseModel
from typing import Optional, Dict
from workbench.types import InvariantType, MonthlyRecord
from typing import List

class Expected(BaseModel):
    initial_verdict: str
    first_violation_month: Optional[str] = None
    violated_invariant: Optional[InvariantType] = None
    ledger: Optional[List[MonthlyRecord]] = None
class Limits(BaseModel):
    max_tool_calls: Optional[int] = 10
    max_repairs: Optional[int] = 1

class Task(BaseModel):
    id: str
    title: str
    mode: str = 'fast' # 'fast' or 'strict'
    prompt: str
    limits: Limits = Limits()
    generate_ledger: bool = False
    expected: Optional[Expected] = None

from enum import Enum

class ErrorCategory(Enum):
    INVALID_JSON = "INVALID_JSON"  # agent produced unparsable JSON
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"  # fails scenario schema / sign rules
    TOOL_CALL_HALLUCINATION = "TOOL_CALL_HALLUCINATION"  # agent claims eval result not present in trace
    EXCEEDED_MAX_TOOL_CALLS = "EXCEEDED_MAX_TOOL_CALLS"  # tool calls exceeded
    REPAIR_FAILED = "REPAIR_FAILED"  # repair attempt did not improve feasibility/min_cash
    EXCEEDED_MAX_REPAIRS = "EXCEEDED_MAX_REPAIRS"  # repair attempts exceeded
    WRONG_VERDICT = "WRONG_VERDICT"  # fixture-only
    WRONG_FIRST_VIOLATION_MONTH = "WRONG_FIRST_VIOLATION_MONTH"  # fixture-only
    WRONG_VIOLATION = "WRONG_VIOLATION"  # fixture-only
    EARLY_STOP = "EARLY_STOP"  # stopped before running run_eval at least once
    INACCURATE_REPAIR_LABEL = "INACCURATE_REPAIR_LABEL"  # repair label does not match issued repair type
class TaskResult(BaseModel):
    task_id: str
    scenario_json: str = None
    repair_json: Optional[str] = None
    draft_ledger_json: Optional[str] = None
    repair_ledger_json: Optional[str] = None
    
    # Run results
    initial_verdict: str
    final_verdict: str
    first_violation_month: Optional[str] = None
    violated_invariant: Optional[InvariantType] = None
    
    # Metrics
    tool_calls: int = 0
    repair_attempts: int = 0
    tool_details: Optional[Dict[str, int]] = None  # {"calculate": 3, "validate_monthly_record": 2}

    # Scoring
    verdict_correct: Optional[bool] = None
    first_violation_month_correct: Optional[bool] = None
    violation_correct: Optional[bool] = None
    draft_ledger_correct: Optional[bool] = None
    
    repair_attempted: bool = False
    repair_made_feasible: Optional[bool] = None
    repair_strategy: Optional[str] = None
    repair_ledger_correct: Optional[bool] = None
    repair_label_accurate: Optional[bool] = None

    #Taxonomy
    error_category: Optional[ErrorCategory] = None
    
    # Overall scoring
    score_earned: Optional[int] = None
    score_possible: Optional[int] = None
    score_percentage: Optional[float] = None
    
    # Comparison metadata (optional, for comparison framework)
    condition_model: Optional[str] = None  # Agent type (claude, claude-tools, stub)
    condition_model_name: Optional[str] = None  # Specific Claude model name
    condition_task_set: Optional[str] = None
    condition_run_number: Optional[int] = None
    condition_id: Optional[str] = None
    condition_model_index: Optional[int] = None