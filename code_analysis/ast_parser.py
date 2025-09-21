import ast

def analyze_code(code: str):
    """Detect empty functions or other AST-based patterns"""
    issues = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.body) == 0:
                issues.append({"line": node.lineno, "col": 0, "text": f"Empty function '{node.name}'"})
    except Exception as e:
        issues.append({"line": 0, "col": 0, "text": f"AST parse error: {e}"})
    return issues
