"""Helper to create system event entries in the comments timeline.

Call these functions from other apps (collaboration, review, ideas)
when significant events occur on an idea.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import IdeaComment

logger = logging.getLogger(__name__)

# Event types
STATE_CHANGED = "state_changed"
COLLABORATOR_JOINED = "collaborator_joined"
COLLABORATOR_LEFT = "collaborator_left"
COLLABORATOR_REMOVED = "collaborator_removed"
OWNER_CHANGED = "owner_changed"


def _broadcast_ws_event(group_name: str, event_type: str, payload: dict) -> None:
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {"type": event_type, "payload": payload},
            )
    except Exception:
        logger.exception("Failed to broadcast WS event %s to %s", event_type, group_name)


def create_system_event(
    idea_id: str,
    event_type: str,
    content: str,
) -> IdeaComment:
    """Create a system event comment and broadcast via WebSocket."""
    comment = IdeaComment.objects.create(
        idea_id=idea_id,
        author_id=None,
        content=content,
        is_system_event=True,
        system_event_type=event_type,
    )

    data = {
        "id": str(comment.id),
        "idea_id": str(comment.idea_id),
        "author": None,
        "parent_id": None,
        "content": comment.content,
        "is_system_event": True,
        "system_event_type": event_type,
        "reactions": [],
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
        "is_edited": False,
        "deleted_at": None,
    }

    _broadcast_ws_event(f"idea_{idea_id}", "comment_created", data)

    return comment


def on_state_changed(idea_id: str, old_state: str, new_state: str) -> None:
    state_labels = {
        "open": "Open",
        "in_review": "In Review",
        "accepted": "Accepted",
        "dropped": "Dropped",
        "rejected": "Rejected",
    }
    old_label = state_labels.get(old_state, old_state)
    new_label = state_labels.get(new_state, new_state)
    create_system_event(
        idea_id,
        STATE_CHANGED,
        f"Idea state changed from **{old_label}** to **{new_label}**",
    )


def on_collaborator_joined(idea_id: str, display_name: str) -> None:
    create_system_event(
        idea_id,
        COLLABORATOR_JOINED,
        f"**{display_name}** joined as a collaborator",
    )


def on_collaborator_left(idea_id: str, display_name: str) -> None:
    create_system_event(
        idea_id,
        COLLABORATOR_LEFT,
        f"**{display_name}** left the idea",
    )


def on_collaborator_removed(idea_id: str, display_name: str) -> None:
    create_system_event(
        idea_id,
        COLLABORATOR_REMOVED,
        f"**{display_name}** was removed from the idea",
    )


def on_owner_changed(idea_id: str, old_owner_name: str, new_owner_name: str) -> None:
    create_system_event(
        idea_id,
        OWNER_CHANGED,
        f"Ownership transferred from **{old_owner_name}** to **{new_owner_name}**",
    )
