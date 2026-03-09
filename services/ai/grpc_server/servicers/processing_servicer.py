import uuid


class AiProcessingServicer:
    """gRPC servicer stub for AI processing methods.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def TriggerChatProcessing(self, request, context):  # type: ignore[no-untyped-def]
        return {"status": "accepted", "processing_id": str(uuid.uuid4())}

    def TriggerBrdGeneration(self, request, context):  # type: ignore[no-untyped-def]
        return {"status": "accepted", "generation_id": str(uuid.uuid4())}

    def TriggerContextReindex(self, request, context):  # type: ignore[no-untyped-def]
        return {"status": "accepted", "chunk_count": 0}

    def GetAiMetrics(self, request, context):  # type: ignore[no-untyped-def]
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
