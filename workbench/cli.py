import typer
from pathlib import Path
from typing import Optional
from workbench.runner import run_task
from workbench.task_types import Task, TaskResult, Limits
from workbench.comparison import ComparisonConfig, run_comparison, save_comparison_results
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
    # Display what we're running
    if model_name:
        typer.echo(f"Running task: {task_path}")
        typer.echo(f"Agent: {model}, Model: {model_name}")
    else:
        typer.echo(f"Running task: {task_path}")
        typer.echo(f"Agent: {model}")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M_%S')}_{str(uuid.uuid4())[:8]}"
    result = run_task(str(task_path), model=model, session_id=session_id, prompt_dir=prompt_dir, model_name=model_name)
    
    # Display results with scoring breakdown
    if result.initial_verdict != result.final_verdict:
        verdict_display = f"{result.initial_verdict} → {result.final_verdict}"
        if result.repair_made_feasible:
            verdict_display += " (repair successful)"
        else:
            verdict_display += " (repair failed)"
    else:
        verdict_display = result.initial_verdict
    
    typer.echo(f"Result: {verdict_display}")
    
    if result.score_earned is not None and result.score_possible is not None:
        typer.echo(f"Score: {result.score_earned}/{result.score_possible}")
        
        # Show scoring breakdown
        from workbench.scoring import calculate_task_score
        task = Task.model_validate_json(open(str(task_path)).read())
        score_data = calculate_task_score(result, task)
        typer.echo("Breakdown:")
        for component, data in score_data["breakdown"].items():
            typer.echo(f"  └ {component.replace('_', ' ').title()}: {data['earned']}/{data['possible']}")
    
    # Show tool usage
    if result.tool_details:
        total_tools = sum(result.tool_details.values())
        if total_tools > 0:
            typer.echo(f"Tools used ({total_tools} total):")
            for tool, count in result.tool_details.items():
                if count > 0:
                    percentage = (count / total_tools) * 100
                    typer.echo(f"  └ {tool}: {count} ({percentage:.0f}%)")
    elif result.tool_calls > 0:
        typer.echo(f"Tool calls: {result.tool_calls}")
    
    if result.error_category:
        if result.score_earned is not None and result.score_possible is not None:
            typer.secho(f"Error: {result.error_category.value} (partial score: {result.score_earned}/{result.score_possible})", fg=typer.colors.RED)
        else:
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
    initially_feasible_tasks = 0;
    initially_infeasible_tasks = 0;
    final_feasible_tasks = 0;
    final_infeasible_tasks = 0;
    tasks_with_repair = 0;
    error_tasks = 0;

    tasks_with_correct_verdict = 0
    tasks_with_correct_violation = 0
    tasks_with_correct_first_violation_month = 0
    repairs_made_feasible = 0
    
    # Ledger tracking
    tasks_with_draft_ledger = 0
    tasks_with_repair_ledger = 0
    draft_ledgers_correct = 0
    repair_ledgers_correct = 0
    
    # Score tracking
    total_score_earned = 0
    total_score_possible = 0
    
    # Repair strategy tracking
    repair_strategies = {}
    error_categories = {}
    
    # Tool usage tracking
    total_tool_calls = 0
    tool_usage_totals = {"calculate": 0, "validate_monthly_record": 0, "duration_advisor": 0, "check_json": 0}
    
    session_summary = ""
    session_results = []
    
    try:
        for i, task in enumerate(task_files, 1):
            # Show progress
            task_name = task.stem
            typer.echo(f"[{i}/{len(task_files)}] {task_name}...", nl=False)
            
            try:
                result = run_task(str(task), model=model, session_id=session_id, prompt_dir=prompt_dir, model_name=model_name)
                
                # Show result summary
                if result.initial_verdict != result.final_verdict:
                    verdict_display = f"{result.initial_verdict} → {result.final_verdict}"
                    if result.repair_made_feasible:
                        verdict_display += " (repair successful)"
                    else:
                        verdict_display += " (repair failed)"
                else:
                    verdict_display = result.initial_verdict
                
                score_display = ""
                if result.score_earned is not None and result.score_possible is not None:
                    score_display = f" - {result.score_earned}/{result.score_possible}"
                
                # Show error or success indicator
                if result.error_category:
                    if result.score_earned is not None and result.score_possible is not None:
                        typer.secho(f" {verdict_display}{score_display} ERROR: {result.error_category.value} (partial score: {result.score_earned}/{result.score_possible})", fg=typer.colors.RED)
                    else:
                        typer.secho(f" {verdict_display}{score_display} ERROR: {result.error_category.value}", fg=typer.colors.RED)
                elif result.repair_made_feasible != False:
                    typer.secho(f" {verdict_display}{score_display} ✅", fg=typer.colors.GREEN)
                else:
                    typer.echo(f" {verdict_display}{score_display}")
            
                # Use mode='json' to properly serialize enums
                try:
                    session_results.append(result.model_dump(mode='json'))
                except Exception as e:
                    typer.secho(f"Error processing result for task {task}: {e}", fg=typer.colors.RED)
                    # Skip this task and continue
                    continue
            except Exception as e:
                typer.secho(f" SYSTEM ERROR: {e}", fg=typer.colors.RED)
                # Skip this task and continue  
                continue
            total_tasks += 1
            
            # Count initial and final verdicts separately
            if result.initial_verdict == "feasible":
                initially_feasible_tasks += 1
            elif result.initial_verdict == "infeasible":
                initially_infeasible_tasks += 1
                
            if result.final_verdict == "feasible":
                final_feasible_tasks += 1
            elif result.final_verdict == "infeasible":
                final_infeasible_tasks += 1
                
            if result.error_category is not None:
                error_tasks += 1
            if result.repair_attempts > 0:
                tasks_with_repair += 1
            
            # Ledger accuracy tracking
            if result.draft_ledger_json is not None:
                tasks_with_draft_ledger += 1
                if result.draft_ledger_correct:
                    draft_ledgers_correct += 1
                    
            if result.repair_ledger_json is not None:
                tasks_with_repair_ledger += 1
                if result.repair_ledger_correct:
                    repair_ledgers_correct += 1
            
            if result.verdict_correct:
                tasks_with_correct_verdict += 1
            if result.violation_correct:
                tasks_with_correct_violation += 1
            if result.repair_made_feasible:
                repairs_made_feasible += 1
            if result.first_violation_month_correct:
                tasks_with_correct_first_violation_month += 1
            
            # Score tracking
            if result.score_earned is not None and result.score_possible is not None:
                total_score_earned += result.score_earned
                total_score_possible += result.score_possible
                
            # Track repair strategies
            if result.repair_strategy:
                repair_strategies[result.repair_strategy] = repair_strategies.get(result.repair_strategy, 0) + 1
                
            # Track error categories
            if result.error_category:
                error_name = result.error_category.value if hasattr(result.error_category, 'value') else str(result.error_category)
                error_categories[error_name] = error_categories.get(error_name, 0) + 1
                
            # Track tool usage
            if result.tool_calls:
                total_tool_calls += result.tool_calls
            if result.tool_details:
                for tool, count in result.tool_details.items():
                    if tool in tool_usage_totals:
                        tool_usage_totals[tool] += count
            
            repair_strategy_lines = "\n".join([f"            {strategy}: {count}" for strategy, count in repair_strategies.items()])
            error_category_lines = "\n".join([f"            {error}: {count}" for error, count in error_categories.items()])
            tool_usage_lines = "\n".join([f"            {tool}: {count}" for tool, count in tool_usage_totals.items() if count > 0])
            
            # Calculate ledger accuracy percentages
            draft_accuracy = f"{draft_ledgers_correct}/{tasks_with_draft_ledger}" if tasks_with_draft_ledger > 0 else "N/A"
            repair_accuracy = f"{repair_ledgers_correct}/{tasks_with_repair_ledger}" if tasks_with_repair_ledger > 0 else "N/A"
            
            # Calculate overall score percentage
            overall_score_pct = round((total_score_earned / total_score_possible * 100), 1) if total_score_possible > 0 else 0
            
            session_summary = f"""
            Session summary:
            total_tasks: {total_tasks}
            initially_feasible_tasks: {initially_feasible_tasks}
            initially_infeasible_tasks: {initially_infeasible_tasks}
            final_feasible_tasks: {final_feasible_tasks}
            final_infeasible_tasks: {final_infeasible_tasks}
            tasks_with_repair: {tasks_with_repair}
            repairs_made_feasible: {repairs_made_feasible}
            tasks_with_correct_verdict: {tasks_with_correct_verdict}
            tasks_with_correct_violation: {tasks_with_correct_violation}
            tasks_with_correct_first_violation_month: {tasks_with_correct_first_violation_month}
            error_tasks: {error_tasks}
            
            Overall Score:
            total_score: {total_score_earned}/{total_score_possible} ({overall_score_pct}%)
            
            Ledger accuracy:
            draft_ledger_accuracy: {draft_accuracy}
            repair_ledger_accuracy: {repair_accuracy}
            
            Repair strategies used:
{repair_strategy_lines or "            (none)"}
            
            Error categories:
{error_category_lines or "            (none)"}
            
            Tool usage (total calls: {total_tool_calls}):
{tool_usage_lines or "            (none)"}
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

@app.command()
def run_prompt(
    prompt: str = typer.Argument(..., help="Natural language financial scenario description"),
    start_month: str = typer.Option("2024-01", help="Default start month if not specified in prompt"),
    horizon: int = typer.Option(6, help="Default horizon if not specified in prompt"), 
    starting_cash: float = typer.Option(1000, help="Default starting cash if not specified in prompt"),
    generate_ledger: bool = typer.Option(True, "--ledger/--no-ledger", help="Request ledger generation"),
    model: str = typer.Option("claude", help="Model to use"),
    model_name: str = typer.Option(None, "--model-name", help="Specific model name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Run a direct prompt without predefined task file. Defaults are used only if scenario is missing required fields."""
    
    task = Task(
        id="prompt_task",
        title="Dynamic Prompt Task", 
        mode="fast",
        generate_ledger=generate_ledger,
        prompt=prompt,  # Use raw prompt - no injection
        limits=Limits(max_tool_calls=20, max_repairs=1),
        expected=None  # No expected results for direct prompts
    )
    
    typer.echo(f"Running prompt: {prompt}")
    typer.echo(f"Defaults (if needed): {start_month}, {horizon} months, ${starting_cash:,.0f} starting cash")
    
    session_id = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M_%S')}_{str(uuid.uuid4())[:8]}"
    
    # Use prompt-specific runner that handles field injection
    from workbench.prompt_runner import run_prompt_task
    result = run_prompt_task(
        prompt=prompt,
        model=model,
        session_id=session_id,
        model_name=model_name,
        generate_ledger=generate_ledger,
        start_month_default=start_month,
        horizon_default=horizon,
        starting_cash_default=starting_cash
    )
    
    # Display results
    if result.initial_verdict != result.final_verdict:
        verdict_display = f"{result.initial_verdict} → {result.final_verdict}"
        if result.repair_made_feasible:
            verdict_display += " (repair successful)"
        else:
            verdict_display += " (repair failed)"
    else:
        verdict_display = result.initial_verdict
    
    typer.echo(f"Result: {verdict_display}")
    
    if result.score_earned is not None:
        typer.echo(f"Score: {result.score_earned}/{result.score_possible} ({result.score_percentage}%)")
        
        from workbench.prompt_scoring import calculate_prompt_score
        score_data = calculate_prompt_score(result)
        typer.echo("Breakdown:")
        for component, data in score_data["breakdown"].items():
            typer.echo(f"  └ {component.replace('_', ' ').title()}: {data['earned']}/{data['possible']}")
    
    if result.error_category:
        if result.score_earned is not None and result.score_possible is not None:
            typer.secho(f"Error: {result.error_category.value} (partial score: {result.score_earned}/{result.score_possible})", fg=typer.colors.RED)
        else:
            typer.secho(f"Error: {result.error_category.value}", fg=typer.colors.RED)
    
    if verbose:
        typer.echo(f"\nGenerated scenario:")
        if result.scenario_json:
            scenario_obj = json.loads(result.scenario_json) 
            typer.echo(json.dumps(scenario_obj, indent=2))


