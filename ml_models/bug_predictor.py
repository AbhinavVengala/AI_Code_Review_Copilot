import random

def predict_bug_risk(code_snippet: str):
    """
    Returns 'HIGH', 'MEDIUM', or 'LOW'
    In real scenario, train model on historical code issues
    """
    return random.choice(["HIGH", "MEDIUM", "LOW"])
