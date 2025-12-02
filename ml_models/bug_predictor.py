from radon.complexity import cc_visit



def analyze_complexity(code: str):
    """
    Analyzes the Cyclomatic Complexity of the entire code.
    Returns a list of blocks with their complexity.
    """
    try:
        return cc_visit(code)
    except Exception:
        return []

def predict_risk_for_line(blocks, line_no):
    """
    Determines risk level based on the complexity of the block containing the line.
    """
    for block in blocks:
        if block.lineno <= line_no <= block.endline:
            if block.complexity > 10:
                return "HIGH"
            elif block.complexity > 5:
                return "MEDIUM"
    return "LOW"
