def extract_snippet(file_path, line_no, context=2):
    """Extract raw code snippet (no markdown fences)."""
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        start = max(0, line_no - context - 1)
        end = min(len(lines), line_no + context)
        return "".join(lines[start:end]).strip()
    except Exception:
        return ""
