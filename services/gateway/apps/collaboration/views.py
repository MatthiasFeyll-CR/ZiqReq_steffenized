import logging
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User
from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea, IdeaCollaborator

from .models import CollaborationInvitation

logger = logging.getLogger(__name__)


def _publish_notification(**kwargs) -> None:
    """Lazy-import wrapper to avoid module-collection ordering issues in tests."""
    from events.publisher import publish_notification_event

    publish_notification_event(**kwargs)


def _broadcast_user_notification(
    user_id: str,
    *,
    event_type: str,
    title: str,
    body: str,
    reference_id: str = "",
    reference_type: str = "",
) -> None:
    """Push a notification directly to a user's WebSocket via their user group."""
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f"user_{user_id}"
        payload = {
            "event_type": event_type,
            "title": title,
            "body": body,
            "reference_id": reference_id,
            "reference_type": reference_type,
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification",
                "payload": payload,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast notification to user %s", user_id)


def _require_auth(request: Request):
    user = request.user
    if user is None or not getattr(user, "id", None):
        return None
    return user


def _unauthorized_response() -> Response:
    return Response(
        {"error": "UNAUTHORIZED", "message": "Authentication required"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def invitations_list(request: Request) -> Response:
    """GET /api/invitations — List pending invitations for current user."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    invitations = CollaborationInvitation.objects.filter(
        invitee_id=user.id,
        status="pending",
    ).order_by("-created_at")

    idea_ids = {inv.idea_id for inv in invitations}
    inviter_ids = {inv.inviter_id for inv in invitations}

    ideas_map = {idea.id: idea for idea in Idea.objects.filter(id__in=idea_ids)}
    inviters_map = {u.id: u for u in User.objects.filter(id__in=inviter_ids)}

    results = []
    for inv in invitations:
        idea = ideas_map.get(inv.idea_id)
        inviter = inviters_map.get(inv.inviter_id)
        results.append(
            {
                "id": str(inv.id),
                "idea_id": str(inv.idea_id),
                "idea_title": idea.title if idea else "",
                "inviter": {
                    "id": str(inv.inviter_id),
                    "display_name": inviter.display_name if inviter else "",
                },
                "created_at": inv.created_at.isoformat(),
            }
        )

    return Response({"invitations": results})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def send_invitation(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/collaborators/invite — Send collaboration invitation."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the idea owner can send invitations"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Support both single invitee_id and bulk invitee_ids
    invitee_ids_raw = request.data.get("invitee_ids")
    single_id = request.data.get("invitee_id")

    if invitee_ids_raw and isinstance(invitee_ids_raw, list):
        raw_ids = invitee_ids_raw
    elif single_id:
        raw_ids = [single_id]
    else:
        return Response(
            {"error": "BAD_REQUEST", "message": "invitee_id or invitee_ids is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate and deduplicate
    invitee_uuids = []
    for raw in raw_ids:
        try:
            uid = uuid.UUID(str(raw))
        except ValueError:
            return Response(
                {"error": "BAD_REQUEST", "message": f"Invalid invitee_id: {raw}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uid == user.id:
            continue  # silently skip self
        if uid not in invitee_uuids:
            invitee_uuids.append(uid)

    if not invitee_uuids:
        return Response(
            {"error": "BAD_REQUEST", "message": "No valid invitees provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_users = set(
        User.objects.filter(id__in=invitee_uuids).values_list("id", flat=True)
    )
    existing_collaborators = set(
        IdeaCollaborator.objects.filter(
            idea_id=idea_uuid, user_id__in=invitee_uuids
        ).values_list("user_id", flat=True)
    )
    existing_pending = set(
        CollaborationInvitation.objects.filter(
            idea_id=idea_uuid, invitee_id__in=invitee_uuids, status="pending"
        ).values_list("invitee_id", flat=True)
    )

    results = []
    for invitee_uuid in invitee_uuids:
        if invitee_uuid not in existing_users:
            results.append({"invitee_id": str(invitee_uuid), "status": "error", "message": "User not found"})
            continue
        if invitee_uuid in existing_collaborators:
            results.append({"invitee_id": str(invitee_uuid), "status": "error", "message": "Already a collaborator"})
            continue
        if invitee_uuid in existing_pending:
            results.append({"invitee_id": str(invitee_uuid), "status": "error", "message": "Pending invitation already exists"})
            continue

        invitation = CollaborationInvitation.objects.create(
            idea_id=idea_uuid,
            inviter_id=user.id,
            invitee_id=invitee_uuid,
            status="pending",
        )

        notif_kwargs = dict(
            event_type="collaboration_invitation",
            title="Collaboration Invitation",
            body=f"{user.display_name} invited you to collaborate on \"{idea.title}\"",
            reference_id=str(idea_uuid),
            reference_type="idea",
        )
        _publish_notification(
            routing_key="notification.collaboration.invitation",
            user_id=str(invitee_uuid),
            **notif_kwargs,
        )
        _broadcast_user_notification(str(invitee_uuid), **notif_kwargs)

        results.append({"invitee_id": str(invitee_uuid), "invitation_id": str(invitation.id), "status": "pending"})

    # Backward-compatible: single invite returns flat object
    if single_id and not invitee_ids_raw:
        if results and results[0].get("invitation_id"):
            return Response(
                {"invitation_id": results[0]["invitation_id"], "status": "pending"},
                status=status.HTTP_201_CREATED,
            )
        elif results:
            return Response(
                {"error": "BAD_REQUEST", "message": results[0].get("message", "Failed to invite")},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {"results": results},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def accept_invitation(request: Request, invitation_id: str) -> Response:
    """POST /api/invitations/:id/accept — Accept collaboration invitation."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        inv_uuid = uuid.UUID(invitation_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        invitation = CollaborationInvitation.objects.get(id=inv_uuid)
    except CollaborationInvitation.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if invitation.invitee_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the invitee can accept this invitation"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if invitation.status != "pending":
        return Response(
            {"error": "BAD_REQUEST", "message": f"Invitation is already {invitation.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        invitation.status = "accepted"
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=["status", "responded_at"])

        IdeaCollaborator.objects.get_or_create(
            idea_id=invitation.idea_id,
            user_id=user.id,
            defaults={"joined_at": timezone.now()},
        )

        collaborator_count = IdeaCollaborator.objects.filter(
            idea_id=invitation.idea_id
        ).count()
        if collaborator_count == 1:
            Idea.objects.filter(id=invitation.idea_id, visibility="private").update(
                visibility="collaborating"
            )

    # Fetch idea title for notification body
    try:
        idea = Idea.objects.get(id=invitation.idea_id)
        idea_title = idea.title or "Untitled Idea"
    except Idea.DoesNotExist:
        idea_title = "an idea"

    # Notify inviter that invitation was accepted
    accepted_kwargs = dict(
        event_type="collaborator_joined",
        title="Invitation Accepted",
        body=f"{user.display_name} accepted your invitation to \"{idea_title}\"",
        reference_id=str(invitation.idea_id),
        reference_type="idea",
    )
    _publish_notification(
        routing_key="notification.collaboration.accepted",
        user_id=str(invitation.inviter_id),
        **accepted_kwargs,
    )
    _broadcast_user_notification(str(invitation.inviter_id), **accepted_kwargs)

    return Response({"message": "Invitation accepted"})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def decline_invitation(request: Request, invitation_id: str) -> Response:
    """POST /api/invitations/:id/decline — Decline collaboration invitation."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        inv_uuid = uuid.UUID(invitation_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        invitation = CollaborationInvitation.objects.get(id=inv_uuid)
    except CollaborationInvitation.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if invitation.invitee_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the invitee can decline this invitation"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if invitation.status != "pending":
        return Response(
            {"error": "BAD_REQUEST", "message": f"Invitation is already {invitation.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    invitation.status = "declined"
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at"])

    # Notify inviter that invitation was declined
    declined_kwargs = dict(
        event_type="collaborator_left",
        title="Invitation Declined",
        body=f"{user.display_name} declined your collaboration invitation",
        reference_id=str(invitation.idea_id),
        reference_type="idea",
    )
    _publish_notification(
        routing_key="notification.collaboration.declined",
        user_id=str(invitation.inviter_id),
        **declined_kwargs,
    )
    _broadcast_user_notification(str(invitation.inviter_id), **declined_kwargs)

    return Response({"message": "Invitation declined"})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def revoke_invitation(request: Request, invitation_id: str) -> Response:
    """POST /api/invitations/:id/revoke — Revoke pending invitation (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        inv_uuid = uuid.UUID(invitation_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        invitation = CollaborationInvitation.objects.get(id=inv_uuid)
    except CollaborationInvitation.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Invitation not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if invitation.inviter_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the inviter can revoke this invitation"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if invitation.status != "pending":
        return Response(
            {"error": "BAD_REQUEST", "message": f"Invitation is already {invitation.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    invitation.status = "revoked"
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at"])

    return Response({"message": "Invitation revoked"})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def list_collaborators(request: Request, idea_id: str) -> Response:
    """GET /api/ideas/:id/collaborators — List owner, co-owner, and collaborators."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Batch-load all relevant users
    user_ids = {idea.owner_id}
    if idea.co_owner_id:
        user_ids.add(idea.co_owner_id)

    collab_entries = IdeaCollaborator.objects.filter(idea_id=idea_uuid)
    for c in collab_entries:
        user_ids.add(c.user_id)

    users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    def _user_dict(u):
        return {
            "id": str(u.id),
            "display_name": u.display_name,
            "email": u.email,
        }

    owner_user = users_map.get(idea.owner_id)
    owner_data = _user_dict(owner_user) if owner_user else {"id": str(idea.owner_id)}

    co_owner_data = None
    if idea.co_owner_id:
        co_owner_user = users_map.get(idea.co_owner_id)
        co_owner_data = _user_dict(co_owner_user) if co_owner_user else {"id": str(idea.co_owner_id)}

    collaborators_data = []
    for c in collab_entries:
        u = users_map.get(c.user_id)
        entry = _user_dict(u) if u else {"id": str(c.user_id)}
        entry["joined_at"] = c.joined_at.isoformat()
        collaborators_data.append(entry)

    return Response({
        "owner": owner_data,
        "co_owner": co_owner_data,
        "collaborators": collaborators_data,
    })


@api_view(["DELETE"])
@authentication_classes([MiddlewareAuthentication])
def remove_collaborator(request: Request, idea_id: str, user_id_param: str) -> Response:
    """DELETE /api/ideas/:id/collaborators/:userId — Remove collaborator (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
        target_uuid = uuid.UUID(user_id_param)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the idea owner can remove collaborators"},
            status=status.HTTP_403_FORBIDDEN,
        )

    deleted_count, _ = IdeaCollaborator.objects.filter(
        idea_id=idea_uuid, user_id=target_uuid
    ).delete()

    if deleted_count == 0:
        return Response(
            {"error": "NOT_FOUND", "message": "Collaborator not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Notify removed collaborator
    removed_kwargs = dict(
        event_type="removed_from_idea",
        title="Removed from Idea",
        body=f"You were removed from \"{idea.title}\" by {user.display_name}",
        reference_id=str(idea_uuid),
        reference_type="idea",
    )
    _publish_notification(
        routing_key="notification.collaboration.removed",
        user_id=str(target_uuid),
        **removed_kwargs,
    )
    _broadcast_user_notification(str(target_uuid), **removed_kwargs)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def transfer_ownership(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/transfer-ownership — Transfer ownership to a collaborator."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the idea owner can transfer ownership"},
            status=status.HTTP_403_FORBIDDEN,
        )

    new_owner_id = request.data.get("new_owner_id")
    if not new_owner_id:
        return Response(
            {"error": "BAD_REQUEST", "message": "new_owner_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        new_owner_uuid = uuid.UUID(str(new_owner_id))
    except ValueError:
        return Response(
            {"error": "BAD_REQUEST", "message": "Invalid new_owner_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_owner_uuid == user.id:
        return Response(
            {"error": "BAD_REQUEST", "message": "Cannot transfer ownership to yourself"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # New owner must be an existing collaborator
    if not IdeaCollaborator.objects.filter(idea_id=idea_uuid, user_id=new_owner_uuid).exists():
        return Response(
            {"error": "BAD_REQUEST", "message": "Target user is not a collaborator"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        # Remove new owner from collaborators table
        IdeaCollaborator.objects.filter(idea_id=idea_uuid, user_id=new_owner_uuid).delete()

        # Add previous owner as collaborator
        IdeaCollaborator.objects.get_or_create(
            idea_id=idea_uuid,
            user_id=user.id,
            defaults={"joined_at": timezone.now()},
        )

        # Transfer ownership
        idea.owner_id = new_owner_uuid
        idea.save(update_fields=["owner_id"])

    # Notify new owner of ownership transfer
    transfer_kwargs = dict(
        event_type="ownership_transferred",
        title="Ownership Transferred",
        body=f"{user.display_name} transferred ownership of \"{idea.title}\" to you",
        reference_id=str(idea_uuid),
        reference_type="idea",
    )
    _publish_notification(
        routing_key="notification.collaboration.transfer",
        user_id=str(new_owner_uuid),
        **transfer_kwargs,
    )
    _broadcast_user_notification(str(new_owner_uuid), **transfer_kwargs)

    return Response({"message": "Ownership transferred"})


@api_view(["POST"])
@authentication_classes([MiddlewareAuthentication])
def leave_idea(request: Request, idea_id: str) -> Response:
    """POST /api/ideas/:id/leave — Leave idea (collaborator or co-owner)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Single owner cannot leave
    if idea.owner_id == user.id and idea.co_owner_id is None:
        return Response(
            {"error": "BAD_REQUEST", "message": "Single owner cannot leave without transferring ownership"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Co-owner leaves: set co_owner_id to NULL
    if idea.co_owner_id == user.id:
        idea.co_owner_id = None
        idea.save(update_fields=["co_owner_id"])
        # Notify owner
        left_kwargs = dict(
            event_type="collaborator_left",
            title="Collaborator Left",
            body=f"{user.display_name} left \"{idea.title}\"",
            reference_id=str(idea_uuid),
            reference_type="idea",
        )
        _publish_notification(
            routing_key="notification.collaboration.left",
            user_id=str(idea.owner_id),
            **left_kwargs,
        )
        _broadcast_user_notification(str(idea.owner_id), **left_kwargs)
        return Response({"message": "You have left the idea"})

    # Regular collaborator leaves
    deleted_count, _ = IdeaCollaborator.objects.filter(
        idea_id=idea_uuid, user_id=user.id
    ).delete()

    if deleted_count == 0:
        return Response(
            {"error": "BAD_REQUEST", "message": "You are not a collaborator on this idea"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Notify owner
    left_kwargs = dict(
        event_type="collaborator_left",
        title="Collaborator Left",
        body=f"{user.display_name} left \"{idea.title}\"",
        reference_id=str(idea_uuid),
        reference_type="idea",
    )
    _publish_notification(
        routing_key="notification.collaboration.left",
        user_id=str(idea.owner_id),
        **left_kwargs,
    )
    _broadcast_user_notification(str(idea.owner_id), **left_kwargs)

    return Response({"message": "You have left the idea"})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def idea_pending_invitations(request: Request, idea_id: str) -> Response:
    """GET /api/ideas/:id/invitations — List pending invitations for an idea (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        idea_uuid = uuid.UUID(idea_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        idea = Idea.objects.get(id=idea_uuid)
    except Idea.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Idea not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if idea.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the idea owner can view pending invitations"},
            status=status.HTTP_403_FORBIDDEN,
        )

    invitations = CollaborationInvitation.objects.filter(
        idea_id=idea_uuid,
        status="pending",
    ).order_by("-created_at")

    invitee_ids = {inv.invitee_id for inv in invitations}
    invitees_map = {u.id: u for u in User.objects.filter(id__in=invitee_ids)}

    results = []
    for inv in invitations:
        invitee = invitees_map.get(inv.invitee_id)
        results.append(
            {
                "id": str(inv.id),
                "invitee": {
                    "id": str(inv.invitee_id),
                    "display_name": invitee.display_name if invitee else "",
                    "email": invitee.email if invitee else "",
                },
                "created_at": inv.created_at.isoformat(),
            }
        )

    return Response({"invitations": results})
