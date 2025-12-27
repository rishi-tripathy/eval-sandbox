from typing import Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class ExecutionStep(BaseModel):
    step: str #draft, eval_initial, repair, eval_repair
    input: Any
    output: Any
    duration_ms: int

class Trace(BaseModel):
    run_id: str
    session_id: str
    task_id: str
    task_name: str
    timestamp: datetime
    model: str
    prompt: str
    execution_steps: List[ExecutionStep]
    final_result: Optional[Any] = None