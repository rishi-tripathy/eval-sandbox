import typer
from pathlib import Path
from typing import Optional
from workbench.runner import run_task
from workbench.task_types import TaskResult
import json
import uuid
from datetime import datetime

app = typer.Typer()

@app.command()
def run_single(
    task_path: Path = typer.Argument(..., help="Path to task JSON file"),
    model: str = typer.Option("stub", help="Model to use (stub, claude)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Run a single task and display results."""
    typer.echo(f"Running task: {task_path}")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M_%S')}_{str(uuid.uuid4())[:8]}"
    result = run_task(str(task_path), model=model, session_id=session_id)
    
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
    model: str = typer.Option("stub", help="Model to use (stub, claude)")
):
    """Run all tasks in a directory."""
    task_files = list(task_dir.glob("*.json"))
    typer.echo(f"Found {len(task_files)} tasks")
    
    # TODO: Implement suite runner
    # Should:
    # 1. Run each task
    # 2. Collect results
    # 3. Generate summary report
    # 4. Save to session directory
    
    typer.echo("Suite runner not implemented yet")

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