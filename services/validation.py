"""
Input validation and proposal state machine.
"""

import re
import time
from collections import defaultdict
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Proposal state machine -- valid transitions
# ---------------------------------------------------------------------------
VALID_TRANSITIONS = {
    "draft": {"pending_review"},
    "pending_review": {"approved", "revision_requested", "rejected"},
    "revision_requested": {"pending_review", "rejected"},
    "approved": {"executing"},
    "executing": {"completed", "failed"},
    "completed": set(),
    "failed": {"pending_review"},
    "rejected": set(),
}

VALID_PROPOSAL_TYPES = {
    "campaign", "landing_page", "ad_copy", "budget", "strategy", "content", "general",
}

VALID_LEAD_STATUSES = {
    "new", "contacted", "qualified", "consultation_booked", "converted", "lost",
}


def validate_status_transition(current: str, new: str) -> Tuple[bool, str]:
    """Check if a proposal status transition is valid."""
    allowed = VALID_TRANSITIONS.get(current, set())
    if new in allowed:
        return True, ""
    return False, f"Invalid transition: {current} -> {new}. Allowed: {', '.join(allowed) or 'none'}"


def validate_lead_input(data: dict) -> Tuple[bool, list]:
    """Validate lead creation input. Returns (valid, errors)."""
    errors = []
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()

    if not name or len(name) < 2:
        errors.append("שם חייב להכיל לפחות 2 תווים")

    if not phone:
        errors.append("טלפון הוא שדה חובה")
    elif not re.match(r'^[\d\-\+\s\(\)]{7,20}$', phone):
        errors.append("מספר טלפון לא תקין")

    if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors.append("כתובת אימייל לא תקינה")

    return (len(errors) == 0, errors)


def validate_proposal_input(data: dict) -> Tuple[bool, list]:
    """Validate proposal creation input."""
    errors = []
    title = (data.get("title") or "").strip()
    ptype = (data.get("proposal_type") or "").strip()

    if not title:
        errors.append("Title is required")
    if ptype and ptype not in VALID_PROPOSAL_TYPES:
        errors.append(f"Invalid proposal_type: {ptype}. Allowed: {', '.join(VALID_PROPOSAL_TYPES)}")

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter
# ---------------------------------------------------------------------------
class RateLimiter:
    """Token-bucket rate limiter per key (e.g., IP or endpoint)."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits = defaultdict(list)

    def is_allowed(self, key: str = "global") -> bool:
        now = time.time()
        self._hits[key] = [t for t in self._hits[key] if t > now - self.window]
        if len(self._hits[key]) >= self.max_requests:
            return False
        self._hits[key].append(now)
        return True


# Singleton instances
chat_limiter = RateLimiter(max_requests=10, window_seconds=60)
api_limiter = RateLimiter(max_requests=30, window_seconds=60)
