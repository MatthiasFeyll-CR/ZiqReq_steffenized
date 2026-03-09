from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def validate_token(request):
    return Response({"status": "ok"})
