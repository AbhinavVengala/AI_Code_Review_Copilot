SEVERITY_ICONS = {
    "HIGH": "🔴",
    "MEDIUM": "🟠",
    "LOW": "🟡"
}

def provide_feedback(issue, severity):
    icon = SEVERITY_ICONS.get(severity, "⚪")
    return f"{icon} [{severity}] {issue}"
