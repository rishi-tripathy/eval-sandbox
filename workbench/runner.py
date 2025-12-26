from workbench.task_types import Task, TaskResult
from workbench.types import Scenario, MonthlyRecord
from workbench.models.agents import get_agent
from workbench.eval import run_eval
from workbench.scoring import update_result_with_score
from typing import List, Optional
import json
from workbench.task_types import ErrorCategory
from workbench.trace_types import Trace, ExecutionStep
from datetime import datetime
import time
import uuid
import os


def run_task(task_path: str, model: str = "claude", session_id: str = None, prompt_dir: str = "prompts/v2", model_name: str = None) -> TaskResult:
    task = Task.model_validate_json(open(task_path).read())
    if session_id is None:
          session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    trace = init_trace(task.id, model, task.prompt, session_id)    
    agent = get_agent(model)

    draft_ledger_json = None
    repair_ledger_json = None

    result = TaskResult( 
        task_id=task.id,
        initial_verdict="error",
        final_verdict="error",
    )
    
    # Try to draft scenario
    try:
        start_time = time.time()
        draft_data = agent.draft(task.prompt, task.mode, task.generate_ledger, prompt_dir, model_name)
        duration_ms = int((time.time()-start_time)*1000)

        trace.execution_steps.append(ExecutionStep(
            step="draft",
            input=task.prompt,
            output=draft_data,
            duration_ms=duration_ms
        ))
        result.tool_calls += 1
        
        # Parse draft JSON
        try:
            draft_parsed = json.loads(draft_data)
            if task.generate_ledger:
                draft_scenario_json = draft_parsed["scenario"]
                draft_ledger_json = draft_parsed.get("ledger")
                if draft_ledger_json:
                    result.draft_ledger_json = json.dumps(draft_ledger_json)
            else:
                draft_scenario_json = draft_parsed
            result.scenario_json = json.dumps(draft_scenario_json)
        except Exception as e:
            write_trace(trace)
            result.error_category = ErrorCategory.INVALID_JSON
            return result
            
        
        # Try to validate schema
        scenario = Scenario.model_validate(draft_scenario_json)
        if draft_ledger_json:
            draft_ledger = [MonthlyRecord.model_validate(record) for record in draft_ledger_json]
    
    except Exception as e:
        write_trace(trace)
        result.error_category = ErrorCategory.SCHEMA_MISMATCH
        return result
    
    start_time = time.time()
    eval_result = run_eval(scenario)
    duration_ms = int((time.time()-start_time)*1000)

    trace.execution_steps.append(ExecutionStep(
        step="eval_initial",
        input=scenario.model_dump(mode='json'),
        output=eval_result.model_dump(mode='json'),
        duration_ms=duration_ms
    ))

    # Set initial eval results immediately
    result.initial_verdict = eval_result.verdict
    result.first_violation_month = eval_result.first_violation_month
    result.violated_invariant = eval_result.violated_invariant
    
    # Validate draft ledger immediately while we have eval result
    if draft_ledger_json:
        result.draft_ledger_correct = validate_ledger(draft_ledger, eval_result.ledger, task.expected.ledger if task.expected else None)
    
    # Set violation correctness if we have expected results
    if task.expected and task.expected.initial_verdict == "infeasible":
        result.violation_correct = eval_result.violated_invariant == task.expected.violated_invariant
        result.first_violation_month_correct = eval_result.first_violation_month == task.expected.first_violation_month
    
    # Set verdict correctness
    result.verdict_correct = eval_result.verdict == task.expected.initial_verdict if task.expected else None

    eval_repair_result = eval_result

    if eval_result.verdict == "infeasible": #begin repair loop
        start_time = time.time()
        repair_data = agent.repair(scenario.model_dump_json(), eval_result.model_dump(mode='json'), task.generate_ledger, prompt_dir, model_name)
        duration_ms = int((time.time()-start_time)*1000)
        trace.execution_steps.append(ExecutionStep(
            step="repair",
            input=scenario.model_dump_json(),
            output=repair_data,
            duration_ms=duration_ms
        ))
        # Parse repair JSON
        try:
            repair_parsed = json.loads(repair_data)
            repair_scenario_json = repair_parsed["repaired_scenario"]
            result.repair_strategy = repair_parsed["repair_applied"]["type"]
            result.repair_json = json.dumps(repair_scenario_json)
            repair_ledger_json = repair_parsed.get("ledger") if task.generate_ledger else None
        except Exception as e:
            write_trace(trace)
            result.error_category = ErrorCategory.INVALID_JSON
            return result

        if result.repair_strategy not in ["baseline_reduction", "event_amount_adjustment", "event_timing_shift"]:
            write_trace(trace)
            result.error_category = ErrorCategory.INACCURATE_REPAIR_LABEL
            return result
        
        if not validate_repair_claim(json.dumps(draft_scenario_json), json.dumps(repair_scenario_json), result.repair_strategy):
            write_trace(trace)
            result.error_category = ErrorCategory.INACCURATE_REPAIR_LABEL
            return result

        try:
            scenario = Scenario.model_validate(repair_scenario_json)
            if repair_ledger_json:
                repair_ledger = [MonthlyRecord.model_validate(record) for record in repair_ledger_json]
        except Exception as e:
            write_trace(trace)
            result.error_category = ErrorCategory.SCHEMA_MISMATCH
            return result

        result.tool_calls += 1
        result.repair_attempts += 1
        result.repair_attempted = True

        start_time = time.time()
        eval_repair_result = run_eval(scenario)
        duration_ms = int((time.time()-start_time)*1000)

        trace.execution_steps.append(ExecutionStep(
            step="eval_repair",
            input=json.dumps(repair_scenario_json),
            output=eval_repair_result.model_dump(mode='json'),
            duration_ms=duration_ms
        ))
        
        # Set repair results immediately
        result.final_verdict = eval_repair_result.verdict
        result.repair_made_feasible = eval_repair_result.verdict == "feasible"
        
        # Validate repair ledger immediately while we have repair eval result
        if repair_ledger_json:
            result.repair_ledger_correct = validate_ledger(repair_ledger, eval_repair_result.ledger, task.expected.ledger if task.expected else None)
    
    else:
        # No repair attempted, final state same as initial
        result.final_verdict = result.initial_verdict
        result.repair_attempted = False

    # Ledger validation completed during eval steps above
    

    if result.tool_calls == 0:
        result.error_category = ErrorCategory.NO_TOOL_USE

    elif result.tool_calls > task.limits.max_tool_calls:
        result.error_category = ErrorCategory.EXCEEDED_MAX_TOOL_CALLS
    
    elif result.repair_attempts > task.limits.max_repairs:
        result.error_category = ErrorCategory.EXCEEDED_MAX_REPAIRS

    elif eval_result.verdict == "infeasible" and result.final_verdict == "infeasible" and result.repair_made_feasible is False:
        result.error_category = ErrorCategory.REPAIR_FAILED

    elif result.verdict_correct is not None and result.verdict_correct is False:
        result.error_category = ErrorCategory.WRONG_VERDICT
    
    elif result.first_violation_month_correct is not None and result.first_violation_month_correct is False:
        result.error_category = ErrorCategory.WRONG_FIRST_VIOLATION_MONTH
    
    elif result.violation_correct is not None and result.violation_correct is False:
        result.error_category = ErrorCategory.WRONG_VIOLATION
    
    # Calculate overall score
    result = update_result_with_score(result, task)
    
    trace.final_result = result
    write_trace(trace)
    return result

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
    os.makedirs(f"traces/{trace.session_id}", exist_ok=True)
    try:
        with open(f"traces/{trace.session_id}/{trace.run_id}.json", "w") as f: 
            f.write(trace.model_dump_json(indent=2))
    except Exception as e:
        print(f"🐛 DEBUG: Error serializing trace for task {trace.task_id}: {e}")
        
        # Check each execution step
        for i, step in enumerate(trace.execution_steps):
            try:
                step.model_dump_json()
                print(f"  ✅ Step {i} ({step.step}): OK")
            except Exception as step_e:
                print(f"  ❌ Step {i} ({step.step}): ERROR - {step_e}")
                # Dig deeper into step output
                try:
                    import json
                    json.dumps(step.output)
                    print(f"     step.output JSON serializable: OK")
                except Exception as output_e:
                    print(f"     step.output JSON error: {output_e}")
        
        # Check final_result 
        try:
            if trace.final_result:
                import json
                json.dumps(trace.final_result)
                print("  ✅ final_result: OK")
        except Exception as final_e:
            print(f"  ❌ final_result: ERROR - {final_e}")
        
        raise e
    return
    
