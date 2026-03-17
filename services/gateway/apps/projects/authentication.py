from rest_framework.authentication import BaseAuthentication


class MiddlewareAuthentication(BaseAuthentication):
    """Bridges Django middleware auth (request.user_obj) to DRF request.user."""

    def authenticate(self, request):
        user = getattr(request, "user_obj", None)
        if user is None:
            return None
        return (user, None)
