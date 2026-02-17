"""
Circuit breaker pattern for external API calls.
Prevents cascading failures by temporarily disabling calls
to a failing service after a threshold of consecutive failures.

Usage:
    breaker = CircuitBreaker("sendgrid")
    if not breaker.is_closed():
        return fallback()
    try:
        result = call_external_api()
        breaker.record_success()
        return result
    except Exception as e:
        breaker.record_failure()
        raise
"""

import time
import logging
from typing import Dict

logger = logging.getLogger("services.circuit_breaker")


class CircuitBreaker:
    """
    Simple circuit breaker with three states:
    - CLOSED (normal): calls go through
    - OPEN (tripped): calls are blocked, returns fallback
    - HALF_OPEN (testing): allows one call through to test recovery
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._success_count = 0

    @property
    def state(self) -> str:
        if self._state == self.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                logger.info(f"Circuit breaker [{self.name}] → HALF_OPEN (testing)")
        return self._state

    def is_closed(self) -> bool:
        """Return True if calls are allowed (CLOSED or HALF_OPEN)."""
        return self.state != self.OPEN

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == self.HALF_OPEN:
            logger.info(f"Circuit breaker [{self.name}] → CLOSED (recovered)")
        self._state = self.CLOSED
        self._failure_count = 0
        self._success_count += 1

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = self.OPEN
            logger.warning(
                f"Circuit breaker [{self.name}] → OPEN "
                f"(after {self._failure_count} failures, "
                f"recovery in {self.recovery_timeout}s)"
            )

    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
        }


# ---------------------------------------------------------------------------
# Global registry of circuit breakers
# ---------------------------------------------------------------------------
_breakers: Dict[str, CircuitBreaker] = {}


def get_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a named circuit breaker."""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name, **kwargs)
    return _breakers[name]


def get_all_statuses() -> list:
    """Return status of all circuit breakers."""
    return [b.get_status() for b in _breakers.values()]