def validate_ledger(agent_ledger: List[MonthlyRecord], ground_truth_ledger: List[MonthlyRecord], expected_ledger: Optional[List[MonthlyRecord]] = None) -> bool:
    """
    Validate ledger accuracy in two ways:
    1. If expected_ledger provided: Compare against expected
    2. Otherwise: Compare against ground_truth_ledger from simulator
    3. Return True only if ledger matches the appropriate baseline
    """
    if not agent_ledger:
        return False
    
    # Prefer expected ledger if provided, otherwise use ground truth
    target_ledger = expected_ledger if expected_ledger is not None else ground_truth_ledger
    
    return agent_ledger == target_ledger

def validate_repair_claim(original_json: str, repaired_json: str, claimed_type: str) -> bool:

    original = json.loads(original_json)
    repaired = json.loads(repaired_json)

    if claimed_type == "baseline_reduction":
      # For baseline_reduction, outflows should become less negative (reduced spending)
      if repaired["base_monthly"]["outflows"] <= original["base_monthly"]["outflows"]:
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
      # Check that baseline spending stayed the same
      if original["base_monthly"]["outflows"] != repaired["base_monthly"]["outflows"]:
          return False
      if original["base_monthly"]["takehome_salary"] != repaired["base_monthly"]["takehome_salary"]:
          return False
      
      # Check all top-level fields except events
      for field in ["id", "title", "start_month", "horizon_months", "initial_state"]:
          if original.get(field) != repaired.get(field):
              return False
      
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