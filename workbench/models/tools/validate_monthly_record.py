import json

def validate_monthly_record(monthly_record_json: str, scenario_context_json: str = None) -> dict:
    """Validate that a monthly record has correct arithmetic and base monthly semantics."""
    try:
        record = json.loads(monthly_record_json)
        
        # Check required fields exist
        required_fields = ["starting_cash", "total_inflows", "total_outflows", "ending_cash"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}"
            }
        
        # Check arithmetic: starting_cash + total_inflows + total_outflows = ending_cash
        starting = record["starting_cash"]
        inflows = record["total_inflows"] 
        outflows = record["total_outflows"]  # Should be negative
        ending = record["ending_cash"]
        
        calculated_ending = starting + inflows + outflows
        
        # Arithmetic validation
        if abs(calculated_ending - ending) > 0.01:
            return {
                "valid": False,
                "error": f"Arithmetic error: {starting} + {inflows} + {outflows} = {calculated_ending}, but ending_cash is {ending}"
            }
        
        # Base monthly semantics validation (if scenario context provided)
        if scenario_context_json:
            try:
                scenario = json.loads(scenario_context_json)
                base_monthly = scenario.get("base_monthly", {})
                expected_base_salary = base_monthly.get("takehome_salary")
                expected_base_outflows = base_monthly.get("outflows")
                
                # Check base_takehome_salary matches scenario
                if "base_takehome_salary" in record and expected_base_salary is not None:
                    if abs(record["base_takehome_salary"] - expected_base_salary) > 0.01:
                        return {
                            "valid": False,
                            "error": f"Base monthly semantic error: base_takehome_salary should always be {expected_base_salary} (from scenario base_monthly), but found {record['base_takehome_salary']}. IMPORTANT: base_monthly values NEVER change during simulation - model salary increases as events that ADD to the base amount."
                        }
                
                # Check base_outflows matches scenario  
                if "base_outflows" in record and expected_base_outflows is not None:
                    if abs(record["base_outflows"] - expected_base_outflows) > 0.01:
                        return {
                            "valid": False,
                            "error": f"Base monthly semantic error: base_outflows should always be {expected_base_outflows} (from scenario base_monthly), but found {record['base_outflows']}. IMPORTANT: base_monthly values NEVER change during simulation - model expense changes as events that ADD to the base amount."
                        }
                        
            except json.JSONDecodeError:
                # If scenario context is invalid JSON, just skip semantic validation
                pass
        
        return {"valid": True, "message": "Arithmetic and semantics are correct"}
            
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}