import typer
from pathlib import Path
from typing import Optional
from workbench.runner import run_task
from workbench.task_types import TaskResult
import json
import uuid
from datetime import datetime
import os
from workbench.trace_types import Trace
from typing import List

app = typer.Typer()

@app.command()
def run_single(
    task_path: Path = typer.Argument(..., help="Path to task JSON file"),
    model: str = typer.Option("stub", help="Model to use (stub, claude)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    prompt_dir: str = typer.Option("prompts/v2", "--prompts", help="Directory containing prompt files"),
    model_name: str = typer.Option(None, "--model-name", help="Name of the model to use")
):
    """Run a single task and display results."""
    typer.echo(f"Running task: {task_path}")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M_%S')}_{str(uuid.uuid4())[:8]}"
    result = run_task(str(task_path), model=model, session_id=session_id, prompt_dir=prompt_dir, model_name=model_name)
    
    # Display results
    typer.echo(f"Initial verdict: {result.initial_verdict}")
    typer.echo(f"Final verdict: {result.final_verdict}")
    typer.echo(f"Tool calls: {result.tool_calls}")
    
    if result.error_category:
        typer.secho(f"Error: {result.error_category.value}", fg=typer.colors.RED)
    
    if verbose:
        typer.echo("\nFull result:")
        typer.echo(result.model_dump_json(indent=2))

@app.command()
def run_suite(
    task_dir: Path = typer.Argument("tasks/v1", help="Directory containing task files"),
    model: str = typer.Option("stub", help="Model to use (stub, claude)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    prompt_dir: str = typer.Option("prompts/v2", "--prompts", help="Directory containing prompt files"),
    model_name: str = typer.Option(None, "--model-name", help="Name of the model to use")
):
    """Run all tasks in a directory."""
    task_files = list(task_dir.glob("*.json"))
    typer.echo(f"Found {len(task_files)} tasks")
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M_%S')}_{str(uuid.uuid4())[:8]}"
    total_tasks = 0;
    feasible_tasks = 0;
    infeasible_tasks = 0;
    tasks_with_repair = 0;
    error_tasks = 0;

    tasks_with_correct_verdict = 0
    tasks_with_correct_violation = 0
    tasks_with_correct_first_violation_month = 0
    repairs_made_feasible = 0
    
    # Repair strategy tracking
    repair_strategies = {}
    error_categories = {}
    
    session_summary = ""
    session_results = []
    
    try:
        for task in task_files:
            try:
                result = run_task(str(task), model=model, session_id=session_id, prompt_dir=prompt_dir, model_name=model_name)
                # Use mode='json' to properly serialize enums
                try:
                    session_results.append(result.model_dump(mode='json'))
                except Exception as e:
                    typer.secho(f"Error processing result for task {task}: {e}", fg=typer.colors.RED)
                    # Skip this task and continue
                    continue
            except Exception as e:
                typer.secho(f"Error running task {task}: {e}", fg=typer.colors.RED)
                # Skip this task and continue  
                continue
            total_tasks += 1
            if result.final_verdict == "feasible":
                feasible_tasks += 1
            elif result.final_verdict == "infeasible":
                infeasible_tasks += 1
            if result.error_category is not None:
                error_tasks += 1
            if result.repair_attempts > 0:
                tasks_with_repair += 1
            
            if result.verdict_correct:
                tasks_with_correct_verdict += 1
            if result.violation_correct:
                tasks_with_correct_violation += 1
            if result.repair_made_feasible:
                repairs_made_feasible += 1
            if result.first_violation_month_correct:
                tasks_with_correct_first_violation_month += 1
                
            # Track repair strategies
            if result.repair_strategy:
                repair_strategies[result.repair_strategy] = repair_strategies.get(result.repair_strategy, 0) + 1
                
            # Track error categories
            if result.error_category:
                error_name = result.error_category.value if hasattr(result.error_category, 'value') else str(result.error_category)
                error_categories[error_name] = error_categories.get(error_name, 0) + 1
            
            repair_strategy_lines = "\n".join([f"            {strategy}: {count}" for strategy, count in repair_strategies.items()])
            error_category_lines = "\n".join([f"            {error}: {count}" for error, count in error_categories.items()])
            
            session_summary = f"""
            Session summary:
            total_tasks: {total_tasks}
            feasible_tasks: {feasible_tasks}
            infeasible_tasks: {infeasible_tasks}
            tasks_with_repair: {tasks_with_repair}
            repairs_made_feasible: {repairs_made_feasible}
            tasks_with_correct_verdict: {tasks_with_correct_verdict}
            tasks_with_correct_violation: {tasks_with_correct_violation}
            tasks_with_correct_first_violation_month: {tasks_with_correct_first_violation_month}
            error_tasks: {error_tasks}
            
            Repair strategies used:
{repair_strategy_lines or "            (none)"}
            
            Error categories:
{error_category_lines or "            (none)"}
            """
            # if verbose:
            #     typer.echo("\nFull result for task {task.name}:")
            #     typer.echo(result.model_dump_json(indent=2))

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
    
    finally:    
        write_session_summary(session_id, session_summary, session_results)

def write_session_summary(session_id: str, session_summary: str, session_results: List[dict]):
    typer.secho(f"Session summary: {session_summary}", fg=typer.colors.BLUE)
    os.makedirs(f"traces/{session_id}", exist_ok=True)  # Add this line
    with open(f"traces/{session_id}/summary.txt", "w") as f: 
            f.write(session_summary)
    with open(f"traces/{session_id}/results.ndjson", "w") as f: 
        for result in session_results:
            f.write(json.dumps(result) + "\n")
    return

@app.command()
def validate(
    scenario_path: Path = typer.Argument(..., help="Path to scenario JSON file")
):
    """Validate a scenario JSON file."""
    from workbench.types import Scenario
    
    try:
        with open(scenario_path) as f:
            data = json.load(f)
        scenario = Scenario.model_validate(data)
        typer.secho("✓ Valid scenario", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"✗ Invalid: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    app()