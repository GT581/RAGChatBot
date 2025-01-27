from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService
from ..db.models import ChatSession, ChatMessage
from ..schemas.models import MessageRole, ChatMessageResponse
import uuid
from datetime import datetime
from fastapi import HTTPException
from app.core.settings import settings

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMService()
        self.document_service = DocumentService(db)
        self.max_history = settings.MAX_HISTORY
        self.temperature = settings.TEMPERATURE
        
    async def create_session(self, user_id: str) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            title="New Chat"
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.hidden == False
        ).all()

    def get_chat_history(self, session_id: str, limit: int = None) -> List[ChatMessage]:
        query = self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        if limit:
            query = query.limit(limit)
        return query.all()

    async def generate_response(self, session_id: str, message_content: str) -> List[ChatMessage]:
        # Validate session exists
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = self.get_chat_history(session_id, limit=self.max_history)
        
        # Save user message first
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.USER,
            content=message_content
        )
        self.db.add(user_message)
        self.db.commit()
        
        # Add system prompt if it's a new conversation
        if len(messages) == 0:
            system_message = ChatMessage(
                session_id=session_id,
                role=MessageRole.SYSTEM,
                content=SYSTEM_PROMPT
            )
            self.db.add(system_message)
            self.db.commit()
            messages = [system_message, user_message]
        else:
            messages.append(user_message)

        # Get chat history for context
        formatted_messages = [
            {"role": str(msg.role.value), "content": msg.content}
            for msg in messages
        ]

        # Retrieve relevant documents
        relevant_chunks, scores = await self.document_service.search_similar_chunks(
            message_content, 
            session_id,
            limit=SIMILARITY_TOP_K
        )
        
        # Format context from relevant documents
        if relevant_chunks:
            context_text = "\n\nRelevant context:\n" + "\n\n".join([
                f"From document '{chunk.document.filename}':\n{chunk.content}"
                for chunk in relevant_chunks
            ])
            print(f"Using context: {context_text}")  # Debug log
            
            # Add context to the user's message
            formatted_messages[-1]["content"] = f"{message_content}\n\n{context_text}"
        else:
            print("No relevant chunks found")

        # Generate response using LLM
        response_content = await self.llm.generate_response(
            formatted_messages,
        )

        # Save assistant message with source information
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response_content,
            meta_info={
                "used_chunks": [
                    {
                        "document_id": str(chunk.document.id),
                        "chunk_id": str(chunk.id),
                        "filename": chunk.document.filename,
                        "similarity_score": score
                    }
                    for chunk, score in zip(relevant_chunks, scores)
                ]
            }
        )
        self.db.add(assistant_message)
        self.db.commit()
        
        return [user_message, assistant_message]

    async def delete_session(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.hidden = True  # Soft delete
        self.db.commit()
        return {"message": "Session hidden"}

    async def update_session_title(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            return
        
        # Get the last message
        last_message = self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .first()
        
        if last_message:
            # Use the first 50 characters of the last message as title
            session.title = last_message.content[:50] + ("..." if len(last_message.content) > 50 else "")
            self.db.commit() 

SYSTEM_PROMPT = settings.SYSTEM_PROMPT
SIMILARITY_TOP_K = settings.SIMILARITY_TOP_K