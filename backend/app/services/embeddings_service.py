import os
import logging
import time
from typing import List, Dict, Any, Union
from openai import OpenAI, RateLimitError

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        """
        Inicializa el servicio de embeddings usando OpenAI
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no encontrada en variables de entorno")
            
        self.client = OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-large"
        self.max_retries = 3
        self.retry_delay = 5  # segundos
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de strings con los textos a vectorizar
            
        Returns:
            Lista de embeddings (vectores)
        """
        if not texts:
            return []
            
        embeddings = []
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Llamada a la API de OpenAI para obtener embeddings
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                
                # Extraer vectores de la respuesta
                embeddings = [item.embedding for item in response.data]
                return embeddings
                
            except RateLimitError:
                retry_count += 1
                logger.warning(f"Rate limit alcanzado. Reintento {retry_count}/{self.max_retries}")
                
                if retry_count < self.max_retries:
                    # Esperar antes de reintentar
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Se alcanzó el máximo de reintentos para generar embeddings")
                    raise
                    
            except Exception as e:
                logger.error(f"Error generando embeddings: {str(e)}")
                raise
    
    async def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa una lista de documentos y agrega sus embeddings
        
        Args:
            documents: Lista de documentos (dicts con 'text' y 'metadata')
            
        Returns:
            Lista de documentos con embeddings agregados
        """
        if not documents:
            return []
            
        # Extraer solo los textos
        texts = [doc["text"] for doc in documents]
        
        # Generar embeddings
        embeddings = await self.create_embeddings(texts)
        
        # Asociar embeddings a cada documento
        for i, embedding in enumerate(embeddings):
            documents[i]["embedding"] = embedding
            
        return documents
