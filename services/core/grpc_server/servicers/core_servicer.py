import uuid


class CoreServicer:
    """gRPC servicer stub for the Core service.

    All methods return valid placeholder responses.
    Full implementations will be added in later milestones.
    """

    def GetIdeaContext(self, request, context):  # type: ignore[no-untyped-def]
        return {
            "metadata": {
                "idea_id": "",
                "title": "",
                "title_manually_edited": False,
                "state": "open",
                "agent_mode": "interactive",
                "owner_display_name": "",
                "co_owner_display_name": "",
            },
            "recent_messages": [],
            "board": {"nodes": [], "connections": []},
            "brd_draft": None,
            "active_users": [],
        }

    def GetFullChatHistory(self, request, context):  # type: ignore[no-untyped-def]
        return {"messages": []}

    def PersistAiChatMessage(self, request, context):  # type: ignore[no-untyped-def]
        return {"message_id": str(uuid.uuid4()), "created_at": ""}

    def PersistAiReaction(self, request, context):  # type: ignore[no-untyped-def]
        return {"reaction_id": str(uuid.uuid4())}

    def UpdateIdeaTitle(self, request, context):  # type: ignore[no-untyped-def]
        return {"success": True}

    def PersistBoardMutations(self, request, context):  # type: ignore[no-untyped-def]
        return {"success": True, "mutations_applied": 0}

    def UpdateBrdDraft(self, request, context):  # type: ignore[no-untyped-def]
        return {"success": True}

    def UpdateIdeaKeywords(self, request, context):  # type: ignore[no-untyped-def]
        return {"success": True}

    def GetIdeasByState(self, request, context):  # type: ignore[no-untyped-def]
        return {"counts": []}

    def GetUserStats(self, request, context):  # type: ignore[no-untyped-def]
        return {"idea_count": 0, "review_count": 0, "contribution_count": 0}

    def GetRateLimitStatus(self, request, context):  # type: ignore[no-untyped-def]
        return {"current_count": 0, "cap": 100, "is_locked": False}
