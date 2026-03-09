from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response

from apps.authentication.models import User
from apps.ideas.authentication import MiddlewareAuthentication
from apps.ideas.models import Idea

from .models import CollaborationInvitation


@api_view(["GET"])
@authentication_classes([MiddlewareAuthentication])
def invitations_list(request: Request) -> Response:
    """GET /api/invitations — List pending invitations for current user."""
    user = request.user
    if user is None or not getattr(user, "id", None):
        return Response(
            {"error": "UNAUTHORIZED", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

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
