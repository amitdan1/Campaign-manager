"""
Test prompt loader.
"""

import pytest
from prompts import load_prompt, reload_prompts


def test_load_lead_scoring_prompt():
    prompt = load_prompt("lead_scoring", "system")
    assert "lead qualification expert" in prompt.lower()
    assert "{memory_context}" in prompt


def test_load_strategy_prompt():
    prompt = load_prompt("strategy", "system")
    assert "{budget}" in prompt
    assert "{performance_data}" in prompt


def test_load_content_prompt():
    prompt = load_prompt("content", "system")
    assert "copywriter" in prompt.lower()


def test_load_orchestrator_prompt():
    prompt = load_prompt("orchestrator", "chat_system")
    assert "orchestrator" in prompt.lower()


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent_agent", "system")


def test_load_nonexistent_key():
    with pytest.raises(KeyError):
        load_prompt("lead_scoring", "nonexistent_key")


def test_reload_clears_cache():
    # Should not raise
    reload_prompts()
    prompt = load_prompt("lead_scoring", "system")
    assert len(prompt) > 0
