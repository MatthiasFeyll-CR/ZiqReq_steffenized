from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ChatProcessingRequest(_message.Message):
    __slots__ = ("idea_id", "message_id")
    IDEA_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    idea_id: str
    message_id: str
    def __init__(self, idea_id: _Optional[str] = ..., message_id: _Optional[str] = ...) -> None: ...

class ChatProcessingResponse(_message.Message):
    __slots__ = ("status", "processing_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_ID_FIELD_NUMBER: _ClassVar[int]
    status: str
    processing_id: str
    def __init__(self, status: _Optional[str] = ..., processing_id: _Optional[str] = ...) -> None: ...

class BrdGenerationRequest(_message.Message):
    __slots__ = ("idea_id", "mode", "sections_to_regenerate", "instruction", "allow_information_gaps")
    IDEA_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_TO_REGENERATE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    ALLOW_INFORMATION_GAPS_FIELD_NUMBER: _ClassVar[int]
    idea_id: str
    mode: str
    sections_to_regenerate: _containers.RepeatedScalarFieldContainer[str]
    instruction: str
    allow_information_gaps: bool
    def __init__(self, idea_id: _Optional[str] = ..., mode: _Optional[str] = ..., sections_to_regenerate: _Optional[_Iterable[str]] = ..., instruction: _Optional[str] = ..., allow_information_gaps: bool = ...) -> None: ...

class BrdGenerationResponse(_message.Message):
    __slots__ = ("status", "generation_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    GENERATION_ID_FIELD_NUMBER: _ClassVar[int]
    status: str
    generation_id: str
    def __init__(self, status: _Optional[str] = ..., generation_id: _Optional[str] = ...) -> None: ...

class ContextReindexRequest(_message.Message):
    __slots__ = ("bucket_id",)
    BUCKET_ID_FIELD_NUMBER: _ClassVar[int]
    bucket_id: str
    def __init__(self, bucket_id: _Optional[str] = ...) -> None: ...

class ContextReindexResponse(_message.Message):
    __slots__ = ("status", "chunk_count")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_COUNT_FIELD_NUMBER: _ClassVar[int]
    status: str
    chunk_count: int
    def __init__(self, status: _Optional[str] = ..., chunk_count: _Optional[int] = ...) -> None: ...

class FacilitatorBucketResponse(_message.Message):
    __slots__ = ("id", "content", "updated_by_id", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    content: str
    updated_by_id: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., content: _Optional[str] = ..., updated_by_id: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class UpdateFacilitatorBucketRequest(_message.Message):
    __slots__ = ("content", "updated_by_id")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    content: str
    updated_by_id: str
    def __init__(self, content: _Optional[str] = ..., updated_by_id: _Optional[str] = ...) -> None: ...

class ContextAgentBucketResponse(_message.Message):
    __slots__ = ("id", "sections_json", "free_text", "updated_by_id", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_JSON_FIELD_NUMBER: _ClassVar[int]
    FREE_TEXT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    sections_json: str
    free_text: str
    updated_by_id: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., sections_json: _Optional[str] = ..., free_text: _Optional[str] = ..., updated_by_id: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class UpdateContextAgentBucketRequest(_message.Message):
    __slots__ = ("sections_json", "free_text", "updated_by_id")
    SECTIONS_JSON_FIELD_NUMBER: _ClassVar[int]
    FREE_TEXT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_ID_FIELD_NUMBER: _ClassVar[int]
    sections_json: str
    free_text: str
    updated_by_id: str
    def __init__(self, sections_json: _Optional[str] = ..., free_text: _Optional[str] = ..., updated_by_id: _Optional[str] = ...) -> None: ...

class AiMetricsRequest(_message.Message):
    __slots__ = ("time_range",)
    TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    time_range: str
    def __init__(self, time_range: _Optional[str] = ...) -> None: ...

class AiMetricsResponse(_message.Message):
    __slots__ = ("processing_count", "success_rate", "latency_p50_ms", "latency_p95_ms", "total_input_tokens", "total_output_tokens", "delegation_count", "compression_count", "board_agent_count", "error_count", "abort_count", "extension_count")
    PROCESSING_COUNT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_RATE_FIELD_NUMBER: _ClassVar[int]
    LATENCY_P50_MS_FIELD_NUMBER: _ClassVar[int]
    LATENCY_P95_MS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_INPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_OUTPUT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    DELEGATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_COUNT_FIELD_NUMBER: _ClassVar[int]
    BOARD_AGENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
    ABORT_COUNT_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_COUNT_FIELD_NUMBER: _ClassVar[int]
    processing_count: int
    success_rate: float
    latency_p50_ms: float
    latency_p95_ms: float
    total_input_tokens: int
    total_output_tokens: int
    delegation_count: int
    compression_count: int
    board_agent_count: int
    error_count: int
    abort_count: int
    extension_count: int
    def __init__(self, processing_count: _Optional[int] = ..., success_rate: _Optional[float] = ..., latency_p50_ms: _Optional[float] = ..., latency_p95_ms: _Optional[float] = ..., total_input_tokens: _Optional[int] = ..., total_output_tokens: _Optional[int] = ..., delegation_count: _Optional[int] = ..., compression_count: _Optional[int] = ..., board_agent_count: _Optional[int] = ..., error_count: _Optional[int] = ..., abort_count: _Optional[int] = ..., extension_count: _Optional[int] = ...) -> None: ...
