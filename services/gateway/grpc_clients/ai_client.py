"""gRPC client for AI service.

Provides typed methods for all AiService RPCs.
Full implementations will connect to the gRPC channel in later milestones.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AiClient:
    """gRPC client for AI service."""

    def __init__(self, address: str = "localhost:50052") -> None:
        self.address = address

    def trigger_chat_processing(
        self, idea_id: str, message_id: str
    ) -> dict[str, Any]:
        logger.warning("AiClient.trigger_chat_processing stub called")
        return {"status": "accepted", "processing_id": ""}

    def trigger_brd_generation(
        self,
        idea_id: str,
        mode: str = "full",
        sections_to_regenerate: list[str] | None = None,
        instruction: str = "",
        allow_information_gaps: bool = False,
    ) -> dict[str, Any]:
        logger.warning("AiClient.trigger_brd_generation stub called")
        return {"status": "accepted", "generation_id": ""}

    def trigger_context_reindex(
        self, bucket_id: str
    ) -> dict[str, Any]:
        logger.warning("AiClient.trigger_context_reindex stub called")
        return {"status": "accepted", "chunk_count": 0}

    def get_facilitator_bucket(self) -> dict[str, Any]:
        logger.warning("AiClient.get_facilitator_bucket stub called")
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def update_facilitator_bucket(
        self, content: str, updated_by_id: str
    ) -> dict[str, Any]:
        logger.warning("AiClient.update_facilitator_bucket stub called")
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def get_context_agent_bucket(self) -> dict[str, Any]:
        logger.warning("AiClient.get_context_agent_bucket stub called")
        return {
            "id": "",
            "sections_json": "{}",
            "free_text": "",
            "updated_by_id": "",
            "updated_at": "",
        }

    def update_context_agent_bucket(
        self, sections_json: str, free_text: str, updated_by_id: str
    ) -> dict[str, Any]:
        logger.warning("AiClient.update_context_agent_bucket stub called")
        return {
            "id": "",
            "sections_json": "{}",
            "free_text": "",
            "updated_by_id": "",
            "updated_at": "",
        }

    def get_ai_metrics(
        self, time_range: str = "24h"
    ) -> dict[str, Any]:
        logger.warning("AiClient.get_ai_metrics stub called")
        return {
            "processing_count": 0,
            "success_rate": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "delegation_count": 0,
            "compression_count": 0,
            "board_agent_count": 0,
            "error_count": 0,
            "abort_count": 0,
            "extension_count": 0,
        }
