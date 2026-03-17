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
from apps.projects.authentication import MiddlewareAuthentication
from apps.projects.models import Project, ProjectCollaborator

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

    project_ids = {inv.project_id for inv in invitations}
    inviter_ids = {inv.inviter_id for inv in invitations}

    projects_map = {project.id: project for project in Project.objects.filter(id__in=project_ids)}
    inviters_map = {u.id: u for u in User.objects.filter(id__in=inviter_ids)}

    results = []
    for inv in invitations:
        project = projects_map.get(inv.project_id)
        inviter = inviters_map.get(inv.inviter_id)
        results.append(
            {
                "id": str(inv.id),
                "project_id": str(inv.project_id),
                "project_title": project.title if project else "",
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
def send_invitation(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/collaborators/invite — Send collaboration invitation."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the project owner can send invitations"},
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
        ProjectCollaborator.objects.filter(
            project_id=project_uuid, user_id__in=invitee_uuids
        ).values_list("user_id", flat=True)
    )
    existing_pending = set(
        CollaborationInvitation.objects.filter(
            project_id=project_uuid, invitee_id__in=invitee_uuids, status="pending"
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
            results.append({
                "invitee_id": str(invitee_uuid),
                "status": "error",
                "message": "Pending invitation already exists",
            })
            continue

        invitation = CollaborationInvitation.objects.create(
            project_id=project_uuid,
            inviter_id=user.id,
            invitee_id=invitee_uuid,
            status="pending",
        )

        notif_kwargs = dict(
            event_type="collaboration_invitation",
            title="Collaboration Invitation",
            body=f"{user.display_name} invited you to collaborate on \"{project.title}\"",
            reference_id=str(project_uuid),
            reference_type="project",
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

        ProjectCollaborator.objects.get_or_create(
            project_id=invitation.project_id,
            user_id=user.id,
            defaults={"joined_at": timezone.now()},
        )

        collaborator_count = ProjectCollaborator.objects.filter(
            project_id=invitation.project_id
        ).count()
        if collaborator_count == 1:
            Project.objects.filter(id=invitation.project_id, visibility="private").update(
                visibility="collaborating"
            )

    # Fetch project title for notification body
    try:
        project = Project.objects.get(id=invitation.project_id)
        project_title = project.title or "Untitled Project"
    except Project.DoesNotExist:
        project_title = "a project"

    # System event for comment timeline
    try:
        from apps.comments.system_events import on_collaborator_joined
        on_collaborator_joined(str(invitation.project_id), user.display_name)
    except Exception:
        logger.exception("Failed to create collaborator_joined system event")

    # Notify inviter that invitation was accepted
    accepted_kwargs = dict(
        event_type="collaborator_joined",
        title="Invitation Accepted",
        body=f"{user.display_name} accepted your invitation to \"{project_title}\"",
        reference_id=str(invitation.project_id),
        reference_type="project",
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
        reference_id=str(invitation.project_id),
        reference_type="project",
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
def list_collaborators(request: Request, project_id: str) -> Response:
    """GET /api/projects/:id/collaborators — List owner, co-owner, and collaborators."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Batch-load all relevant users
    user_ids = {project.owner_id}

    collab_entries = ProjectCollaborator.objects.filter(project_id=project_uuid)
    for c in collab_entries:
        user_ids.add(c.user_id)

    users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

    def _user_dict(u):
        return {
            "id": str(u.id),
            "display_name": u.display_name,
            "email": u.email,
        }

    owner_user = users_map.get(project.owner_id)
    owner_data = _user_dict(owner_user) if owner_user else {"id": str(project.owner_id)}

    collaborators_data = []
    for c in collab_entries:
        u = users_map.get(c.user_id)
        entry = _user_dict(u) if u else {"id": str(c.user_id)}
        entry["joined_at"] = c.joined_at.isoformat()
        collaborators_data.append(entry)

    return Response({
        "owner": owner_data,
        "collaborators": collaborators_data,
    })


@api_view(["DELETE"])
@authentication_classes([MiddlewareAuthentication])
def remove_collaborator(request: Request, project_id: str, user_id_param: str) -> Response:
    """DELETE /api/projects/:id/collaborators/:userId — Remove collaborator (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
        target_uuid = uuid.UUID(user_id_param)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the project owner can remove collaborators"},
            status=status.HTTP_403_FORBIDDEN,
        )

    deleted_count, _ = ProjectCollaborator.objects.filter(
        project_id=project_uuid, user_id=target_uuid
    ).delete()

    if deleted_count == 0:
        return Response(
            {"error": "NOT_FOUND", "message": "Collaborator not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # System event for comment timeline
    try:
        target_user = User.objects.filter(id=target_uuid).first()
        from apps.comments.system_events import on_collaborator_removed
        on_collaborator_removed(str(project_uuid), target_user.display_name if target_user else str(target_uuid))
    except Exception:
        logger.exception("Failed to create collaborator_removed system event")

    # Notify removed collaborator
    removed_kwargs = dict(
        event_type="removed_from_project",
        title="Removed from Project",
        body=f"You were removed from \"{project.title}\" by {user.display_name}",
        reference_id=str(project_uuid),
        reference_type="project",
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
def transfer_ownership(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/transfer-ownership — Transfer ownership to a collaborator."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the project owner can transfer ownership"},
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
    if not ProjectCollaborator.objects.filter(project_id=project_uuid, user_id=new_owner_uuid).exists():
        return Response(
            {"error": "BAD_REQUEST", "message": "Target user is not a collaborator"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        # Remove new owner from collaborators table
        ProjectCollaborator.objects.filter(project_id=project_uuid, user_id=new_owner_uuid).delete()

        # Add previous owner as collaborator
        ProjectCollaborator.objects.get_or_create(
            project_id=project_uuid,
            user_id=user.id,
            defaults={"joined_at": timezone.now()},
        )

        # Transfer ownership
        project.owner_id = new_owner_uuid
        project.save(update_fields=["owner_id"])

    # System event for comment timeline
    try:
        new_owner_user = User.objects.filter(id=new_owner_uuid).first()
        from apps.comments.system_events import on_owner_changed
        on_owner_changed(
            str(project_uuid),
            user.display_name,
            new_owner_user.display_name if new_owner_user else str(new_owner_uuid),
        )
    except Exception:
        logger.exception("Failed to create owner_changed system event")

    # Notify new owner of ownership transfer
    transfer_kwargs = dict(
        event_type="ownership_transferred",
        title="Ownership Transferred",
        body=f"{user.display_name} transferred ownership of \"{project.title}\" to you",
        reference_id=str(project_uuid),
        reference_type="project",
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
def leave_project(request: Request, project_id: str) -> Response:
    """POST /api/projects/:id/leave — Leave project (collaborator or co-owner)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Owner cannot leave their own project
    if project.owner_id == user.id:
        return Response(
            {"error": "BAD_REQUEST", "message": "Owner cannot leave without transferring ownership"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Regular collaborator leaves
    deleted_count, _ = ProjectCollaborator.objects.filter(
        project_id=project_uuid, user_id=user.id
    ).delete()

    if deleted_count == 0:
        return Response(
            {"error": "BAD_REQUEST", "message": "You are not a collaborator on this project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # System event for comment timeline
    try:
        from apps.comments.system_events import on_collaborator_left
        on_collaborator_left(str(project_uuid), user.display_name)
    except Exception:
        logger.exception("Failed to create collaborator_left system event")

    # Notify owner
    left_kwargs = dict(
        event_type="collaborator_left",
        title="Collaborator Left",
        body=f"{user.display_name} left \"{project.title}\"",
        reference_id=str(project_uuid),
        reference_type="project",
    )
    _publish_notification(
        routing_key="notification.collaboration.left",
        user_id=str(project.owner_id),
        **left_kwargs,
    )
    _broadcast_user_notification(str(project.owner_id), **left_kwargs)

    return Response({"message": "You have left the project"})


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def project_pending_invitations(request: Request, project_id: str) -> Response:
    """GET /api/projects/:id/invitations — List pending invitations for a project (owner only)."""
    user = _require_auth(request)
    if user is None:
        return _unauthorized_response()

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        project = Project.objects.get(id=project_uuid)
    except Project.DoesNotExist:
        return Response(
            {"error": "NOT_FOUND", "message": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.owner_id != user.id:
        return Response(
            {"error": "FORBIDDEN", "message": "Only the project owner can view pending invitations"},
            status=status.HTTP_403_FORBIDDEN,
        )

    invitations = CollaborationInvitation.objects.filter(
        project_id=project_uuid,
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
