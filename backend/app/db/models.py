from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from .database import Base
from ..schemas.models import MessageRole
from pgvector.sqlalchemy import Vector

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String)
    title = Column(String, nullable=True)
    hidden = Column(Boolean, default=False)  # For soft deletion
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("ChatMessage", back_populates="session")
    documents = relationship("Document", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    role = Column(Enum(MessageRole))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_info = Column(JSON, nullable=True)  # Store references to used chunks
    
    session = relationship("ChatSession", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    filename = Column(String)  # Keep track of source file
    file_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta_info = Column(JSON)
    
    session = relationship("ChatSession", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    chunk_index = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    document = relationship("Document", back_populates="chunks") 