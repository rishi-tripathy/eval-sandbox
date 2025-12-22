from workbench.task_types import Task, TaskResult
from workbench.types import Scenario
from workbench.models.agents import get_agent
from workbench.eval import run_eval


def run_task(task_path: str, model: str = "stub") -> TaskResult:
    from workbench.task_types import ErrorCategory
    import json
    
    task = Task.model_validate_json(open(task_path).read())
    
    agent = get_agent(model)
    tool_calls = 0
    repair_attempts = 0

    # Try to draft scenario
    try:
        scenario_json = agent.draft(task.prompt, task.mode)
        tool_calls += 1
        
        # Try to parse JSON
        try:
            json.loads(scenario_json)
        except json.JSONDecodeError:
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
        return TaskResult(
            task_id=task.id,
            scenario_json={},
            initial_verdict="error",
            final_verdict="error",
            tool_calls=tool_calls,
            error_category=ErrorCategory.SCHEMA_MISMATCH
        )
    

    eval_result = run_eval(scenario)

    repair_json = None

    final_result = eval_result

    if eval_result.verdict == "infeasible":
        repair_json = agent.repair(scenario_json, eval_result)
        if repair_json:
            scenario = Scenario.model_validate_json(repair_json)
            final_result = run_eval(scenario)
            tool_calls += 1
            repair_attempts += 1


    import json
    
    return TaskResult(
        task_id=task.id,
        scenario_json=json.loads(scenario_json),
        repair_json=json.loads(repair_json) if repair_json else None,
        initial_verdict=eval_result.verdict,
        final_verdict=final_result.verdict,
        first_violation_month=final_result.first_violation_month,
        violated_invariant=final_result.violated_invariant,
        tool_calls=tool_calls,
        repair_attempts=1 if repair_json else 0,
        verdict_correct=eval_result.verdict == task.expected.initial_verdict if task.expected else None,
        violation_correct=eval_result.violated_invariant == task.expected.violated_invariant if task.expected else None,
        repair_attempted=repair_json is not None,
        repair_made_feasible=final_result.verdict == "feasible",
        error_category=final_result.error_category
    )