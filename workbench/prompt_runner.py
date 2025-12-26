from workbench.runner import run_task
from workbench.task_types import Task, TaskResult
import json
import tempfile
import os

def run_prompt_task(
    prompt: str, 
    model: str = "claude", 
    session_id: str = None,
    model_name: str = None,
    generate_ledger: bool = True,
    start_month_default: str = "2024-01",
    horizon_default: int = 6, 
    starting_cash_default: float = 1000
) -> TaskResult:
    """Run a direct prompt with post-processing to inject missing required fields."""
    
    from workbench.task_types import Limits
    from workbench.models.agents import get_agent
    from workbench.types import Scenario
    from workbench.prompt_scoring import update_prompt_result_with_score
    
    # Create basic task for agent
    task = Task(
        id="prompt_task",
        title="Dynamic Prompt Task", 
        mode="fast",
        generate_ledger=generate_ledger,
        prompt=prompt,  # Raw prompt only
        limits=Limits(max_tool_calls=10, max_repairs=1),
        expected=None
    )
    
    # Get agent and generate scenario
    agent = get_agent(model)
    
    try:
        # Get Claude's response to raw prompt
        draft_data = agent.draft(task.prompt, task.mode, task.generate_ledger, "prompts/v2", model_name)
        draft_parsed = json.loads(draft_data)
        
        if task.generate_ledger:
            draft_scenario_json = draft_parsed["scenario"]
            draft_ledger_json = draft_parsed.get("ledger")
        else:
            draft_scenario_json = draft_parsed
            draft_ledger_json = None
            
        # Inject missing required fields
        if "start_month" not in draft_scenario_json:
            draft_scenario_json["start_month"] = start_month_default
            
        if "horizon_months" not in draft_scenario_json:
            draft_scenario_json["horizon_months"] = horizon_default
            
        if "initial_state" not in draft_scenario_json:
            draft_scenario_json["initial_state"] = {}
        if "starting_cash" not in draft_scenario_json["initial_state"]:
            draft_scenario_json["initial_state"]["starting_cash"] = starting_cash_default
            
        # Create temporary task file with injected scenario
        if task.generate_ledger:
            final_response = {
                "scenario": draft_scenario_json,
                "ledger": draft_ledger_json
            }
        else:
            final_response = draft_scenario_json
            
        # Create a modified task that uses the injected scenario
        modified_task = Task(
            id="prompt_task_processed",
            title="Processed Prompt Task",
            mode="fast", 
            generate_ledger=generate_ledger,
            prompt="processed_scenario",  # Dummy prompt since we're injecting scenario
            limits=Limits(max_tool_calls=10, max_repairs=1),
            expected=None
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(modified_task.model_dump_json(indent=2))
            temp_path = f.name
        
        try:
            # Use regular runner but override the draft step result
            result = run_task(temp_path, model=model, session_id=session_id, model_name=model_name)
            
            # Override with our injected data
            result.scenario_json = json.dumps(draft_scenario_json)
            if draft_ledger_json:
                result.draft_ledger_json = json.dumps(draft_ledger_json)
            
            # Apply prompt-specific scoring
            result = update_prompt_result_with_score(result)
            
            return result
            
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        # Return error result
        result = TaskResult(
            task_id="prompt_task",
            initial_verdict="error", 
            final_verdict="error"
        )
        result = update_prompt_result_with_score(result)
        return result