import json

def check_json(response_text: str) -> bool:
    """
    Check if a string contains valid JSON.
    
    Args:
        response_text: The text to check for valid JSON
        
    Returns:
        bool: True if the string is valid JSON, False otherwise
    """
    try:
        json.loads(response_text.strip())
        return True
    except (json.JSONDecodeError, ValueError):
        return False