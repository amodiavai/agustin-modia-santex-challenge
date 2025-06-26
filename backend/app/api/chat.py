from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
from app.services.chat_service import ChatService
from app.services.chat_history_service import ChatHistoryService, ChatHistoryItem
from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# Modelos para las peticiones y respuestas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []

# Función para obtener servicios
async def get_chat_service():
    return ChatService()

async def get_chat_history_service():
    return ChatHistoryService()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    db: Session = Depends(get_db)
):
    """
    Envía un mensaje al gemelo digital y obtiene una respuesta.
    """
    try:
        # Convertir historial a formato esperado
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Obtener respuesta del servicio de chat
        response = await chat_service.get_response(request.message, history)
        
        # Guardar en historial
        chat_history_service.save_chat_message(
            db=db,
            user_message=request.message,
            assistant_response=response["response"],
            session_id=current_user
        )
        
        return {
            "response": response["response"],
            "sources": response.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error en /chat/send: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Envía un mensaje al gemelo digital y obtiene una respuesta en streaming.
    """
    try:
        # Convertir historial a formato esperado
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Crear función generadora para streaming
        async def response_generator():
            async for chunk in chat_service.get_streaming_response(request.message, history):
                # Convertir el chunk a formato de evento SSE
                if chunk["finished"]:
                    yield f"data: [DONE]\n\n"
                else:
                    yield f"data: {chunk['chunk']}\n\n"
        
        # Devolver streaming response
        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error en /chat/stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=List[ChatHistoryItem])
async def get_chat_history(
    current_user: str = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Obtiene el historial de chat del usuario.
    """
    try:
        return chat_history_service.get_chat_history(db, current_user, limit)
    except Exception as e:
        logger.error(f"Error en /chat/history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/history")
async def clear_chat_history(
    current_user: str = Depends(get_current_user),
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service),
    db: Session = Depends(get_db)
):
    """
    Limpia el historial de chat del usuario.
    """
    try:
        chat_history_service.clear_chat_history(db, current_user)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        logger.error(f"Error en /chat/history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
