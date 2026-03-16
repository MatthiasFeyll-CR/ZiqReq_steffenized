from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PdfGenerationRequest(_message.Message):
    __slots__ = ("project_id", "project_title", "sections", "generated_at")
    class SectionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_TITLE_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    project_title: str
    sections: _containers.ScalarMap[str, str]
    generated_at: str
    def __init__(self, project_id: _Optional[str] = ..., project_title: _Optional[str] = ..., sections: _Optional[_Mapping[str, str]] = ..., generated_at: _Optional[str] = ...) -> None: ...

class PdfGenerationResponse(_message.Message):
    __slots__ = ("pdf_data", "filename")
    PDF_DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    pdf_data: bytes
    filename: str
    def __init__(self, pdf_data: _Optional[bytes] = ..., filename: _Optional[str] = ...) -> None: ...
