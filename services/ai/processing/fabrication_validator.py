"""Fabrication validator — lightweight heuristic checks for BRD content.

Uses keyword extraction + fuzzy string matching to flag sections that
contain claims not traceable to the source material (chat messages and
board content). This is NOT AI-based — purely heuristic.

Flagged sections receive a 'fabrication_warning' flag but content is
still returned (the user decides whether to keep it).
"""

from __future__ import annotations

import logging
import re
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)

# Minimum fuzzy-match ratio to consider a keyword grounded in the source
_MATCH_THRESHOLD = 0.75

# Minimum keyword length to consider (skip short words like "the", "and")
_MIN_KEYWORD_LENGTH = 4

# Minimum flagged keyword ratio to trigger a fabrication warning
_FLAG_RATIO_THRESHOLD = 0.5


class FabricationValidator:
    """Validates BRD sections against source material for fabrication.

    Uses keyword extraction and fuzzy string matching to detect
    claims that are not traceable to chat messages or board content.
    """

    def validate(
        self,
        sections: dict[str, str | None],
        source_material: str,
    ) -> list[dict[str, Any]]:
        """Validate BRD sections against source material.

        Args:
            sections: Dict mapping section field names (e.g. 'section_title')
                to their content strings. None values are skipped.
            source_material: Combined text from chat messages and board content
                used as the ground truth for validation.

        Returns:
            List of fabrication flag dicts, each with:
                - section: section field name
                - ungrounded_keywords: list of keywords not found in source
                - keyword_count: total extracted keywords
                - match_ratio: ratio of grounded keywords
        """
        flags: list[dict[str, Any]] = []
        source_lower = source_material.lower()
        source_words = set(re.findall(r"\b\w+\b", source_lower))

        for section_name, content in sections.items():
            if content is None or not content.strip():
                continue
            # Skip sections that are "Not enough information." or /TODO
            if content.strip() == "Not enough information." or content.strip().startswith("/TODO"):
                continue

            keywords = _extract_keywords(content)
            if not keywords:
                continue

            ungrounded = []
            for kw in keywords:
                if not _is_grounded(kw, source_lower, source_words):
                    ungrounded.append(kw)

            grounded_count = len(keywords) - len(ungrounded)
            match_ratio = grounded_count / len(keywords) if keywords else 1.0

            if match_ratio < _FLAG_RATIO_THRESHOLD:
                flags.append({
                    "section": section_name,
                    "ungrounded_keywords": ungrounded,
                    "keyword_count": len(keywords),
                    "match_ratio": round(match_ratio, 2),
                })
                logger.warning(
                    "Fabrication flag: section=%s, match_ratio=%.2f, "
                    "ungrounded=%s",
                    section_name, match_ratio, ungrounded,
                )

        return flags


def _extract_keywords(text: str) -> list[str]:
    """Extract significant keywords from text.

    Extracts words that are at least _MIN_KEYWORD_LENGTH characters,
    filters out common stop words, and extracts proper nouns
    (capitalized words that aren't at sentence start).
    """
    words = re.findall(r"\b\w+\b", text)
    keywords: list[str] = []
    seen: set[str] = set()

    for word in words:
        lower = word.lower()
        if len(lower) < _MIN_KEYWORD_LENGTH:
            continue
        if lower in _STOP_WORDS:
            continue
        if lower not in seen:
            seen.add(lower)
            keywords.append(lower)

    # Extract proper nouns (capitalized words not at sentence starts)
    proper_nouns = _extract_proper_nouns(text)
    for pn in proper_nouns:
        lower = pn.lower()
        if lower not in seen:
            seen.add(lower)
            keywords.append(lower)

    return keywords


def _extract_proper_nouns(text: str) -> list[str]:
    """Extract potential proper nouns from text.

    Finds capitalized words that are not at the start of a sentence.
    """
    proper_nouns: list[str] = []
    sentences = re.split(r"[.!?]\s+", text)

    for sentence in sentences:
        words = sentence.split()
        # Skip first word of each sentence
        for word in words[1:]:
            cleaned = re.sub(r"[^\w]", "", word)
            if cleaned and cleaned[0].isupper() and len(cleaned) >= _MIN_KEYWORD_LENGTH:
                proper_nouns.append(cleaned)

    return proper_nouns


def _is_grounded(keyword: str, source_lower: str, source_words: set[str]) -> bool:
    """Check if a keyword is grounded in the source material.

    Uses exact word match first, then fuzzy matching as fallback.
    """
    # Exact match in source words
    if keyword in source_words:
        return True

    # Substring match in source text
    if keyword in source_lower:
        return True

    # Fuzzy match against source words
    for source_word in source_words:
        if len(source_word) < _MIN_KEYWORD_LENGTH:
            continue
        ratio = SequenceMatcher(None, keyword, source_word).ratio()
        if ratio >= _MATCH_THRESHOLD:
            return True

    return False


def build_source_material(
    chat_summary: str,
    recent_messages: list[dict[str, Any]],
    board_state: dict[str, Any],
) -> str:
    """Build a combined source material string from brainstorming data.

    Args:
        chat_summary: Summary of chat context.
        recent_messages: Last N chat messages.
        board_state: Board nodes and connections.

    Returns:
        Combined text string for validation.
    """
    parts: list[str] = []

    if chat_summary:
        parts.append(chat_summary)

    for msg in recent_messages:
        content = msg.get("content", "")
        if content:
            parts.append(content)

    nodes = board_state.get("nodes", [])
    for node in nodes:
        title = node.get("title", "")
        body = node.get("body", "")
        if title:
            parts.append(title)
        if body:
            parts.append(body)

    return " ".join(parts)


# Common English stop words to filter out during keyword extraction
_STOP_WORDS = frozenset({
    "about", "above", "after", "again", "against", "also", "been",
    "before", "being", "below", "between", "both", "could", "does",
    "doing", "down", "during", "each", "every", "from", "further",
    "have", "having", "here", "hers", "herself", "himself", "into",
    "itself", "just", "more", "most", "myself", "once", "only",
    "other", "ourselves", "over", "same", "shall", "should", "some",
    "such", "than", "that", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through",
    "under", "until", "very", "what", "when", "where", "which",
    "while", "whom", "will", "with", "would", "your", "yours",
    "yourself", "yourselves",
})
