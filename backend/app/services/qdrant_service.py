import os
import logging
from typing import List, Dict, Any, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        """
        Inicializa el servicio de Qdrant para almacenamiento y búsqueda de vectores
        """
        self.collection_name = os.getenv("COLLECTION_NAME", "gemelo_agustin_large")
        self.vector_size = 3072  # Dimensión del modelo text-embedding-3-large
        
        # Configuración para Railway, Docker y servicios externos
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_private_url = os.getenv("QDRANT_PRIVATE_URL")  # Railway internal URL
        
        # Prioridad: URL externa > URL privada Railway > host:port tradicional
        if qdrant_url:
            # Usar URL completa (para Qdrant Cloud o URLs externas)
            try:
                api_key = os.getenv("QDRANT_API_KEY")
                self.client = QdrantClient(url=qdrant_url, api_key=api_key)
                logger.info(f"Conexión exitosa a Qdrant usando URL externa: {qdrant_url}")
            except Exception as e:
                logger.error(f"Error conectando a Qdrant con URL externa: {str(e)}")
                raise
        elif qdrant_private_url:
            # Usar URL privada de Railway (comunicación interna entre servicios)
            try:
                self.client = QdrantClient(url=qdrant_private_url)
                logger.info(f"Conexión exitosa a Qdrant usando URL privada Railway: {qdrant_private_url}")
            except Exception as e:
                logger.error(f"Error conectando a Qdrant con URL privada Railway: {str(e)}")
                raise
        else:
            # Configuración tradicional host:port (para Docker local)
            self.host = os.getenv("QDRANT_HOST", "localhost")
            self.port = int(os.getenv("QDRANT_PORT", "6333"))
            try:
                self.client = QdrantClient(host=self.host, port=self.port)
                logger.info(f"Conexión exitosa a Qdrant en {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Error conectando a Qdrant: {str(e)}")
                raise
    
    async def collection_exists(self) -> bool:
        """
        Verifica si la colección existe en Qdrant
        
        Returns:
            True si la colección existe, False en caso contrario
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Error verificando si existe la colección {self.collection_name}: {str(e)}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la colección
        
        Returns:
            Diccionario con información de la colección
        """
        try:
            # Verificar si la colección existe
            if not await self.collection_exists():
                return {"exists": False, "points_count": 0}
            
            # Obtener información de la colección
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            
            # Construir respuesta
            return {
                "exists": True,
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de colección {self.collection_name}: {str(e)}")
            return {"exists": False, "error": str(e)}

    async def initialize_collection(self) -> bool:
        """
        Inicializa la colección en Qdrant si no existe
        
        Returns:
            True si la colección se creó o ya existía, False en caso de error
        """
        try:
            # Verificar si la colección ya existe
            if await self.collection_exists():
                logger.info(f"Colección {self.collection_name} ya existe")
                return True
                
            # Crear la colección si no existe
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                ),
                # Configurar índices para metadatos importantes
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0,  # Indexar inmediatamente
                ),
            )
            
            # Crear índice para búsquedas por metadata
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.file_name",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            
            # Crear índice para búsquedas por metadata
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="metadata.source",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            
            logger.info(f"Colección {self.collection_name} creada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando colección {self.collection_name}: {str(e)}")
            return False
    
    async def insert_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Inserta documentos con sus embeddings en Qdrant
        
        Args:
            documents: Lista de documentos con campos 'text', 'embedding' y 'metadata'
            
        Returns:
            Lista de IDs de documentos insertados
        """
        if not documents:
            return []
            
        try:
            points = []
            ids = []
            
            for i, doc in enumerate(documents):
                # Verificar que tenga embedding
                if "embedding" not in doc:
                    logger.warning(f"Documento {i} no tiene embedding, saltando...")
                    continue
                
                # Generar ID único para el punto
                point_id = len(ids) + 1
                ids.append(str(point_id))
                
                # Crear punto para Qdrant
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=doc["embedding"],
                        payload={
                            "text": doc["text"],
                            "metadata": doc["metadata"]
                        }
                    )
                )
            
            # Insertar puntos en la colección
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Insertados {len(points)} documentos en Qdrant")
            return ids
            
        except Exception as e:
            logger.error(f"Error insertando documentos en Qdrant: {str(e)}")
            raise
    
    async def search(self, query_vector: List[float], limit: int = 5, filter_params: Optional[Dict] = None) -> List[Dict]:
        """
        Busca documentos similares a un vector de consulta
        
        Args:
            query_vector: Vector de embedding de la consulta
            limit: Número máximo de resultados
            filter_params: Filtros adicionales para la búsqueda
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            # Construir filtro si existe
            search_filter = None
            if filter_params:
                filter_conditions = []
                
                if 'file_name' in filter_params:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.file_name",
                            match=models.MatchValue(value=filter_params['file_name'])
                        )
                    )
                    
                if 'source' in filter_params:
                    filter_conditions.append(
                        models.FieldCondition(
                            key="metadata.source",
                            match=models.MatchValue(value=filter_params['source'])
                        )
                    )
                    
                if filter_conditions:
                    search_filter = models.Filter(
                        must=filter_conditions
                    )
            
            # Realizar búsqueda
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
            
            # Formatear resultados
            results = []
            for hit in search_result:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {})
                }
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error buscando en Qdrant: {str(e)}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la colección
        
        Returns:
            Diccionario con estadísticas de la colección
        """
        try:
            # Verificar si la colección existe
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                return {
                    "exists": False,
                    "count": 0,
                    "name": self.collection_name
                }
            
            # Obtener estadísticas
            collection_info = self.client.get_collection(self.collection_name)
            # Use points_count which represents actual documents stored
            count = getattr(collection_info, 'points_count', 0) or 0
            
            return {
                "exists": True,
                "count": count,
                "name": self.collection_name,
                "vector_size": self.vector_size
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo info de colección: {str(e)}")
            return {
                "exists": False,
                "error": str(e)
            }
    
    async def get_documents_by_filename(self, filename: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los documentos que pertenecen a un archivo específico
        
        Args:
            filename: Nombre del archivo a buscar
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            # Verificar si la colección existe
            if not await self.collection_exists():
                logger.warning(f"No se puede buscar {filename}: La colección no existe")
                return []
                
            # Buscar puntos con el nombre de archivo
            search_response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.file_name",
                            match=models.MatchValue(value=filename)
                        )
                    ]
                ),
                limit=10000,  # Máximo razonable para recuperar todos los puntos
                with_payload=True,  # Necesitamos los payloads para ver los metadatos
                with_vectors=False,  # No necesitamos los vectores
            )
            
            # Convertir resultados a formato más amigable
            documents = []
            for point in search_response[0]:
                if hasattr(point, 'payload') and point.payload:
                    doc = {
                        'id': point.id,
                        'text': point.payload.get('text', ''),
                        'metadata': point.payload.get('metadata', {})
                    }
                    documents.append(doc)
            
            logger.info(f"Encontrados {len(documents)} documentos con nombre {filename}")
            return documents
            
        except Exception as e:
            logger.error(f"Error buscando documentos por nombre {filename}: {str(e)}")
            return []
    
    async def delete_by_filter(self, filter_params: Dict) -> int:
        """
        Elimina documentos que coincidan con el filtro
        
        Args:
            filter_params: Diccionario con filtros (e.g., {'file_name': 'doc1.pdf'})
            
        Returns:
            Número de documentos eliminados
        """
        try:
            # Construir filtro
            filter_conditions = []
            
            if 'file_name' in filter_params:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.file_name",
                        match=models.MatchValue(value=filter_params['file_name'])
                    )
                )
                
            if 'source' in filter_params:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=filter_params['source'])
                    )
                )
                
            if not filter_conditions:
                logger.warning("No se especificó ningún filtro para eliminar documentos")
                return 0
                
            search_filter = models.Filter(
                must=filter_conditions
            )
            
            # Eliminar puntos que coincidan con el filtro
            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=search_filter
                )
            )
            
            return getattr(result, 'deleted', 0)
            
        except Exception as e:
            logger.error(f"Error eliminando documentos: {str(e)}")
            raise
