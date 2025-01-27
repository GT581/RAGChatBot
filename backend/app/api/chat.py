from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.database import get_db
from ..services.chat_service import ChatService
from ..schemas.models import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionCreate
)
import uuid
from uuid import UUID

router = APIRouter(prefix="/chat")

@router.post("/sessions/", response_model=ChatSessionResponse)
async def create_chat_session(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    return await chat_service.create_session(user_id)

@router.get("/sessions/{user_id}", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    return chat_service.get_user_sessions(user_id)

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    return chat_service.get_chat_history(str(session_id))

@router.post("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def create_message(
    session_id: UUID,
    message: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    messages = await chat_service.generate_response(
        str(session_id),
        message.content
    )
    await chat_service.update_session_title(str(session_id))
    return messages

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db)
    return await chat_service.delete_session(str(session_id)) 