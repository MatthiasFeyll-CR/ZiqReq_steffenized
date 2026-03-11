"""Embed idea content for similarity detection.

Generates a single vector(1536) embedding from idea title + chat summary + board content,
then persists it to the idea_embeddings table via CoreClient gRPC.
"""

from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


class IdeaEmbedder:
    """Generates and persists idea embeddings for similarity detection."""

    async def generate(
        self,
        idea_id: str,
        title: str,
        chat_summary: str,
        board_content: str,
    ) -> None:
        """Generate and persist idea embedding from combined content.

        Concatenates title, chat_summary, and board_content into source text,
        generates embedding via Azure OpenAI, and persists to idea_embeddings.

        Args:
            idea_id: The idea to generate embedding for.
            title: Idea title.
            chat_summary: Summary of chat content.
            board_content: Summary of board content.
        """
        source_text = f"{title}\n{chat_summary}\n{board_content}".strip()
        if not source_text:
            logger.info("[idea_embedder] No content to embed for idea %s", idea_id)
            return

        source_text_hash = hashlib.sha256(source_text.encode()).hexdigest()

        try:
            from embedding.embedder import Embedder

            embedder = Embedder()
            embeddings = await embedder._call_embedding_api([source_text])

            if not embeddings:
                logger.warning("[idea_embedder] No embedding returned for idea %s", idea_id)
                return

            embedding = embeddings[0]

            from grpc_clients.core_client import CoreClient

            client = CoreClient()
            client.upsert_idea_embedding(
                idea_id=idea_id,
                embedding=embedding,
                source_text_hash=source_text_hash,
            )

            logger.info(
                "[idea_embedder] Generated embedding for idea %s (hash=%s)",
                idea_id,
                source_text_hash[:12],
            )

        except Exception:
            logger.exception(
                "[idea_embedder] Failed to generate embedding for idea %s",
                idea_id,
            )
