def duration_advisor(event_description: str) -> dict:
    """Determine if an event description suggests a one-time occurrence."""
    description = event_description.lower().strip()
    
    # Keywords that strongly suggest ONE-TIME events
    one_time_indicators = [
        "purchase", "buy", "bought", "deposit", "down payment",
        "surgery", "repair", "wedding", "vacation", "trip", 
        "bonus", "gift", "refund", "investment", "equipment",
        "fee", "fine", "penalty", "installation", "setup",
        "emergency", "accident", "medical", "dental"
    ]
    
    for keyword in one_time_indicators:
        if keyword in description:
            return {
                "appears_one_time": True,
                "reasoning": f"'{keyword}' typically indicates a single occurrence. If that makes sense to you, return 1 for the duration_months."
            }
    
    return {
        "appears_one_time": False, 
        "reasoning": "No clear one-time indicators detected. Use your best judgment to determine the duration of the event."
    }