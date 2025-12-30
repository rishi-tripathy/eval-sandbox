from typing import Any, List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class ExecutionStep(BaseModel):
    step: str #draft, eval_initial, repair, eval_repair
    input: Any
    output: Any
    duration_ms: int
    tool_usage: Optional[Dict[str, int]] = None  # Tool breakdown for this step

class Trace(BaseModel):
    run_id: str
    session_id: str
    task_id: str
    task_name: str
    timestamp: datetime
    model: str  # Agent type (claude, claude-tools, stub)
    model_name: Optional[str] = None  # Specific Claude model (claude-3-5-haiku-20241022)
    prompt: str
    execution_steps: List[ExecutionStep]
    final_result: Optional[Any] = None