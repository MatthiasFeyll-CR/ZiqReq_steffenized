from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PdfGenerationRequest(_message.Message):
    __slots__ = ("project_id", "project_type", "title", "short_description", "structure_json", "generated_date")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SHORT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_JSON_FIELD_NUMBER: _ClassVar[int]
    GENERATED_DATE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    project_type: str
    title: str
    short_description: str
    structure_json: str
    generated_date: str
    def __init__(self, project_id: _Optional[str] = ..., project_type: _Optional[str] = ..., title: _Optional[str] = ..., short_description: _Optional[str] = ..., structure_json: _Optional[str] = ..., generated_date: _Optional[str] = ...) -> None: ...

class PdfGenerationResponse(_message.Message):
    __slots__ = ("pdf_data", "filename")
    PDF_DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    pdf_data: bytes
    filename: str
    def __init__(self, pdf_data: _Optional[bytes] = ..., filename: _Optional[str] = ...) -> None: ...
