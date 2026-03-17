"""gRPC client for AI service."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import grpc


# Ensure proto directory is on sys.path for generated imports
def _find_proto_dir() -> str:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        candidate = current / "proto"
        if candidate.is_dir():
            return str(candidate)
        current = current.parent
    return ""

_proto_dir = _find_proto_dir()
if _proto_dir and _proto_dir not in sys.path:
    sys.path.insert(0, _proto_dir)

import ai_pb2  # noqa: E402
import ai_pb2_grpc  # noqa: E402

logger = logging.getLogger(__name__)


class AiClient:
    """gRPC client for AI service."""

    def __init__(self, address: str = "localhost:50052") -> None:
        self.address = address
        self._channel: grpc.Channel | None = None
        self._stub: ai_pb2_grpc.AiServiceStub | None = None

    def _ensure_channel(self) -> ai_pb2_grpc.AiServiceStub:
        if self._stub is None:
            self._channel = grpc.insecure_channel(self.address)
            self._stub = ai_pb2_grpc.AiServiceStub(self._channel)
        return self._stub

    def trigger_chat_processing(
        self, project_id: str, message_id: str
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.ChatProcessingRequest(
            project_id=project_id,
            message_id=message_id,
        )
        response = stub.TriggerChatProcessing(request)
        logger.info(
            "AI trigger_chat_processing: project=%s, status=%s, processing_id=%s",
            project_id, response.status, response.processing_id,
        )
        return {"status": response.status, "processing_id": response.processing_id}

    def trigger_brd_generation(
        self,
        project_id: str,
        mode: str = "full_generation",
        section_name: str = "",
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.BrdGenerationRequest(
            project_id=project_id,
            mode=mode,
        )
        response = stub.TriggerBrdGeneration(request)
        return {"status": response.status, "generation_id": response.generation_id}

    def trigger_context_reindex(
        self, bucket_id: str
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.ContextReindexRequest(bucket_id=bucket_id)
        response = stub.TriggerContextReindex(request)
        return {"status": response.status, "chunk_count": response.chunk_count}

    def get_facilitator_bucket(self) -> dict[str, Any]:
        stub = self._ensure_channel()
        from google.protobuf.empty_pb2 import Empty
        response = stub.GetFacilitatorBucket(Empty())
        return {
            "id": response.id,
            "content": response.content,
            "updated_by_id": response.updated_by_id,
            "updated_at": response.updated_at,
        }

    def update_facilitator_bucket(
        self, content: str, updated_by_id: str
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.UpdateFacilitatorBucketRequest(
            content=content,
            updated_by_id=updated_by_id,
        )
        response = stub.UpdateFacilitatorBucket(request)
        return {
            "id": response.id,
            "content": response.content,
            "updated_by_id": response.updated_by_id,
            "updated_at": response.updated_at,
        }

    def get_context_agent_bucket(self) -> dict[str, Any]:
        stub = self._ensure_channel()
        from google.protobuf.empty_pb2 import Empty
        response = stub.GetContextAgentBucket(Empty())
        return {
            "id": response.id,
            "sections_json": response.sections_json,
            "free_text": response.free_text,
            "updated_by_id": response.updated_by_id,
            "updated_at": response.updated_at,
        }

    def update_context_agent_bucket(
        self, sections_json: str, free_text: str, updated_by_id: str
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.UpdateContextAgentBucketRequest(
            sections_json=sections_json,
            free_text=free_text,
            updated_by_id=updated_by_id,
        )
        response = stub.UpdateContextAgentBucket(request)
        return {
            "id": response.id,
            "sections_json": response.sections_json,
            "free_text": response.free_text,
            "updated_by_id": response.updated_by_id,
            "updated_at": response.updated_at,
        }

    def get_ai_metrics(
        self, time_range: str = "24h"
    ) -> dict[str, Any]:
        stub = self._ensure_channel()
        request = ai_pb2.AiMetricsRequest(time_range=time_range)
        response = stub.GetAiMetrics(request)
        return {
            "processing_count": response.processing_count,
            "success_rate": response.success_rate,
            "latency_p50_ms": response.latency_p50_ms,
            "latency_p95_ms": response.latency_p95_ms,
            "total_input_tokens": response.total_input_tokens,
            "total_output_tokens": response.total_output_tokens,
            "delegation_count": response.delegation_count,
            "compression_count": response.compression_count,
            "error_count": response.error_count,
            "abort_count": response.abort_count,
            "extension_count": response.extension_count,
        }

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()
            self._channel = None
            self._stub = None
