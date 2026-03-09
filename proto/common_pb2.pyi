from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserRef(_message.Message):
    __slots__ = ("id", "display_name", "email")
    ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    id: str
    display_name: str
    email: str
    def __init__(self, id: _Optional[str] = ..., display_name: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...

class PaginationRequest(_message.Message):
    __slots__ = ("page", "page_size")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ("total_count", "page", "page_size")
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    total_count: int
    page: int
    page_size: int
    def __init__(self, total_count: _Optional[int] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class Reaction(_message.Message):
    __slots__ = ("id", "message_id", "reaction_type", "created_by_type", "created_by_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    REACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    message_id: str
    reaction_type: str
    created_by_type: str
    created_by_id: str
    created_at: str
    def __init__(self, id: _Optional[str] = ..., message_id: _Optional[str] = ..., reaction_type: _Optional[str] = ..., created_by_type: _Optional[str] = ..., created_by_id: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class BoardNode(_message.Message):
    __slots__ = ("id", "idea_id", "node_type", "content", "x_position", "y_position", "parent_id", "sort_order", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    IDEA_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    X_POSITION_FIELD_NUMBER: _ClassVar[int]
    Y_POSITION_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    idea_id: str
    node_type: str
    content: str
    x_position: float
    y_position: float
    parent_id: str
    sort_order: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., idea_id: _Optional[str] = ..., node_type: _Optional[str] = ..., content: _Optional[str] = ..., x_position: _Optional[float] = ..., y_position: _Optional[float] = ..., parent_id: _Optional[str] = ..., sort_order: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class BoardConnection(_message.Message):
    __slots__ = ("id", "idea_id", "source_node_id", "target_node_id", "label", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    IDEA_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_NODE_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    idea_id: str
    source_node_id: str
    target_node_id: str
    label: str
    created_at: str
    def __init__(self, id: _Optional[str] = ..., idea_id: _Optional[str] = ..., source_node_id: _Optional[str] = ..., target_node_id: _Optional[str] = ..., label: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...
