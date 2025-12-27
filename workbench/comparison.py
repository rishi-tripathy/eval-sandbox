"""
Comparison framework for systematic model performance evaluation.
Supports A/B testing across models, task sets, and other parameters.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Iterator, Optional, Dict
import uuid
import typer
import json
import os
from collections import defaultdict
from workbench.task_types import TaskResult, ErrorCategory
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


def group_results_by_condition(comparison_result: ComparisonResult) -> Dict[Tuple[str, str], List[TaskResult]]:
    """Group results by model and task set for analysis."""
    grouped = {}
    
    for result in comparison_result.results:
        key = (result.condition_model, result.condition_task_set)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)
    
    return grouped


@dataclass
class ConditionStats:
    """Statistics for a single condition (model + task set combination)."""
    model: str
    task_set: str
    total_tasks: int
    successful_tasks: int
    success_rate: float
    average_score: float
    score_std: float
    error_categories: Dict[str, int]
    tool_usage_total: int
    tool_usage_breakdown: Dict[str, int]


def calculate_condition_stats(results: List[TaskResult]) -> ConditionStats:
    """Calculate aggregate statistics for a condition."""
    if not results:
        return ConditionStats(
            model="unknown", task_set="unknown", total_tasks=0,
            successful_tasks=0, success_rate=0.0, average_score=0.0, score_std=0.0,
            error_categories={}, tool_usage_total=0, tool_usage_breakdown={}
        )
    
    # Basic counts
    total_tasks = len(results)
    successful_tasks = sum(1 for r in results if r.error_category is None)
    success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0.0
    
    # Score statistics
    scores = [r.score_earned for r in results if r.score_earned is not None]
    average_score = sum(scores) / len(scores) if scores else 0.0
    score_variance = sum((s - average_score) ** 2 for s in scores) / len(scores) if len(scores) > 1 else 0.0
    score_std = score_variance ** 0.5
    
    # Error category breakdown
    error_categories = defaultdict(int)
    for result in results:
        if result.error_category:
            error_categories[result.error_category.value] += 1
    
    # Tool usage statistics
    tool_usage_total = sum(r.tool_calls for r in results if r.tool_calls)
    tool_usage_breakdown = defaultdict(int)
    for result in results:
        if result.tool_details:
            for tool, count in result.tool_details.items():
                tool_usage_breakdown[tool] += count
    
    return ConditionStats(
        model=results[0].condition_model,
        task_set=results[0].condition_task_set,
        total_tasks=total_tasks,
        successful_tasks=successful_tasks,
        success_rate=success_rate,
        average_score=average_score,
        score_std=score_std,
        error_categories=dict(error_categories),
        tool_usage_total=tool_usage_total,
        tool_usage_breakdown=dict(tool_usage_breakdown)
    )


def generate_comparison_report(comparison_result: ComparisonResult) -> str:
    """Generate a markdown comparison report."""
    config = comparison_result.config
    grouped_results = group_results_by_condition(comparison_result)
    
    # Calculate stats for each condition
    condition_stats = {}
    for (model, task_set), results in grouped_results.items():
        condition_stats[(model, task_set)] = calculate_condition_stats(results)
    
    # Generate report
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    report = f"""# Comparison Report: {timestamp}

## Configuration
- Models: {', '.join(config.models)}
- Task Sets: {', '.join([Path(ts).name for ts in config.task_sets])}
- Runs per condition: {config.runs_per_condition}
- Total executions: {len(comparison_result.results)}

## Results Summary

