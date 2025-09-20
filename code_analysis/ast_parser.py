import ast

def analyze_code(code):
    try:
        tree = ast.parse(code)
        issues = []
    except SyntaxError as e:
        return [{"line": e.lineno, "col": e.offset, "text": f"Syntax error: {e.msg}"}]


    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not node.body:
            issues.append({
                "line": node.lineno,
                "col": node.col_offset,
                "text": f"AST: Empty function '{node.name}' found"
            })
    return issues