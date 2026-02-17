"""
Test validation functions and state machine.
"""

from services.validation import (
    validate_lead_input,
    validate_proposal_input,
    validate_status_transition,
    RateLimiter,
)


# --- Lead validation ---

def test_lead_valid():
    valid, errors = validate_lead_input({"name": "John", "phone": "052-1234567"})
    assert valid is True
    assert errors == []


def test_lead_missing_name():
    valid, errors = validate_lead_input({"name": "", "phone": "052-1234567"})
    assert valid is False
    assert len(errors) == 1


def test_lead_missing_phone():
    valid, errors = validate_lead_input({"name": "John", "phone": ""})
    assert valid is False


def test_lead_invalid_email():
    valid, errors = validate_lead_input({"name": "John", "phone": "052-1234567", "email": "bad"})
    assert valid is False


def test_lead_valid_email():
    valid, errors = validate_lead_input({"name": "John", "phone": "052-1234567", "email": "test@example.com"})
    assert valid is True


# --- Proposal validation ---

def test_proposal_valid():
    valid, errors = validate_proposal_input({"title": "Test", "proposal_type": "campaign"})
    assert valid is True


def test_proposal_missing_title():
    valid, errors = validate_proposal_input({"title": ""})
    assert valid is False


def test_proposal_invalid_type():
    valid, errors = validate_proposal_input({"title": "Test", "proposal_type": "invalid"})
    assert valid is False


# --- State machine ---

def test_valid_transitions():
    valid, _ = validate_status_transition("pending_review", "approved")
    assert valid is True

    valid, _ = validate_status_transition("pending_review", "rejected")
    assert valid is True

    valid, _ = validate_status_transition("approved", "executing")
    assert valid is True

    valid, _ = validate_status_transition("executing", "completed")
    assert valid is True


def test_invalid_transitions():
    valid, msg = validate_status_transition("pending_review", "completed")
    assert valid is False
    assert "Invalid transition" in msg

    valid, _ = validate_status_transition("completed", "approved")
    assert valid is False

    valid, _ = validate_status_transition("rejected", "approved")
    assert valid is False


# --- Rate limiter ---

def test_rate_limiter_allows():
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("test") is True
    assert limiter.is_allowed("test") is True
    assert limiter.is_allowed("test") is True


def test_rate_limiter_blocks():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("key1") is True
    assert limiter.is_allowed("key1") is True
    assert limiter.is_allowed("key1") is False


def test_rate_limiter_separate_keys():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    assert limiter.is_allowed("a") is True
    assert limiter.is_allowed("b") is True
    assert limiter.is_allowed("a") is False
