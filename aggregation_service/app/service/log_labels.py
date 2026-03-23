def format_source_log(source: str) -> str:
    label = {"kaggle": "Kaggle", "uci": "UCI"}.get((source or "").lower(), source or "?")
    return f"[{label}] "