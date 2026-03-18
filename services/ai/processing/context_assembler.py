"""Context window assembly from gRPC data.

Assembles the context dict that the Facilitator agent needs:
  - project metadata (title, state, title_manually_edited, project_type)
  - recent messages (last N from admin param)
  - chat summary (from chat_context_summaries if exists)
  - facilitator bucket content (global + type-specific combined)
  - requirements structure (hierarchical JSON from requirements draft)
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_bucket_model():
    """Import FacilitatorContextBucket from whichever app is available."""
    try:
        from apps.context.models import FacilitatorContextBucket
        return FacilitatorContextBucket
    except ImportError:
        from apps.admin_ai_context.models import FacilitatorContextBucket
        return FacilitatorContextBucket


def get_facilitator_context(project_type: str) -> str:
    """Combine global + type-specific facilitator context buckets.

    Args:
        project_type: 'software' or 'non_software'.

    Returns:
        Combined context string with XML-tagged sections.
        Returns empty string if DB is unavailable.
    """
    try:
        FacilitatorContextBucket = _get_bucket_model()
    except Exception:
        logger.debug("Could not load FacilitatorContextBucket model — skipping")
        return ""

    global_content = ""
    type_content = ""

    try:
        global_bucket = FacilitatorContextBucket.objects.get(context_type="global")
        global_content = global_bucket.content or ""
    except FacilitatorContextBucket.DoesNotExist:
        logger.warning("Global facilitator context bucket not found")
    except Exception:
        logger.debug("Could not query global facilitator bucket")

    try:
        type_bucket = FacilitatorContextBucket.objects.get(context_type=project_type)
        type_content = type_bucket.content or ""
    except FacilitatorContextBucket.DoesNotExist:
        logger.warning("Facilitator context bucket for type '%s' not found", project_type)
    except Exception:
        logger.debug("Could not query %s facilitator bucket", project_type)

    parts = []
    if global_content.strip():
        parts.append(f"<global_guidance>\n{global_content}\n</global_guidance>")
    if type_content.strip():
        parts.append(f"<type_specific_guidance>\n{type_content}\n</type_specific_guidance>")

    return "\n\n".join(parts)


class ContextAssembler:
    """Build the input_data dict for FacilitatorAgent.process() from raw gRPC response."""

    def assemble(self, project_id: str, project_context_response: dict[str, Any]) -> dict[str, Any]:
        """Assemble context from GetProjectContext gRPC response.

        Args:
            project_id: The project UUID string.
            project_context_response: Raw dict from CoreClient.get_project_context().

        Returns:
            Dict ready to pass to FacilitatorAgent.process().
        """
        project = project_context_response.get("project", {})
        recent_messages = project_context_response.get("recent_messages", [])
        chat_summary = project_context_response.get("chat_summary")
        project_type = project.get("project_type", "software")

        # Combine global + type-specific facilitator context
        facilitator_bucket = get_facilitator_context(project_type)
        if not facilitator_bucket:
            # Fall back to raw gRPC response content if no buckets found
            facilitator_bucket = project_context_response.get("facilitator_bucket_content", "")

        # Parse requirements structure from gRPC response
        requirements_structure = _parse_requirements_structure(
            project_context_response.get("requirements_state", {})
        )

        # Load project attachments with completed extraction
        attachments = _load_project_attachments(project_id)

        assembled = {
            "project_id": project_id,
            "project_context": {
                "title": project.get("title", ""),
                "state": project.get("state", "open"),
                "title_manually_edited": project.get("title_manually_edited", False),
                "project_type": project_type,
            },
            "recent_messages": recent_messages,
            "chat_summary": chat_summary,
            "facilitator_bucket_content": facilitator_bucket,
            "requirements_structure": requirements_structure,
            "attachments": attachments,
            "delegation_results": None,
            "extension_results": None,
        }

        logger.info(
            "Assembled context for project %s: %d messages, %d attachments, summary=%s, type=%s",
            project_id,
            len(recent_messages),
            len(attachments),
            "yes" if chat_summary else "no",
            project_type,
        )
        return assembled


def _load_project_attachments(project_id: str) -> list[dict[str, Any]]:
    """Load active attachments with completed extraction for a project.

    Returns:
        List of attachment dicts with id, filename, content_type, extracted_content, message_id.
    """
    try:
        from grpc_clients.core_client import CoreClient
        client = CoreClient()
        return client.get_project_attachments(project_id)
    except Exception:
        logger.warning("Failed to load attachments for project %s", project_id)
        return []


def _parse_requirements_structure(requirements_state: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse requirements structure from CoreClient requirements state response.

    Args:
        requirements_state: Dict from CoreClient.get_requirements_state() with
            'structure' key (already-parsed list) or 'structure_json' (JSON string).

    Returns:
        Parsed list of structure items, or empty list.
    """
    # CoreClient.get_requirements_state() returns "structure" as a parsed list
    structure = requirements_state.get("structure")
    if isinstance(structure, list):
        return structure

    # Fallback: support JSON string under "structure_json" key
    structure_json = requirements_state.get("structure_json", "")
    if not structure_json:
        return []
    try:
        parsed = json.loads(structure_json)
        if isinstance(parsed, list):
            return parsed
        logger.warning("requirements structure_json is not a list, ignoring")
        return []
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse requirements structure_json")
        return []
