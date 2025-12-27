"""
Comparison framework for systematic model performance evaluation.
Supports A/B testing across models, task sets, and other parameters.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Iterator, Optional
import uuid
import typer
from workbench.task_types import TaskResult
from workbench.runner import run_task


@dataclass
class ComparisonConfig:
    """Configuration for a systematic model comparison."""
    models: List[str]
    task_sets: List[str] 
    runs_per_condition: int
    session_id: str
    prompt_dir: str = "prompts/v2"
    model_name: str = None

    @classmethod
    def from_csv_params(
        cls,
        models_csv: str,
        task_sets_csv: str,
        runs_per_condition: int = 5,
        session_id: str = None,
        prompt_dir: str = "prompts/v2",
        model_name: str = None
    ) -> "ComparisonConfig":
        """Create config from CSV parameters."""
        models = [m.strip() for m in models_csv.split(",")]
        task_sets = [ts.strip() for ts in task_sets_csv.split(",")]
        
        if session_id is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            session_id = f"comparison_{timestamp}"
        
        return cls(
            models=models,
            task_sets=task_sets,
            runs_per_condition=runs_per_condition,
            session_id=session_id,
            prompt_dir=prompt_dir,
            model_name=model_name
        )

    def total_executions(self) -> int:
        """Calculate total number of individual task executions."""
        return len(self.models) * len(self.task_sets) * self.runs_per_condition

    def total_conditions(self) -> int:
        """Calculate total number of unique conditions."""
        return len(self.models) * len(self.task_sets)


@dataclass
class ComparisonCondition:
    """A single condition in the comparison matrix."""
    model: str
    task_set: str
    run_number: int
    condition_id: str
    
    @property
    def display_name(self) -> str:
        """Human-readable condition identifier."""
        return f"{self.model}+{Path(self.task_set).name}"


@dataclass 
class ComparisonResult:
    """Results from a completed comparison."""
    config: ComparisonConfig
    results: List[TaskResult]
    conditions: List[ComparisonCondition]
    
    def get_results_for_condition(self, model: str, task_set: str) -> List[TaskResult]:
        """Get all results for a specific model/task_set combination."""
        condition_results = []
        for i, condition in enumerate(self.conditions):
            if condition.model == model and condition.task_set == task_set:
                condition_results.append(self.results[i])
        return condition_results


def generate_comparison_conditions(config: ComparisonConfig) -> List[ComparisonCondition]:
    """Generate the matrix of conditions to execute."""
    conditions = []
    
    for model in config.models:
        for task_set in config.task_sets:
            for run in range(1, config.runs_per_condition + 1):
                condition_id = f"{model}_{Path(task_set).name}_run{run}"
                condition = ComparisonCondition(
                    model=model,
                    task_set=task_set,
                    run_number=run,
                    condition_id=condition_id
                )
                conditions.append(condition)
    
    return conditions


def get_task_files_for_set(task_set: str) -> List[Path]:
    """Get all task files for a given task set directory."""
    task_dir = Path(task_set)
    if not task_dir.exists():
        raise ValueError(f"Task set directory not found: {task_set}")
    
    task_files = list(task_dir.glob("*.json"))
    if not task_files:
        raise ValueError(f"No task files found in: {task_set}")
    
    return sorted(task_files)


def create_comparison_session_id(models: List[str], task_sets: List[str]) -> str:
    """Create a descriptive session ID for a comparison."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    model_str = "_".join(models)
    task_str = "_".join([Path(ts).name for ts in task_sets])
    return f"comparison_{timestamp}_{model_str}_{task_str}"


def run_comparison(config: ComparisonConfig) -> ComparisonResult:
    """Execute a full comparison across all conditions."""
    
    # Generate conditions matrix
    conditions = generate_comparison_conditions(config)
    total_executions = len(conditions)
    
    # Display comparison overview
    typer.echo(f"=== COMPARISON: {len(config.models)} models × {len(config.task_sets)} task-sets × {config.runs_per_condition} runs = {total_executions} total ===")
    
    results = []
    execution_count = 0
    
    try:
        for condition in conditions:
            execution_count += 1
            
            # Get task files for this condition
            task_files = get_task_files_for_set(condition.task_set)
            
            # Execute each task in the set
            for task_file in task_files:
                # Create unique session ID for this execution
                execution_session_id = f"{config.session_id}_{condition.condition_id}_{task_file.stem}"
                
                # Progress display
                progress_msg = f"[{execution_count}/{total_executions}] {condition.display_name} (run {condition.run_number}/{config.runs_per_condition}): {task_file.stem}..."
                typer.echo(progress_msg, nl=False)
                
                try:
                    # Execute the task
                    result = run_task(
                        task_path=str(task_file),
                        model=condition.model,
                        session_id=execution_session_id,
                        prompt_dir=config.prompt_dir,
                        model_name=config.model_name
                    )
                    
                    # Add condition metadata to result
                    result.condition_model = condition.model
                    result.condition_task_set = condition.task_set
                    result.condition_run_number = condition.run_number
                    result.condition_id = condition.condition_id
                    
                    results.append(result)
                    
                    # Progress result display 
                    if result.error_category:
                        typer.secho(f" error ({result.error_category.value})", fg=typer.colors.RED)
                    else:
                        score_display = f"{result.score_earned}/{result.score_possible}" if result.score_earned else "N/A"
                        typer.secho(f" {result.final_verdict} (Score: {score_display})", fg=typer.colors.GREEN)
                        
                except Exception as e:
                    typer.secho(f" SYSTEM ERROR: {e}", fg=typer.colors.RED)
                    # Continue with next task rather than failing entire comparison
                    continue
                    
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Comparison interrupted by user")
        # Return partial results
        
    except Exception as e:
        typer.secho(f"\n❌ Comparison failed: {e}", fg=typer.colors.RED)
        raise
        
    # Create final result object
    comparison_result = ComparisonResult(
        config=config,
        results=results,
        conditions=conditions
    )
    
    typer.echo(f"\n✓ Comparison complete. {len(results)} tasks executed.")
    return comparison_result


def group_results_by_condition(comparison_result: ComparisonResult) -> dict:
    """Group results by model and task set for analysis."""
    grouped = {}
    
    for result in comparison_result.results:
        key = (result.condition_model, result.condition_task_set)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)
    
    return grouped