| Model | Task Set | Avg Score | Success Rate | Total Tasks | Top Errors |
|-------|----------|-----------|--------------|-------------|------------|"""

    # Add table rows
    for (model, task_set), stats in condition_stats.items():
        task_set_name = Path(task_set).name
        score_display = f"{stats.average_score:.1f} ± {stats.score_std:.1f}"
        success_display = f"{stats.success_rate:.1f}%"
        
        # Top 2 errors
        top_errors = sorted(stats.error_categories.items(), key=lambda x: x[1], reverse=True)[:2]
        error_display = ", ".join([f"{error} ({count})" for error, count in top_errors]) if top_errors else "None"
        
        report += f"\n| {model} | {task_set_name} | {score_display} | {success_display} | {stats.total_tasks} | {error_display} |"
    
    # Tool usage section
    if any(stats.tool_usage_total > 0 for stats in condition_stats.values()):
        report += "\n\n## Tool Usage Analysis\n\n"
        report += "| Model | Task Set | Total Calls | Tool Breakdown |\n"
        report += "|-------|----------|-------------|----------------|\n"
        
        for (model, task_set), stats in condition_stats.items():
            task_set_name = Path(task_set).name
            if stats.tool_usage_total > 0:
                tool_breakdown = ", ".join([f"{tool}: {count}" for tool, count in stats.tool_usage_breakdown.items()])
                report += f"| {model} | {task_set_name} | {stats.tool_usage_total} | {tool_breakdown} |\n"
            else:
                report += f"| {model} | {task_set_name} | 0 | None |\n"
    
    # Error analysis section
    report += "\n\n## Error Analysis\n\n"
    all_errors = defaultdict(int)
    for stats in condition_stats.values():
        for error, count in stats.error_categories.items():
            all_errors[error] += count
    
    if all_errors:
        for error, total_count in sorted(all_errors.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{error}**: {total_count} total occurrences\n"
            # Show breakdown by condition
            for (model, task_set), stats in condition_stats.items():
                if error in stats.error_categories:
                    count = stats.error_categories[error]
                    report += f"  - {model} + {Path(task_set).name}: {count}\n"
    else:
        report += "No errors occurred across all conditions.\n"
    
    # Key findings
    report += "\n## Key Findings\n\n"
    
    # Compare models if multiple
    if len(config.models) > 1:
        model_scores = {}
        model_success = {}
        for (model, task_set), stats in condition_stats.items():
            if model not in model_scores:
                model_scores[model] = []
                model_success[model] = []
            model_scores[model].append(stats.average_score)
            model_success[model].append(stats.success_rate)
        
        for model in config.models:
            avg_score = sum(model_scores[model]) / len(model_scores[model])
            avg_success = sum(model_success[model]) / len(model_success[model])
            report += f"- **{model}**: {avg_score:.1f} avg score, {avg_success:.1f}% success rate\n"
    
    # Compare task sets if multiple
    if len(config.task_sets) > 1:
        report += "\n"
        task_set_scores = {}
        for (model, task_set), stats in condition_stats.items():
            task_name = Path(task_set).name
            if task_name not in task_set_scores:
                task_set_scores[task_name] = []
            task_set_scores[task_name].append(stats.average_score)
        
        for task_name, scores in task_set_scores.items():
            avg_score = sum(scores) / len(scores)
            report += f"- **{task_name}**: {avg_score:.1f} average difficulty\n"
    
    return report


def save_comparison_results(comparison_result: ComparisonResult, output_dir: str = "reports") -> str:
    """Save comparison results to structured output directory."""
    
    # Create output directory structure
    output_path = Path(output_dir) / comparison_result.config.session_id
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config_data = {
        "models": comparison_result.config.models,
        "task_sets": comparison_result.config.task_sets,
        "runs_per_condition": comparison_result.config.runs_per_condition,
        "session_id": comparison_result.config.session_id,
        "prompt_dir": comparison_result.config.prompt_dir,
        "total_executions": len(comparison_result.results),
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path / "config.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    # Save raw results as NDJSON
    with open(output_path / "raw_results.ndjson", "w") as f:
        for result in comparison_result.results:
            f.write(result.model_dump_json() + "\n")
    
    # Save comparison report
    report = generate_comparison_report(comparison_result)
    with open(output_path / "comparison_report.md", "w") as f:
        f.write(report)
    
    # Create traces directory (individual trace files are already saved by run_task)
    traces_dir = output_path / "traces"
    traces_dir.mkdir(exist_ok=True)
    
    return str(output_path)