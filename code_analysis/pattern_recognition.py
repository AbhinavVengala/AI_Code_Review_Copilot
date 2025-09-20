def detect_patterns(code):
    issues = []
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if "eval(" in line:
            issues.append({
                "line": i + 1,
                "col": line.find("eval(") + 1,
                "text": "Pattern: Use of 'eval' detected — potential security risk"
            })
    return issues