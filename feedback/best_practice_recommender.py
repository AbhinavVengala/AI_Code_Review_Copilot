def recommend_best_practices(code: str):
    recommendations = []

    if "eval(" in code:
        recommendations.append("Avoid using eval(); consider safer alternatives like ast.literal_eval.")
    if "open(" in code and "with" not in code:
        recommendations.append("Use context managers (with ... ) when handling files.")
    if "def " in code and '"""' not in code:
        recommendations.append("Add docstrings to functions for better maintainability.")

    # Generic fallback
    if not recommendations:
        recommendations.append("Follow coding standards and best practices.")

    return recommendations
