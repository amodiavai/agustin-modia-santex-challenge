from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import ChatMessage, get_db
from pydantic import BaseModel
from datetime import datetime

class ChatHistoryItem(BaseModel):
    id: int
    user_message: str
    assistant_response: str
    timestamp: datetime
    session_id: str

    class Config:
        from_attributes = True

class ChatHistoryService:
    def __init__(self):
        pass

    def save_chat_message(self, db: Session, user_message: str, assistant_response: str, session_id: str = "default"):
        """Save a chat message to the database"""
        chat_message = ChatMessage(
            user_message=user_message,
            assistant_response=assistant_response,
            session_id=session_id
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message

    def get_chat_history(self, db: Session, session_id: str = "default", limit: int = 50) -> List[ChatHistoryItem]:
        """Get chat history from the database"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        return [ChatHistoryItem.from_orm(msg) for msg in messages]

    def clear_chat_history(self, db: Session, session_id: str = "default"):
        """Clear chat history for a session"""
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        db.commit()

    def get_recent_messages_for_context(self, db: Session, session_id: str = "default", limit: int = 10) -> List[Dict[str, str]]:
        """Get recent messages formatted for conversation context"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        # Reverse to get chronological order
        messages.reverse()
        
        context = []
        for msg in messages:
            context.append({"role": "user", "content": msg.user_message})
            context.append({"role": "assistant", "content": msg.assistant_response})
        
        return context