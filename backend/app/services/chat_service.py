import os
import logging
from typing import Dict, List, Any, AsyncGenerator, Optional
import json
from openai import OpenAI, AsyncOpenAI

from app.agents.gemelo_agent import GemeloAgent

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        """
        Inicializa el servicio de chat que gestiona las conversaciones
        con el gemelo digital
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no encontrada en variables de entorno")
            
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Servicio de chat utilizando modelo OpenAI: {self.model}")
        
        # Inicializar el agente de LangGraph
        self.agent = GemeloAgent()
        
    async def get_response(
        self, 
        message: str, 
        history: List[Dict[str, str]] = None,
        use_streaming: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene una respuesta del gemelo digital sin streaming
        
        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            use_streaming: Si es True, prepara la respuesta para streaming
            
        Returns:
            Diccionario con la respuesta
        """
        if not history:
            history = []
            
        try:
            # Usar el agente de LangGraph para procesar el mensaje
            response = await self.agent.process_message(message, history)
            
            return {
                "response": response["response"],
                "sources": response.get("sources", []),
                "thought_process": response.get("thought_process", "")
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo respuesta: {str(e)}")
            return {
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "error": str(e)
            }
            
    async def get_streaming_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Obtiene una respuesta del gemelo digital con streaming
        
        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            
        Yields:
            Chunks de la respuesta para streaming
        """
        if not history:
            history = []
            
        try:
            # Preparar para streaming usando el agente
            async for chunk in self.agent.process_message_streaming(message, history):
                yield {
                    "chunk": chunk,
                    "finished": False
                }
                
            # Enviar señal de finalización
            yield {
                "chunk": "",
                "finished": True
            }
            
        except Exception as e:
            logger.error(f"Error en streaming de respuesta: {str(e)}")
            yield {
                "chunk": f"Lo siento, ocurrió un error: {str(e)}",
                "finished": True
            }
