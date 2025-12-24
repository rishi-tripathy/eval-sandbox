def format_eval_failure(eval_result: dict) -> str:
    """Format eval result dict into a clear failure message for repair prompt."""
    
    verdict = eval_result.get("verdict")
    first_violation_month = eval_result.get("first_violation_month")
    violated_invariant = eval_result.get("violated_invariant")
    ledger_summary = eval_result.get("ledger_summary", {})
    violations = eval_result.get("violations", [])
    
    # Build failure message
    msg = f"The simulation was {verdict}.\n"
    
    if violated_invariant == "LIQUIDITY_FLOOR":
        msg += f"The scenario ran out of money in {first_violation_month}. "
        msg += f"Ending cash: ${ledger_summary.get('ending_cash', 0):,.0f}, "
        msg += f"Minimum cash: ${ledger_summary.get('min_cash', 0):,.0f}."
        
    elif violated_invariant == "MONEY_CONSERVATION":
        msg += "The financial calculations don't add up correctly. "
        msg += "This indicates an internal consistency error."
        
    elif violated_invariant == "TEMPORAL_CONSISTENCY":
        msg += "Events were scheduled outside valid time bounds. "
        msg += "Check event timing relative to the scenario timeline."
    
    # Add first violation details if available
    if violations and len(violations) > 0:
        first = violations[0]
        record = first.get("record", {})
        month = first.get('month')
            
        msg += f"\n\nIn {month}: "
        msg += f"Started with ${record.get('starting_cash', 0):,.0f}, "
        msg += f"income ${record.get('total_inflows', 0):,.0f}, "
        msg += f"expenses ${record.get('total_outflows', 0):,.0f}, "
        msg += f"ended with ${record.get('ending_cash', 0):,.0f}."
    
    return msg