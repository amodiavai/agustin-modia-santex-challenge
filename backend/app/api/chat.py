from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
from app.services.chat_service import ChatService

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

# Función para obtener servicio de chat
async def get_chat_service():
    return ChatService()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Envía un mensaje al gemelo digital y obtiene una respuesta.
    """
    try:
        # Convertir historial a formato esperado
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Obtener respuesta del servicio de chat
        response = await chat_service.get_response(request.message, history)
        
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
