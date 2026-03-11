"""Token usage tracking for Azure OpenAI calls.

Logs input/output token counts per agent invocation. Token metadata is
extracted from SK ChatCompletion results when available.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Snapshot of token consumption for a single invocation."""

    agent_name: str
    deployment: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class TokenTracker:
    """Accumulates token usage across multiple invocations."""

    entries: list[TokenUsage] = field(default_factory=list)

    def record(
        self,
        agent_name: str,
        deployment: str,
        metadata: dict[str, Any] | None = None,
    ) -> TokenUsage:
        """Extract token counts from SK completion metadata and log them.

        Args:
            agent_name: Identifier for the calling agent.
            deployment: Azure OpenAI deployment used.
            metadata: The ``metadata`` dict from an SK ChatMessageContent,
                      expected to contain ``usage`` with ``prompt_tokens``
                      and ``completion_tokens``.

        Returns:
            The recorded TokenUsage entry.
        """
        input_tokens = 0
        output_tokens = 0

        if metadata:
            usage = metadata.get("usage")
            if usage:
                input_tokens = getattr(usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(usage, "completion_tokens", 0) or 0

        entry = TokenUsage(
            agent_name=agent_name,
            deployment=deployment,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self.entries.append(entry)

        logger.info(
            "Token usage [%s/%s]: in=%d out=%d total=%d",
            agent_name,
            deployment,
            input_tokens,
            output_tokens,
            entry.total_tokens,
        )
        return entry

    @property
    def total_input(self) -> int:
        return sum(e.input_tokens for e in self.entries)

    @property
    def total_output(self) -> int:
        return sum(e.output_tokens for e in self.entries)

    @property
    def total(self) -> int:
        return self.total_input + self.total_output
