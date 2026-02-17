"""
OpenAI API service wrapper.
Provides a simple interface for all LLM-powered agents.
B5: Includes exponential backoff retry on transient errors.
"""

import json
import logging
import time
from datetime import date
from typing import Any, Dict, Optional

from config import Config
from services.circuit_breaker import get_breaker

logger = logging.getLogger("services.openai")

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds

# Daily token budget (configurable via env)
DAILY_TOKEN_LIMIT = Config.DAILY_TOKEN_LIMIT


class TokenTracker:
    """Tracks daily token usage across all OpenAI calls."""

    def __init__(self):
        self._date = date.today()
        self._tokens_used = 0

    def _reset_if_new_day(self):
        today = date.today()
        if today != self._date:
            self._date = today
            self._tokens_used = 0

    def record(self, prompt_tokens: int, completion_tokens: int):
        self._reset_if_new_day()
        self._tokens_used += prompt_tokens + completion_tokens

    def is_within_budget(self) -> bool:
        self._reset_if_new_day()
        return self._tokens_used < DAILY_TOKEN_LIMIT

    @property
    def tokens_used_today(self) -> int:
        self._reset_if_new_day()
        return self._tokens_used

    @property
    def tokens_remaining(self) -> int:
        self._reset_if_new_day()
        return max(0, DAILY_TOKEN_LIMIT - self._tokens_used)


# Singleton token tracker
token_tracker = TokenTracker()


class OpenAIService:
    """Wrapper around the OpenAI API for all AI agent calls."""

    def __init__(self):
        if not Config.is_openai_configured():
            logger.warning(
                "OpenAI API key not configured. AI-powered agents will use fallback logic. "
                "Set OPENAI_API_KEY in your .env file."
            )
            self.client = None
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> Optional[str]:
        """
        Send a chat completion request with retry on transient errors.
        Returns the assistant's response text, or None if unavailable.
        """
        if not self.client:
            return None

        breaker = get_breaker("openai")
        if not breaker.is_closed():
            logger.warning("OpenAI circuit breaker OPEN -- returning None")
            return None

        if not token_tracker.is_within_budget():
            logger.warning(f"Daily token budget exhausted ({token_tracker.tokens_used_today} used). Returning None.")
            return None

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                # Track token usage
                usage = response.usage
                if usage:
                    token_tracker.record(usage.prompt_tokens, usage.completion_tokens)
                breaker.record_success()
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                # Retry on rate limits (429) and server errors (5xx)
                if "429" in str(e) or "rate" in err_str or "500" in str(e) or "502" in str(e) or "503" in str(e):
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"OpenAI transient error (attempt {attempt+1}/{MAX_RETRIES}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                # Non-retryable error
                logger.error(f"OpenAI API error (non-retryable): {e}")
                return None

        breaker.record_failure()
        logger.error(f"OpenAI API failed after {MAX_RETRIES} retries: {last_error}")
        return None

    def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a chat request and parse the response as JSON.
        Returns parsed dict, or None on failure.
        """
        raw = self.chat(system_prompt, user_message, temperature, max_tokens)
        if not raw:
            return None

        try:
            cleaned = raw.strip()
            # Strip markdown code fences
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                cleaned = "\n".join(lines)

            # Try to extract JSON from text that may have surrounding content
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start >= 0 and end > start:
                cleaned = cleaned[start:end]

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}\nRaw: {raw[:500]}")
            return None

    def is_available(self) -> bool:
        """Check if the OpenAI service is configured."""
        return self.client is not None

    @staticmethod
    def get_token_stats() -> Dict[str, Any]:
        """Return current token usage stats."""
        return {
            "tokens_used_today": token_tracker.tokens_used_today,
            "tokens_remaining": token_tracker.tokens_remaining,
            "daily_limit": DAILY_TOKEN_LIMIT,
        }
