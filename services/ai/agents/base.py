"""BaseAgent abstract class — async process() with mock mode support."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base for all SK-powered agents.

    Subclasses must implement:
        _execute(input_data) — the real SK invocation
        _load_mock_response(input_data) — fixture-based response for tests
    """

    agent_name: str = "base"
    fixture_file: str | None = None

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Entry point — dispatches to mock or real execution."""
        if getattr(settings, "AI_MOCK_MODE", False):
            logger.info("[%s] mock mode — loading fixture", self.agent_name)
            return await self._load_mock_response(input_data)
        return await self._execute(input_data)

    @abstractmethod
    async def _execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the agent via Semantic Kernel."""
        ...

    async def _load_mock_response(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Load a mock response from the fixture file."""
        if self.fixture_file is None:
            raise NotImplementedError(
                f"{self.agent_name} has no fixture_file configured"
            )
        fixture_path = Path(settings.BASE_DIR) / "fixtures" / self.fixture_file
        text = fixture_path.read_text(encoding="utf-8")
        return json.loads(text)
