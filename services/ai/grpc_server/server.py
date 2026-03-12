"""AI service gRPC server setup.

Starts a gRPC server on port 50052 serving AiService RPCs.
"""

import logging
import sys
from concurrent import futures
from pathlib import Path

import grpc

# Ensure the app root is on sys.path
_app_root = str(Path(__file__).resolve().parent.parent)
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

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

from grpc_server.servicers.context_servicer import AiContextServicer  # noqa: E402
from grpc_server.servicers.processing_servicer import AiProcessingServicer  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_PORT = 50052


class CombinedAiServicer(ai_pb2_grpc.AiServiceServicer):
    """Combined servicer that delegates to processing and context servicers,
    converting dict returns into proper protobuf messages."""

    def __init__(self) -> None:
        self._processing = AiProcessingServicer()
        self._context = AiContextServicer()

    def TriggerChatProcessing(self, request, context):
        result = self._processing.TriggerChatProcessing(request, context)
        return ai_pb2.ChatProcessingResponse(
            status=result.get("status", ""),
            processing_id=result.get("processing_id", ""),
        )

    def TriggerBrdGeneration(self, request, context):
        result = self._processing.TriggerBrdGeneration(request, context)
        return ai_pb2.BrdGenerationResponse(
            status=result.get("status", ""),
            generation_id=result.get("generation_id", ""),
        )

    def TriggerContextReindex(self, request, context):
        result = self._processing.TriggerContextReindex(request, context)
        return ai_pb2.ContextReindexResponse(
            status=result.get("status", ""),
            chunk_count=result.get("chunk_count", 0),
        )

    def GetFacilitatorBucket(self, request, context):
        result = self._context.GetFacilitatorBucket(request, context)
        return ai_pb2.FacilitatorBucketResponse(
            id=result.get("id", ""),
            content=result.get("content", ""),
            updated_by_id=result.get("updated_by_id", ""),
            updated_at=result.get("updated_at", ""),
        )

    def UpdateFacilitatorBucket(self, request, context):
        result = self._context.UpdateFacilitatorBucket(request, context)
        return ai_pb2.FacilitatorBucketResponse(
            id=result.get("id", ""),
            content=result.get("content", ""),
            updated_by_id=result.get("updated_by_id", ""),
            updated_at=result.get("updated_at", ""),
        )

    def GetContextAgentBucket(self, request, context):
        result = self._context.GetContextAgentBucket(request, context)
        return ai_pb2.ContextAgentBucketResponse(
            id=result.get("id", ""),
            sections_json=result.get("sections_json", "{}"),
            free_text=result.get("free_text", ""),
            updated_by_id=result.get("updated_by_id", ""),
            updated_at=result.get("updated_at", ""),
        )

    def UpdateContextAgentBucket(self, request, context):
        result = self._context.UpdateContextAgentBucket(request, context)
        return ai_pb2.ContextAgentBucketResponse(
            id=result.get("id", ""),
            sections_json=result.get("sections_json", "{}"),
            free_text=result.get("free_text", ""),
            updated_by_id=result.get("updated_by_id", ""),
            updated_at=result.get("updated_at", ""),
        )

    def GetAiMetrics(self, request, context):
        result = self._processing.GetAiMetrics(request, context)
        return ai_pb2.AiMetricsResponse(
            processing_count=result.get("processing_count", 0),
            success_rate=result.get("success_rate", 0.0),
            latency_p50_ms=result.get("latency_p50_ms", 0.0),
            latency_p95_ms=result.get("latency_p95_ms", 0.0),
            total_input_tokens=result.get("total_input_tokens", 0),
            total_output_tokens=result.get("total_output_tokens", 0),
            delegation_count=result.get("delegation_count", 0),
            compression_count=result.get("compression_count", 0),
            board_agent_count=result.get("board_agent_count", 0),
            error_count=result.get("error_count", 0),
            abort_count=result.get("abort_count", 0),
            extension_count=result.get("extension_count", 0),
        )


def serve(port: int = DEFAULT_PORT) -> grpc.Server:
    """Create and start the AI gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = CombinedAiServicer()
    ai_pb2_grpc.add_AiServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    logger.info("AI gRPC server starting on port %d", port)
    server.start()
    return server


if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings.development")
    django.setup()
    logging.basicConfig(level=logging.INFO)
    s = serve()
    logger.info("AI gRPC server started, waiting for termination...")
    s.wait_for_termination()
