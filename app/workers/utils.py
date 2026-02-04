def compute_backoff_seconds(attempts: int) -> int:
    return min(2**attempts, 300)
