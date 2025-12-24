from workbench.task_types import Task, TaskResult
from workbench.types import Scenario
from workbench.models.agents import get_agent
from workbench.eval import run_eval
import json
from workbench.task_types import ErrorCategory
from workbench.trace_types import Trace, ExecutionStep
from datetime import datetime
import time
import uuid
import os
from json_diff import json_diff


def run_task(task_path: str, model: str = "stub", session_id: str = None) -> TaskResult:
    task = Task.model_validate_json(open(task_path).read())
    if session_id is None:
          session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    trace = init_trace(task.id, model, task.prompt, session_id)
    
    agent = get_agent(model)
    tool_calls = 0
    repair_attempts = 0

    # Try to draft scenario
    try:
        start_time = time.time()
        scenario_json = agent.draft(task.prompt, task.mode)
        duration_ms = int((time.time()-start_time)*1000)

        trace.execution_steps.append(ExecutionStep(
            step="draft",
            input=task.prompt,
            output=scenario_json,
            duration_ms=duration_ms
        ))
        tool_calls += 1
        
        # Try to parse JSON
        try:
            json.loads(scenario_json)
        except json.JSONDecodeError:
            write_trace(trace)
            return TaskResult(
                task_id=task.id,
                scenario_json={},
                initial_verdict="error",
                final_verdict="error",
                tool_calls=tool_calls,
                error_category=ErrorCategory.INVALID_JSON
            )
        
        # Try to validate schema
        scenario = Scenario.model_validate_json(scenario_json)
    except Exception as e:
        write_trace(trace)
        return TaskResult(
            task_id=task.id,
            scenario_json={},
            initial_verdict="error",
            final_verdict="error",
            tool_calls=tool_calls,
            error_category=ErrorCategory.SCHEMA_MISMATCH
        )
    
    start_time = time.time()
    eval_result = run_eval(scenario)
    duration_ms = int((time.time()-start_time)*1000)

    trace.execution_steps.append(ExecutionStep(
        step="eval_initial",
        input=scenario_json,
        output=eval_result,
        duration_ms=duration_ms
    ))

    repair_json = None
    final_result = eval_result

    if eval_result.verdict == "infeasible": #begin repair loop
        start_time = time.time()
        repair_data = agent.repair(scenario_json, eval_result)
        try:
            repair_json = json.loads(repair_data)
            repair_type = repair_json.get("repair_applied").get("type")
            repair_scenario_json = json.dumps(repair_json.get("repaired_scenario"))
        except Exception as e:
            write_trace(trace)
            return TaskResult(
                task_id=task.id,
                scenario_json={},
                initial_verdict="error",
                final_verdict="error",
                tool_calls=tool_calls,
                error_category=ErrorCategory.INVALID_JSON
            )
        
        if repair_type not in ["baseline_reduction", "event_amount_adjustment", "event_timing_shift"]:
            write_trace(trace)
            return TaskResult(
                task_id=task.id,
                scenario_json={},
                initial_verdict="error",
                final_verdict="error",
                tool_calls=tool_calls,
                error_category=ErrorCategory.INACCURATE_REPAIR_LABEL
            )
        
        if not validate_repair_claim(scenario_json, repair_scenario_json, repair_type):
            write_trace(trace)
            return TaskResult(
                task_id=task.id,
                scenario_json={},
                initial_verdict="error",
                final_verdict="error",
                tool_calls=tool_calls,
                error_category=ErrorCategory.INACCURATE_REPAIR_LABEL
            )

        duration_ms = int((time.time()-start_time)*1000)

        trace.execution_steps.append(ExecutionStep(
            step="repair",
            input=scenario_json,
            output=repair_scenario_json,
            duration_ms=duration_ms
        ))

        tool_calls += 1
        repair_attempts += 1
        if repair_json:
            try:
                scenario = Scenario.model_validate_json(repair_scenario_json)
            except Exception as e:
                write_trace(trace)
                return TaskResult(
                    task_id=task.id,
                    scenario_json={},
                    initial_verdict="error",
                    final_verdict="error",
                    tool_calls=tool_calls,
                    error_category=ErrorCategory.SCHEMA_MISMATCH
                )
            start_time = time.time()
            final_result = run_eval(scenario)
            duration_ms = int((time.time()-start_time)*1000)

            trace.execution_steps.append(ExecutionStep(
                step="eval_repair",
                input=repair_json,
                output=final_result,
                duration_ms=duration_ms
            ))

    task_result = TaskResult(
        task_id=task.id,
        scenario_json=json.loads(scenario_json),
        repair_json=json.loads(repair_json) if repair_json else None,
        initial_verdict=eval_result.verdict,
        final_verdict=final_result.verdict,
        first_violation_month=final_result.first_violation_month,
        violated_invariant=final_result.violated_invariant,
        tool_calls=tool_calls,
        repair_attempts=repair_attempts,
        verdict_correct=eval_result.verdict == task.expected.initial_verdict if task.expected else None,
        first_violation_month_correct=eval_result.first_violation_month == task.expected.first_violation_month if task.expected else None,
        violation_correct=eval_result.violated_invariant == task.expected.violated_invariant if task.expected else None,
        repair_attempted=repair_json is not None,
        repair_made_feasible=final_result.verdict == "feasible",
        error_category=None
    )

    if tool_calls == 0:
        task_result.error_category = ErrorCategory.NO_TOOL_USE

    elif tool_calls > task.limits.max_tool_calls:
        task_result.error_category = ErrorCategory.EXCEEDED_MAX_TOOL_CALLS
    
    elif repair_attempts > task.limits.max_repairs:
        task_result.error_category = ErrorCategory.EXCEEDED_MAX_REPAIRS

    elif eval_result.verdict == "infeasible" and task_result.final_verdict == "infeasible" and task_result.repair_made_feasible is False:
        task_result.error_category = ErrorCategory.REPAIR_FAILED

    elif task_result.verdict_correct is not None and task_result.verdict_correct is False:
        task_result.error_category = ErrorCategory.WRONG_VERDICT
    
    elif task_result.first_violation_month_correct is not None and task_result.first_violation_month_correct is False:
        task_result.error_category = ErrorCategory.WRONG_FIRST_VIOLATION_MONTH
    
    elif task_result.violation_correct is not None and task_result.violation_correct is False:
        task_result.error_category = ErrorCategory.WRONG_VIOLATION
    
    trace.final_result = task_result.model_dump()
    write_trace(trace)
    return task_result

