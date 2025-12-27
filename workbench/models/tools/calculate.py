def calculate(expression: str) -> str:
    try:
        return eval(expression)
    except Exception as e:
        return f"Error: {e}"