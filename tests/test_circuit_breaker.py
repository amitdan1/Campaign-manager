"""
Test circuit breaker behavior.
"""

from services.circuit_breaker import CircuitBreaker


def test_starts_closed():
    cb = CircuitBreaker("test", failure_threshold=3)
    assert cb.state == CircuitBreaker.CLOSED
    assert cb.is_closed() is True


def test_opens_after_threshold():
    cb = CircuitBreaker("test2", failure_threshold=3)
    cb.record_failure()
    cb.record_failure()
    assert cb.is_closed() is True
    cb.record_failure()
    assert cb.state == CircuitBreaker.OPEN
    assert cb.is_closed() is False


def test_success_resets_failures():
    cb = CircuitBreaker("test3", failure_threshold=3)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb._failure_count == 0
    assert cb.state == CircuitBreaker.CLOSED


def test_half_open_after_timeout():
    cb = CircuitBreaker("test4", failure_threshold=1, recovery_timeout=0.01)
    cb.record_failure()
    assert cb.state == CircuitBreaker.OPEN

    import time
    time.sleep(0.02)

    assert cb.state == CircuitBreaker.HALF_OPEN
    assert cb.is_closed() is True


def test_status_dict():
    cb = CircuitBreaker("status_test", failure_threshold=5)
    cb.record_success()
    status = cb.get_status()
    assert status["name"] == "status_test"
    assert status["state"] == "closed"
    assert status["success_count"] == 1