def init_trace(task_id: str, model: str, prompt: str, session_id: str) -> Trace:
    return Trace(
        run_id=str(uuid.uuid4()),
        session_id=session_id,
        task_id=task_id,
        timestamp=datetime.now(),
        model=model,
        prompt=prompt,
        execution_steps=[],
        final_result=None
    )

def write_trace(trace: Trace):
    os.makedirs(f"traces/{trace.session_id}", exist_ok=True)  # Add this line
    with open(f"traces/{trace.session_id}/{trace.run_id}.json", "w") as f: f.write(trace.model_dump_json(indent=2))
    return
    
def validate_repair_claim(original_json: str, repaired_json: str, claimed_type: str) -> bool:
    original = json.loads(original_json)
    repaired = json.loads(repaired_json)

    if claimed_type == "baseline_reduction":
      # Outflows must change
      if original["base_monthly"]["outflows"] == repaired["base_monthly"]["outflows"]:
          return False

      # Check all top-level fields except base_monthly
      for field in ["id", "title", "start_month", "horizon_months", "initial_state", "events"]:
          if original.get(field) != repaired.get(field):
              return False

      # Check base_monthly.takehome_salary stayed the same
      if original["base_monthly"]["takehome_salary"] != repaired["base_monthly"]["takehome_salary"]:
          return False

      return True
    
    elif claimed_type == "event_amount_adjustment":
      # First, check same number of events
      if len(original["events"]) != len(repaired["events"]):
          return False

      # Count how many events have different amounts
      changes_count = 0
      for i in range(len(original["events"])):
          orig_event = original["events"][i]
          rep_event = repaired["events"][i]
        
          # Check if amount changed signs
          if orig_event["amount"] * rep_event["amount"] < 0:
              return False

          # Check if amount changed
          if orig_event["amount"] != rep_event["amount"]:
              changes_count += 1

          # Check all other fields stayed the same
          for field in ["label", "start_month", "duration_months"]:
              if field in orig_event:  # Handle optional fields
                  if orig_event.get(field) != rep_event.get(field):
                      return False

      # Exactly one event should have changed amount
      return changes_count == 1
    
    elif claimed_type == "event_timing_shift":
      # First, check same number of events
      if len(original["events"]) != len(repaired["events"]):
          return False

      # Count how many events have different start months
      changes_count = 0
      for i in range(len(original["events"])):
          orig_event = original["events"][i]
          rep_event = repaired["events"][i]

          # Check if start month changed
          if orig_event["start_month"] != rep_event["start_month"]:
              changes_count += 1

          # Check all other fields stayed the same
          for field in ["label", "amount", "duration_months"]:
              if field in orig_event:  # Handle optional fields
                  if orig_event.get(field) != rep_event.get(field):
                      return False

      # Exactly one event should have changed start month
      return changes_count == 1