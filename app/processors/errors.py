class NonRetryableProcessingError(Exception):
    """Bad/unsupported/corrupt user file. Do not retry."""
    pass


class RetryableProcessingError(Exception):
    """Transient/system/storage errors. Safe to retry."""
    pass
