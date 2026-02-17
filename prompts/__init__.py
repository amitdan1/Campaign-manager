"""
Centralized prompt loader -- all LLM prompts live in YAML files in this directory.
Usage:
    from prompts import load_prompt
    prompt = load_prompt("lead_scoring", "system")
    formatted = prompt.format(memory_context=ctx)
"""

import os
from functools import lru_cache
from pathlib import Path

import yaml

_PROMPTS_DIR = Path(__file__).parent


@lru_cache(maxsize=64)
def _load_yaml(filename: str) -> dict:
    """Load and cache a YAML prompt file."""
    filepath = _PROMPTS_DIR / f"{filename}.yaml"
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(agent: str, key: str = "system") -> str:
    """
    Load a specific prompt string from prompts/<agent>.yaml.

    Args:
        agent: YAML filename (without extension), e.g. 'lead_scoring'
        key: top-level key inside the YAML file, e.g. 'system', 'user_ad_copy'
    Returns:
        The prompt string (may contain {placeholders} for .format())
    """
    data = _load_yaml(agent)
    if key not in data:
        raise KeyError(f"Prompt key '{key}' not found in prompts/{agent}.yaml. Available: {list(data.keys())}")
    return data[key]


def reload_prompts() -> None:
    """Clear the LRU cache so prompts are re-read from disk."""
    _load_yaml.cache_clear()
