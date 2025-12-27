import json
import re
from typing import Dict, Any, List

def finalize_json(response_text: str, expected_schema: str = "scenario") -> dict:
    """Extract, clean, and validate JSON from Claude's response text."""
    
    result = {
        "valid": False,
        "cleaned_json": None,
        "fixes_applied": [],
        "errors": [],
        "validation_results": {}
    }
    
    try:
        # Step 1: Try to extract JSON from potentially messy text
        extracted_json, extraction_fixes = _extract_json_from_text(response_text)
        result["fixes_applied"].extend(extraction_fixes)
        
        if not extracted_json:
            result["errors"].append("No valid JSON found in response text")
            return result
            
        # Step 2: Parse and clean the JSON
        try:
            parsed_json = json.loads(extracted_json)
            result["cleaned_json"] = parsed_json
        except json.JSONDecodeError as e:
            result["errors"].append(f"JSON parsing failed: {str(e)}")
            return result
            
        # Step 3: Validate against expected schema
        validation_results = _validate_schema(parsed_json, expected_schema)
        result["validation_results"] = validation_results
        
        if validation_results.get("schema_valid", False):
            result["valid"] = True
        else:
            result["errors"].extend(validation_results.get("errors", []))
            
        return result
        
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        return result

def _extract_json_from_text(text: str):
    """Extract JSON from potentially messy response text."""
    fixes_applied = []
    
    # Pattern 1: Markdown code blocks
    markdown_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    markdown_match = re.search(markdown_pattern, text, re.DOTALL)
    if markdown_match:
        fixes_applied.append("Extracted JSON from markdown code block")
        return markdown_match.group(1).strip(), fixes_applied
    
    # Pattern 2: Look for largest complete JSON object
    json_pattern = r'\{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*\}'
    json_matches = re.findall(json_pattern, text, re.DOTALL)
    
    if json_matches:
        # Take the longest match (likely the main response)
        longest_json = max(json_matches, key=len)
        
        # Check if it was embedded in other text
        if text.strip() != longest_json.strip():
            fixes_applied.append("Extracted JSON from explanatory text")
            
        return longest_json.strip(), fixes_applied
    
    # Pattern 3: Try to parse the entire text as JSON
    try:
        json.loads(text.strip())
        return text.strip(), fixes_applied
    except json.JSONDecodeError:
        pass
    
    return None, fixes_applied

def _validate_schema(parsed_json: Dict[str, Any], expected_schema: str) -> Dict[str, Any]:
    """Validate JSON against expected schema."""
    validation_result = {
        "schema_valid": False,
        "errors": []
    }
    
    try:
        if expected_schema == "scenario":
            validation_result.update(_validate_scenario_schema(parsed_json))
        elif expected_schema == "repair":
            validation_result.update(_validate_repair_schema(parsed_json))
        else:
            validation_result["errors"].append(f"Unknown schema type: {expected_schema}")
            
    except Exception as e:
        validation_result["errors"].append(f"Schema validation error: {str(e)}")
    
    return validation_result

def _validate_scenario_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate scenario JSON structure."""
    result = {"schema_valid": True, "errors": [], "warnings": []}
    
    # Check for required top-level fields
    if "scenario" in data:
        scenario = data["scenario"]
    else:
        scenario = data
        result["warnings"].append("Expected 'scenario' wrapper, but found direct scenario data")
    
    # Required scenario fields
    required_fields = ["id", "title", "start_month", "horizon_months", "initial_state", "base_monthly", "events"]
    for field in required_fields:
        if field not in scenario:
            result["errors"].append(f"Missing required field: {field}")
            result["schema_valid"] = False
    
    # Validate sign conventions
    if "base_monthly" in scenario:
        base_monthly = scenario["base_monthly"]
        if "takehome_salary" in base_monthly and base_monthly["takehome_salary"] < 0:
            result["errors"].append("takehome_salary must be non-negative")
            result["schema_valid"] = False
        if "outflows" in base_monthly and base_monthly["outflows"] > 0:
            result["errors"].append("outflows must be non-positive")
            result["schema_valid"] = False
    
    # Validate events structure
    if "events" in scenario:
        for i, event in enumerate(scenario["events"]):
            if not isinstance(event, dict):
                result["errors"].append(f"Event {i} is not a valid object")
                result["schema_valid"] = False
                continue
                
            event_required = ["label", "start_month", "amount"]
            for field in event_required:
                if field not in event:
                    result["errors"].append(f"Event {i} missing required field: {field}")
                    result["schema_valid"] = False
    
    return result

def _validate_repair_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate repair JSON structure."""
    result = {"schema_valid": True, "errors": []}
    
    # Required repair fields
    required_fields = ["repaired_scenario", "repair_applied"]
    for field in required_fields:
        if field not in data:
            result["errors"].append(f"Missing required field: {field}")
            result["schema_valid"] = False
    
    # Validate repair_applied structure
    if "repair_applied" in data:
        repair_applied = data["repair_applied"]
        repair_required = ["type", "changes"]
        for field in repair_required:
            if field not in repair_applied:
                result["errors"].append(f"repair_applied missing required field: {field}")
                result["schema_valid"] = False
                
        valid_types = ["baseline_reduction", "event_amount_adjustment", "event_timing_shift"]
        if "type" in repair_applied and repair_applied["type"] not in valid_types:
            result["errors"].append(f"Invalid repair type: {repair_applied['type']}")
            result["schema_valid"] = False
    
    # Validate the repaired scenario itself
    if "repaired_scenario" in data:
        scenario_validation = _validate_scenario_schema(data["repaired_scenario"])
        if not scenario_validation["schema_valid"]:
            result["errors"].extend([f"Repaired scenario: {err}" for err in scenario_validation["errors"]])
            result["schema_valid"] = False
    
    return result