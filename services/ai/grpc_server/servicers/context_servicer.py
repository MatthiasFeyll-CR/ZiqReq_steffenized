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
        from apps.context.models import FacilitatorContextBucket

        bucket = FacilitatorContextBucket.objects.first()
        if bucket is None:
            return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

        return {
            "id": str(bucket.id),
            "content": bucket.content or "",
            "updated_by_id": str(bucket.updated_by) if bucket.updated_by else "",
            "updated_at": bucket.updated_at.isoformat() if bucket.updated_at else "",
        }

    def UpdateFacilitatorBucket(self, request, context):  # type: ignore[no-untyped-def]
        from apps.context.models import FacilitatorContextBucket

        content = getattr(request, "content", "")
        updated_by_id = getattr(request, "updated_by_id", "")

        bucket = FacilitatorContextBucket.objects.first()
        if bucket is None:
            bucket = FacilitatorContextBucket.objects.create(
                content=content,
                updated_by=updated_by_id or None,
            )
        else:
            bucket.content = content
            if updated_by_id:
                bucket.updated_by = updated_by_id
            bucket.save()

        logger.info("UpdateFacilitatorBucket complete: bucket=%s", bucket.id)

        return {
            "id": str(bucket.id),
            "content": bucket.content or "",
            "updated_by_id": str(bucket.updated_by) if bucket.updated_by else "",
            "updated_at": bucket.updated_at.isoformat() if bucket.updated_at else "",
        }

    def GetContextAgentBucket(self, request, context):  # type: ignore[no-untyped-def]
        from apps.context.models import ContextAgentBucket

        bucket = ContextAgentBucket.objects.first()
        if bucket is None:
            return {
                "id": "",
                "sections_json": "{}",
                "free_text": "",
                "updated_by_id": "",
                "updated_at": "",
            }

        return {
            "id": str(bucket.id),
            "sections_json": json.dumps(bucket.sections) if bucket.sections else "{}",
            "free_text": bucket.free_text or "",
            "updated_by_id": str(bucket.updated_by) if bucket.updated_by else "",
            "updated_at": bucket.updated_at.isoformat() if bucket.updated_at else "",
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
