from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

class MessageRole(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'

# Document schemas
class DocumentCreate(BaseModel):
    session_id: UUID
    filename: str
    file_type: str = Field(..., pattern="^(txt|pdf|doc|docx|csv|json|xlsx)$")
    meta_info: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    meta_info: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Chat schemas
class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    meta_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: UUID
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[ChatMessageResponse]] = None

    class Config:
        from_attributes = True

class LogLevel(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    DEBUG = 'debug' 