import asyncio
import logging
import threading
import uuid

logger = logging.getLogger(__name__)

# Single persistent event loop running in a dedicated daemon thread.
# All async pipeline work is submitted here so httpx/OpenAI SDK clients
# are never orphaned by a closed loop.
_pipeline_loop: asyncio.AbstractEventLoop | None = None
_pipeline_loop_lock = threading.Lock()


def _get_pipeline_loop() -> asyncio.AbstractEventLoop:
    """Return (and lazily start) the shared pipeline event loop."""
    global _pipeline_loop
    if _pipeline_loop is not None and _pipeline_loop.is_running():
        return _pipeline_loop

    with _pipeline_loop_lock:
        if _pipeline_loop is not None and _pipeline_loop.is_running():
            return _pipeline_loop

        loop = asyncio.new_event_loop()
        thread = threading.Thread(
            target=loop.run_forever,
            daemon=True,
            name="pipeline-event-loop",
        )
        thread.start()
        _pipeline_loop = loop
        return loop


class AiProcessingServicer:
    """gRPC servicer for AI processing methods."""

    def TriggerChatProcessing(self, request, context):  # type: ignore[no-untyped-def]
        idea_id = self._get_field(request, "idea_id")
        message_id = self._get_field(request, "message_id")
        processing_id = str(uuid.uuid4())

        logger.info(
            "TriggerChatProcessing: idea_id=%s, message_id=%s, processing_id=%s",
            idea_id, message_id, processing_id,
        )

        loop = _get_pipeline_loop()
        asyncio.run_coroutine_threadsafe(
            self._run_chat_pipeline(idea_id), loop,
        )

        return {"status": "accepted", "processing_id": processing_id}

    async def _run_chat_pipeline(self, idea_id: str) -> None:
        """Run the chat processing pipeline."""
        try:
            from processing.pipeline import ChatProcessingPipeline

            pipeline = ChatProcessingPipeline()
            result = await pipeline.execute(idea_id)
            logger.info(
                "Chat pipeline completed for idea %s: status=%s",
                idea_id, result.get("status"),
            )
        except Exception:
            logger.exception("Chat pipeline failed for idea %s", idea_id)

    def _get_field(self, request, name: str, default: str = "") -> str:  # type: ignore[no-untyped-def]
        if isinstance(request, dict):
            return request.get(name, default)
        return getattr(request, name, default)

    def TriggerBrdGeneration(self, request, context):  # type: ignore[no-untyped-def]
        idea_id = self._get_field(request, "idea_id")
        mode = self._get_field(request, "mode", "full_generation")
        section_name = self._get_field(request, "section_name")

        generation_id = str(uuid.uuid4())

        loop = _get_pipeline_loop()
        asyncio.run_coroutine_threadsafe(
            self._run_brd_pipeline(idea_id, mode, section_name), loop,
        )

        return {"status": "accepted", "generation_id": generation_id}

    async def _run_brd_pipeline(self, idea_id: str, mode: str, section_name: str) -> None:
        """Run BRD pipeline."""
        try:
            from processing.brd_pipeline import BrdGenerationPipeline
            from events.publishers import publish_event

            pipeline = BrdGenerationPipeline()
            result = await pipeline.execute(
                idea_id=idea_id,
                mode=mode,
                section_name=section_name or None,
            )

            if result.get("status") == "completed":
                await publish_event("ai.brd.ready", {
                    "idea_id": idea_id,
                    "mode": mode,
                    "sections": result.get("sections", {}),
                    "readiness_evaluation": result.get("readiness_evaluation", {}),
                    "fabrication_flags": result.get("fabrication_flags", []),
                })
                logger.info("ai.brd.ready event published for idea %s", idea_id)
            else:
                logger.warning(
                    "BRD pipeline did not complete for idea %s: status=%s",
                    idea_id, result.get("status"),
                )
        except Exception:
            logger.exception("BRD pipeline failed for idea %s", idea_id)

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
