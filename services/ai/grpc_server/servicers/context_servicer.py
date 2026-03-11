import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class AiContextServicer:
    """gRPC servicer for AI context bucket management.

    UpdateContextAgentBucket triggers the embedding pipeline (chunk → embed → persist).
    Other methods return valid placeholder responses.
    """

    def GetFacilitatorBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def UpdateFacilitatorBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def GetContextAgentBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {
            "id": "",
            "sections_json": "{}",
            "free_text": "",
            "updated_by_id": "",
            "updated_at": "",
        }

    def UpdateContextAgentBucket(self, request, context):  # type: ignore[no-untyped-def]
        """Update context agent bucket and trigger re-indexing.

        Accepts sections (jsonb) and free_text, persists to DB,
        then runs the embedding pipeline (chunk → embed → persist).

        Returns {chunk_count, total_tokens, duration_ms}.
        """
        from apps.context.models import ContextAgentBucket
        from embedding.reindexer import Reindexer

        sections_raw = getattr(request, "sections_json", "{}")
        free_text = getattr(request, "free_text", "")

        if isinstance(sections_raw, str):
            try:
                sections = json.loads(sections_raw)
            except json.JSONDecodeError:
                sections = {}
        else:
            sections = sections_raw or {}

        bucket = ContextAgentBucket.objects.first()
        if bucket is None:
            bucket = ContextAgentBucket.objects.create(
                sections=sections,
                free_text=free_text,
            )
        else:
            bucket.sections = sections
            bucket.free_text = free_text
            bucket.save()

        bucket_id = str(bucket.id)

        reindexer = Reindexer()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(
                        asyncio.run,
                        reindexer.reindex(bucket_id, sections, free_text),
                    ).result()
            else:
                result = asyncio.run(
                    reindexer.reindex(bucket_id, sections, free_text)
                )
        except Exception:
            logger.exception(
                "Embedding pipeline failed for bucket %s", bucket_id
            )
            raise

        logger.info(
            "UpdateContextAgentBucket complete: bucket=%s, chunks=%d, tokens=%d, duration=%dms",
            bucket_id,
            result["chunk_count"],
            result["total_tokens"],
            result["duration_ms"],
        )

        return {
            "chunk_count": result["chunk_count"],
            "total_tokens": result["total_tokens"],
            "duration_ms": result["duration_ms"],
        }
