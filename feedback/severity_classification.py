SEVERITY_ICONS = {
    "HIGH": "🔴",
    "MEDIUM": "🟠",
    "LOW": "🟡"
}

def provide_feedback(issue: str, severity: str):
    icon = SEVERITY_ICONS.get(severity, "⚪")
    return f"{icon} [{severity}] {issue}"
