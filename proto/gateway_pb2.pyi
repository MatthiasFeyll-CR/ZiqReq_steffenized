from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateNotificationRequest(_message.Message):
    __slots__ = ("user_id", "event_type", "title", "body", "reference_id", "reference_type")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    event_type: str
    title: str
    body: str
    reference_id: str
    reference_type: str
    def __init__(self, user_id: _Optional[str] = ..., event_type: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., reference_id: _Optional[str] = ..., reference_type: _Optional[str] = ...) -> None: ...

class CreateNotificationResponse(_message.Message):
    __slots__ = ("notification_id",)
    NOTIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    notification_id: str
    def __init__(self, notification_id: _Optional[str] = ...) -> None: ...

class UserPreferencesRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class UserPreferencesResponse(_message.Message):
    __slots__ = ("user_id", "email", "display_name", "email_notification_preferences")
    class EmailNotificationPreferencesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_NOTIFICATION_PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    display_name: str
    email_notification_preferences: _containers.ScalarMap[str, bool]
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., display_name: _Optional[str] = ..., email_notification_preferences: _Optional[_Mapping[str, bool]] = ...) -> None: ...

class AlertRecipientsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AlertRecipientsResponse(_message.Message):
    __slots__ = ("recipients",)
    RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    recipients: _containers.RepeatedCompositeFieldContainer[AlertRecipient]
    def __init__(self, recipients: _Optional[_Iterable[_Union[AlertRecipient, _Mapping]]] = ...) -> None: ...

class AlertRecipient(_message.Message):
    __slots__ = ("user_id", "email", "display_name")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    display_name: str
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., display_name: _Optional[str] = ...) -> None: ...
