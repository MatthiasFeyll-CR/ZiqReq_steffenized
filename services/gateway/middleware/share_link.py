"""Share link token validation middleware.

Validates ?token= query parameter for read-only share link access.
If valid, adds 'share_link_viewer' role to the user object.
If invalid, returns 403.
"""

from django.http import JsonResponse

from apps.projects.models import Project


class ShareLinkMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.GET.get("token")
        if not token:
            return self.get_response(request)

        # Only apply to project workspace paths
        path = request.path.rstrip("/")
        if not path.startswith("/api/projects/"):
            return self.get_response(request)

        # Validate token against database
        project = Project.objects.filter(share_link_token=token).first()
        if project is None:
            return JsonResponse(
                {"error": "FORBIDDEN", "message": "Invalid share link token"},
                status=403,
            )

        # Add share_link_viewer role to user object (or create anonymous-like access)
        user = getattr(request, "user_obj", None)
        if user is not None and hasattr(user, "roles"):
            if "share_link_viewer" not in user.roles:
                user.roles = [*user.roles, "share_link_viewer"]
        else:
            # For unauthenticated users viewing via share link,
            # attach the project reference so downstream can check
            request.share_link_project = project  # type: ignore[attr-defined]
            request.share_link_viewer = True  # type: ignore[attr-defined]

        return self.get_response(request)
