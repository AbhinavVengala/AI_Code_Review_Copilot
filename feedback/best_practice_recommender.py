def recommend_best_practices(issue):
    recommendations = {
        "eval": "Avoid using eval() — consider safer alternatives.",
        "empty function": "Implement logic or remove empty functions to improve readability."
    }
    return recommendations.get(issue.lower(), "Follow coding standards.")
