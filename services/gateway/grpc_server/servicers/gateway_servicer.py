import uuid


class GatewayServicer:
    """gRPC servicer stub for the Gateway service.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def CreateNotification(self, request, context):  # type: ignore[no-untyped-def]
        return {"notification_id": str(uuid.uuid4())}

    def GetUserPreferences(self, request, context):  # type: ignore[no-untyped-def]
        return {
            "user_id": "",
            "email": "",
            "display_name": "",
            "email_notification_preferences": {},
        }

    def GetAlertRecipients(self, request, context):  # type: ignore[no-untyped-def]
        return {"recipients": []}
