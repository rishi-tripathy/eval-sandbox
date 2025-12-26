from workbench.task_types import TaskResult, ErrorCategory

def calculate_prompt_score(result: TaskResult) -> dict:
    """Calculate score for direct prompt tasks (limited scoring without expected results)."""
    points_earned = 0
    points_possible = 0
    breakdown = {}
    
    # Scenario Generation (20 pts - always applies)
    scenario_possible = 20
    if result.error_category is None:
        scenario_earned = 20  # Perfect execution
    elif result.error_category in [ErrorCategory.SCHEMA_MISMATCH, ErrorCategory.INVALID_JSON]:
        scenario_earned = 0   # Complete failure - can't even generate valid scenario
    else:
        scenario_earned = 10  # Partial credit - scenario worked but other issues
    
    breakdown["scenario_generation"] = {"earned": scenario_earned, "possible": scenario_possible}
    points_earned += scenario_earned
    points_possible += scenario_possible
    
    # Mathematical Precision (15 pts - only if ledger was requested)
    if result.draft_ledger_json is not None:
        ledger_possible = 15
        ledger_earned = 0
        if result.draft_ledger_correct:
            ledger_earned = 15  # Ledger matches simulator
        breakdown["mathematical_precision"] = {"earned": ledger_earned, "possible": ledger_possible}
        points_earned += ledger_earned
        points_possible += ledger_possible
    
    # Basic Feasibility Reasoning (10 pts - sanity check)
    reasoning_possible = 10
    if result.initial_verdict in ["feasible", "infeasible"]:
        reasoning_earned = 10  # Got a reasonable verdict
    else:
        reasoning_earned = 0
    
    breakdown["feasibility_reasoning"] = {"earned": reasoning_earned, "possible": reasoning_possible}
    points_earned += reasoning_earned
    points_possible += reasoning_possible
    
    # Calculate final percentage
    percentage = (points_earned / points_possible * 100) if points_possible > 0 else 0
    
    return {
        "points_earned": points_earned,
        "points_possible": points_possible,
        "percentage": round(percentage, 1),
        "breakdown": breakdown
    }

def update_prompt_result_with_score(result: TaskResult) -> TaskResult:
    """Update a TaskResult with prompt-specific scoring."""
    score_data = calculate_prompt_score(result)
    result.score_earned = score_data["points_earned"]
    result.score_possible = score_data["points_possible"]
    result.score_percentage = score_data["percentage"]
    return result