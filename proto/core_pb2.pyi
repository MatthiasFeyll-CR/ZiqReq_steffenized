import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectContextRequest(_message.Message):
    __slots__ = ("project_id", "recent_message_limit", "include_brd_draft")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RECENT_MESSAGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_BRD_DRAFT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    recent_message_limit: int
    include_brd_draft: bool
    def __init__(self, project_id: _Optional[str] = ..., recent_message_limit: _Optional[int] = ..., include_brd_draft: bool = ...) -> None: ...

class ProjectContextResponse(_message.Message):
    __slots__ = ("metadata", "recent_messages", "brd_draft", "active_users")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RECENT_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    BRD_DRAFT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_USERS_FIELD_NUMBER: _ClassVar[int]
    metadata: ProjectMetadata
    recent_messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    brd_draft: BrdDraftState
    active_users: _containers.RepeatedCompositeFieldContainer[UserInfo]
    def __init__(self, metadata: _Optional[_Union[ProjectMetadata, _Mapping]] = ..., recent_messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., brd_draft: _Optional[_Union[BrdDraftState, _Mapping]] = ..., active_users: _Optional[_Iterable[_Union[UserInfo, _Mapping]]] = ...) -> None: ...

class ProjectMetadata(_message.Message):
    __slots__ = ("project_id", "title", "title_manually_edited", "state", "agent_mode", "owner_display_name", "co_owner_display_name", "project_type")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TITLE_MANUALLY_EDITED_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    AGENT_MODE_FIELD_NUMBER: _ClassVar[int]
    OWNER_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    CO_OWNER_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    title: str
    title_manually_edited: bool
    state: str
    agent_mode: str
    owner_display_name: str
    co_owner_display_name: str
    project_type: str
    def __init__(self, project_id: _Optional[str] = ..., title: _Optional[str] = ..., title_manually_edited: bool = ..., state: _Optional[str] = ..., agent_mode: _Optional[str] = ..., owner_display_name: _Optional[str] = ..., co_owner_display_name: _Optional[str] = ..., project_type: _Optional[str] = ...) -> None: ...

class BrdDraftState(_message.Message):
    __slots__ = ("project_id", "sections", "locked_sections", "updated_at")
    class SectionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class LockedSectionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    LOCKED_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    sections: _containers.ScalarMap[str, str]
    locked_sections: _containers.ScalarMap[str, bool]
    updated_at: str
    def __init__(self, project_id: _Optional[str] = ..., sections: _Optional[_Mapping[str, str]] = ..., locked_sections: _Optional[_Mapping[str, bool]] = ..., updated_at: _Optional[str] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ("id", "display_name", "role")
    ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    id: str
    display_name: str
    role: str
    def __init__(self, id: _Optional[str] = ..., display_name: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ("id", "sender_type", "sender_display_name", "content", "message_type", "created_at", "reactions")
    ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SENDER_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    REACTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    sender_type: str
    sender_display_name: str
    content: str
    message_type: str
    created_at: str
    reactions: _containers.RepeatedCompositeFieldContainer[_common_pb2.Reaction]
    def __init__(self, id: _Optional[str] = ..., sender_type: _Optional[str] = ..., sender_display_name: _Optional[str] = ..., content: _Optional[str] = ..., message_type: _Optional[str] = ..., created_at: _Optional[str] = ..., reactions: _Optional[_Iterable[_Union[_common_pb2.Reaction, _Mapping]]] = ...) -> None: ...

class FullChatHistoryRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class FullChatHistoryResponse(_message.Message):
    __slots__ = ("messages",)
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    def __init__(self, messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ...) -> None: ...

class AiChatMessageRequest(_message.Message):
    __slots__ = ("project_id", "content", "message_type", "language", "processing_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    content: str
    message_type: str
    language: str
    processing_id: str
    def __init__(self, project_id: _Optional[str] = ..., content: _Optional[str] = ..., message_type: _Optional[str] = ..., language: _Optional[str] = ..., processing_id: _Optional[str] = ...) -> None: ...

class AiChatMessageResponse(_message.Message):
    __slots__ = ("message_id", "created_at")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    created_at: str
    def __init__(self, message_id: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class AiReactionRequest(_message.Message):
    __slots__ = ("project_id", "message_id", "reaction_type")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    REACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    message_id: str
    reaction_type: str
    def __init__(self, project_id: _Optional[str] = ..., message_id: _Optional[str] = ..., reaction_type: _Optional[str] = ...) -> None: ...

class AiReactionResponse(_message.Message):
    __slots__ = ("reaction_id",)
    REACTION_ID_FIELD_NUMBER: _ClassVar[int]
    reaction_id: str
    def __init__(self, reaction_id: _Optional[str] = ...) -> None: ...

class UpdateTitleRequest(_message.Message):
    __slots__ = ("project_id", "new_title")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_TITLE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    new_title: str
    def __init__(self, project_id: _Optional[str] = ..., new_title: _Optional[str] = ...) -> None: ...

class UpdateTitleResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UpdateBrdDraftRequest(_message.Message):
    __slots__ = ("project_id", "sections", "readiness_evaluation_json")
    class SectionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    READINESS_EVALUATION_JSON_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    sections: _containers.ScalarMap[str, str]
    readiness_evaluation_json: str
    def __init__(self, project_id: _Optional[str] = ..., sections: _Optional[_Mapping[str, str]] = ..., readiness_evaluation_json: _Optional[str] = ...) -> None: ...

class UpdateBrdDraftResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ProjectsByStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProjectsByStateResponse(_message.Message):
    __slots__ = ("counts",)
    COUNTS_FIELD_NUMBER: _ClassVar[int]
    counts: _containers.RepeatedCompositeFieldContainer[StateCount]
    def __init__(self, counts: _Optional[_Iterable[_Union[StateCount, _Mapping]]] = ...) -> None: ...

class StateCount(_message.Message):
    __slots__ = ("state", "count")
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    state: str
    count: int
    def __init__(self, state: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class GetUserStatsRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class UserStatsResponse(_message.Message):
    __slots__ = ("project_count", "review_count", "contribution_count")
    PROJECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    REVIEW_COUNT_FIELD_NUMBER: _ClassVar[int]
    CONTRIBUTION_COUNT_FIELD_NUMBER: _ClassVar[int]
    project_count: int
    review_count: int
    contribution_count: int
    def __init__(self, project_count: _Optional[int] = ..., review_count: _Optional[int] = ..., contribution_count: _Optional[int] = ...) -> None: ...

class RateLimitRequest(_message.Message):
    __slots__ = ("project_id",)
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    def __init__(self, project_id: _Optional[str] = ...) -> None: ...

class RateLimitResponse(_message.Message):
    __slots__ = ("current_count", "cap", "is_locked")
    CURRENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    CAP_FIELD_NUMBER: _ClassVar[int]
    IS_LOCKED_FIELD_NUMBER: _ClassVar[int]
    current_count: int
    cap: int
    is_locked: bool
    def __init__(self, current_count: _Optional[int] = ..., cap: _Optional[int] = ..., is_locked: bool = ...) -> None: ...
