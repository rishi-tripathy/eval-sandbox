from workbench.task_types import Task, TaskResult, ErrorCategory

def calculate_task_score(result: TaskResult, task: Task) -> dict:
    """Calculate comprehensive score for a task result with variable point totals."""
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
    
    # Verdict Accuracy (25 pts - always applies)
    verdict_possible = 25
    if result.verdict_correct is None:
        verdict_earned = 0  # No expected result to compare against
    else:
        verdict_earned = 25 if result.verdict_correct else 0
    breakdown["verdict_accuracy"] = {"earned": verdict_earned, "possible": verdict_possible}
    points_earned += verdict_earned
    points_possible += verdict_possible
    
    # Violation Detection (20 pts - only applies to initially infeasible scenarios)
    if result.initial_verdict == "infeasible":
        violation_possible = 20
        violation_earned = 0
        if result.violation_correct is True:
            violation_earned += 10
        if result.first_violation_month_correct is True:
            violation_earned += 10
        breakdown["violation_detection"] = {"earned": violation_earned, "possible": violation_possible}
        points_earned += violation_earned
        points_possible += violation_possible
    
    # Repair Capability (20 pts - only applies when repair was attempted)
    if result.repair_attempted:
        repair_possible = 20
        repair_earned = 0
        
        # Repair effectiveness (15 pts)
        if result.repair_made_feasible is True:
            repair_earned += 15  # Successful repair
        elif result.error_category == ErrorCategory.REPAIR_FAILED:
            repair_earned += 3   # Attempted but ineffective repair
        
        # Repair labeling accuracy (5 pts) 
        if result.repair_label_accurate is True:
            repair_earned += 5   # Correctly labeled repair type
        
        breakdown["repair_capability"] = {"earned": repair_earned, "possible": repair_possible}
        points_earned += repair_earned
        points_possible += repair_possible
    
    # Mathematical Precision (15 pts - only applies to ledger generation tasks)
    if task.generate_ledger:
        ledger_possible = 15
        ledger_earned = 0
        if result.draft_ledger_correct is True:
            ledger_earned += 10  # Draft ledger accuracy
        if result.repair_ledger_correct is True:
            ledger_earned += 5   # Repair ledger accuracy (if applicable)
        breakdown["mathematical_precision"] = {"earned": ledger_earned, "possible": ledger_possible}
        points_earned += ledger_earned
        points_possible += ledger_possible
    
    # Calculate final percentage
    percentage = (points_earned / points_possible * 100) if points_possible > 0 else 0
    
    return {
        "points_earned": points_earned,
        "points_possible": points_possible,
        "percentage": round(percentage, 1),
        "breakdown": breakdown
    }

def update_result_with_score(result: TaskResult, task: Task) -> TaskResult:
    """Update a TaskResult with calculated score fields."""
    score_data = calculate_task_score(result, task)
    result.score_earned = score_data["points_earned"]
    result.score_possible = score_data["points_possible"]
    result.score_percentage = score_data["percentage"]
    return result