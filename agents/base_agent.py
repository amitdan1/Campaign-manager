"""
Base class for all marketing agents.
Every agent inherits from this and implements its own logic.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from config import Config


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Every agent must implement:
        - run()          : main execution logic
        - health_check() : verify the agent and its dependencies are working
    """

    def __init__(self, name: str):
        self.name = name
        self.config = Config
        self.logger = logging.getLogger(f"agent.{name}")
        self._setup_logging()
        self.logger.info(f"{self.name} initialized")

    def _setup_logging(self):
        """Configure logging for this agent."""
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            )

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        Returns a dict with results and any metadata.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check that the agent and its external dependencies are reachable.
        Returns {"healthy": True/False, "details": ...}
        """
        pass

    def _timestamp(self) -> str:
        """Current ISO timestamp."""
        return datetime.now().isoformat()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
