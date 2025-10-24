import re

def predict_bug_risk(code_snippet: str):
    """
    Predicts bug risk based on simple heuristics.
    Returns 'HIGH', 'MEDIUM', or 'LOW'.
    """
    lines = code_snippet.splitlines()
    line_count = len(lines)

    # HIGH risk indicators
    if line_count > 100:
        return "HIGH"
    if re.search(r'#\s*(FIXME|TODO)', code_snippet, re.IGNORECASE):
        return "HIGH"
    if re.search(r'\beval\s*\(|\bexec\s*\(', code_snippet):
        return "HIGH"

    # MEDIUM risk indicators
    if line_count > 50:
        return "MEDIUM"
    # Bare except
    if re.search(r'^\s*except\s*:', code_snippet, re.MULTILINE):
        return "MEDIUM"
    
    # Simple complexity check
    complexity = len(re.findall(r'\b(if|for|while|elif|else)\b', code_snippet))
    if complexity > 10:
        return "MEDIUM"

    return "LOW"
