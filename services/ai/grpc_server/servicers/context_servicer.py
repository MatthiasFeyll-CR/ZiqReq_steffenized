class AiContextServicer:
    """gRPC servicer stub for AI context bucket management.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def GetFacilitatorBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def UpdateFacilitatorBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {"id": "", "content": "", "updated_by_id": "", "updated_at": ""}

    def GetContextAgentBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {
            "id": "",
            "sections_json": "{}",
            "free_text": "",
            "updated_by_id": "",
            "updated_at": "",
        }

    def UpdateContextAgentBucket(self, request, context):  # type: ignore[no-untyped-def]
        return {
            "id": "",
            "sections_json": "{}",
            "free_text": "",
            "updated_by_id": "",
            "updated_at": "",
        }