@app.command(name="run-comparison")
def comparison_cli(
    models: str = typer.Option(..., "--models", help="Comma-separated list of models (e.g., claude,claude-tools)"),
    task_sets: str = typer.Option(..., "--task-sets", help="Comma-separated list of task set directories"),
    runs: int = typer.Option(5, "--runs", help="Number of runs per condition"),
    session_id: Optional[str] = typer.Option(None, "--session-id", help="Custom session ID (auto-generated if not provided)"),
    prompt_dir: str = typer.Option("prompts/v2", "--prompts", help="Directory containing prompt files"),
    model_name: Optional[str] = typer.Option(None, "--model-name", help="Specific model name to pass to API (applies to all models)"),
    model_names: Optional[str] = typer.Option(None, "--model-names", help="Per-model names as model:name pairs (e.g., claude:claude-3-5-sonnet-20241022,haiku:claude-3-5-haiku-20241022)"),
    output_dir: str = typer.Option("reports", "--output", help="Output directory for results")
):
    """Run systematic comparison across models and task sets."""
    
    # Validate inputs
    try:
        # Check that task sets exist
        task_set_list = [ts.strip() for ts in task_sets.split(",")]
        for task_set in task_set_list:
            if not Path(task_set).exists():
                typer.secho(f"❌ Task set directory not found: {task_set}", fg=typer.colors.RED)
                raise typer.Exit(1)
                
            # Check for task files
            task_files = list(Path(task_set).glob("*.json"))
            if not task_files:
                typer.secho(f"❌ No task files found in: {task_set}", fg=typer.colors.RED)
                raise typer.Exit(1)
        
        # Parse model-names parameter if provided
        parsed_model_names = None
        if model_names:
            try:
                parsed_model_names = {}
                model_pairs = model_names.split(",")
                models_list = [m.strip() for m in models.split(",")]
                
                # Handle by position if we have duplicate model types
                if len(model_pairs) == len(models_list):
                    # Map by position: first model-name to first model, etc.
                    for i, pair in enumerate(model_pairs):
                        model_key, model_value = pair.strip().split(":", 1)
                        # Use model index as key for duplicates
                        index_key = f"{models_list[i]}_{i}"
                        parsed_model_names[index_key] = model_value.strip()
                    typer.echo(f"📝 Using positional model names mapping")
                else:
                    # Legacy behavior: map by model name
                    for pair in model_pairs:
                        model_key, model_value = pair.strip().split(":", 1)
                        parsed_model_names[model_key.strip()] = model_value.strip()
                    typer.echo(f"📝 Using per-model names: {parsed_model_names}")
            except ValueError as e:
                typer.secho(f"❌ Invalid model-names format. Expected model:name pairs separated by commas (e.g., claude:claude-3-5-sonnet-20241022,claude-tools:claude-3-5-haiku-20241022)", fg=typer.colors.RED)
                raise typer.Exit(1)
        
        # Validate that model-name and model-names are not both provided
        if model_name and model_names:
            typer.secho(f"❌ Cannot specify both --model-name and --model-names. Use --model-names for per-model specification.", fg=typer.colors.RED)
            raise typer.Exit(1)
        
        # Create configuration
        config = ComparisonConfig.from_csv_params(
            models_csv=models,
            task_sets_csv=task_sets,
            runs_per_condition=runs,
            session_id=session_id,
            prompt_dir=prompt_dir,
            model_name=model_name,
            model_names=parsed_model_names
        )
        
        # Display comparison plan
        typer.echo(f"🔬 Comparison Configuration:")
        typer.echo(f"   Models: {', '.join(config.models)}")
        if config.model_names or config.model_name:
            typer.echo(f"   Agent → Model Mapping:")
            for i, model in enumerate(config.models):
                model_name_to_use = config.get_model_name(model, i)
                if model_name_to_use:
                    typer.echo(f"     - Agent: {model} → Model: {model_name_to_use}")
                else:
                    typer.echo(f"     - Agent: {model} → Model: (default)")
        typer.echo(f"   Task Sets: {', '.join([Path(ts).name for ts in config.task_sets])}")
        typer.echo(f"   Runs per condition: {config.runs_per_condition}")
        typer.echo(f"   Total executions: {config.total_executions()}")
        typer.echo(f"   Session ID: {config.session_id}")
        typer.echo()
        
        # Confirm execution
        if config.total_executions() > 50:
            proceed = typer.confirm(f"This will run {config.total_executions()} individual tasks. Continue?")
            if not proceed:
                typer.echo("Comparison cancelled.")
                raise typer.Exit(0)
        
        # Run comparison
        comparison_result = run_comparison(config)
        
        # Save results
        output_path = save_comparison_results(comparison_result, output_dir)
        
        # Display summary
        typer.echo()
        typer.secho(f"✓ Comparison complete!", fg=typer.colors.GREEN)
        typer.echo(f"📊 Results saved to: {output_path}")
        typer.echo(f"📈 Report: {output_path}/comparison_report.md")
        typer.echo(f"📋 Raw data: {output_path}/raw_results.ndjson")
        
    except Exception as e:
        typer.secho(f"❌ Comparison failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()