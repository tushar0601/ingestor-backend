ALLOWED_TRANSITIONS = {
    "PENDING_UPLOAD": {"UPLOADED", "EXPIRED", "ABORTED"},
    "UPLOADED": {"PROCESSING"},
    "PROCESSING": {"PROCESSED", "FAILED"},
    "PROCESSED": set(),
    "FAILED": set(),
    "EXPIRED": set(),
    "ABORTED": set(),
}


def assert_transition(old: str, new: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(old, set())
    if new not in allowed:
        raise ValueError(f"Invalid upload state transition: {old} -> {new}")