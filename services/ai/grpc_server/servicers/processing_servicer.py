import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


class AiProcessingServicer:
    """gRPC servicer stub for AI processing methods.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def TriggerChatProcessing(self, request, context):  # type: ignore[no-untyped-def]
        return {"status": "accepted", "processing_id": str(uuid.uuid4())}

    def _get_field(self, request, name: str, default: str = "") -> str:  # type: ignore[no-untyped-def]
        if isinstance(request, dict):
            return request.get(name, default)
        return getattr(request, name, default)

    def TriggerBrdGeneration(self, request, context):  # type: ignore[no-untyped-def]
        idea_id = self._get_field(request, "idea_id")
        mode = self._get_field(request, "mode", "full_generation")
        section_name = self._get_field(request, "section_name")

        generation_id = str(uuid.uuid4())

        # Launch BRD generation pipeline asynchronously
        try:
            from processing.brd_pipeline import BrdGenerationPipeline

            pipeline = BrdGenerationPipeline()
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(
                    self._run_brd_pipeline(pipeline, idea_id, mode, section_name)
                )
            else:
                loop.run_until_complete(
                    self._run_brd_pipeline(pipeline, idea_id, mode, section_name)
                )
        except Exception:
            logger.exception("Failed to launch BRD generation pipeline for idea %s", idea_id)

        return {"status": "accepted", "generation_id": generation_id}

    async def _run_brd_pipeline(
        self, pipeline, idea_id: str, mode: str, section_name: str  # type: ignore[no-untyped-def]
    ) -> None:
        """Run BRD pipeline and publish ai.brd.ready event on completion."""
        try:
            result = await pipeline.execute(
                idea_id=idea_id,
                mode=mode,
                section_name=section_name or None,
            )

            if result.get("status") == "completed":
                from events.publishers import publish_event

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
                    "BRD pipeline did not complete successfully for idea %s: status=%s",
                    idea_id, result.get("status"),
                )
        except Exception:
            logger.exception("BRD pipeline execution failed for idea %s", idea_id)

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
