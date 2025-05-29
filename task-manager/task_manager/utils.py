def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    import datetime
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')



