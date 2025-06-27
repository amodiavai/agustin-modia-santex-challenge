from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, JSONResponse
import logging
from typing import List, Dict, Any
import os
import time
from pathlib import Path

# Configurar logger
logger = logging.getLogger(__name__)

from app.services.qdrant_service import QdrantService
from app.agents.gemelo_agent import GemeloAgent

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/reset_collection")
async def reset_collection():
    """
    Reinicia la colección en Qdrant (elimina y vuelve a crear)
    
    Útil para cuando se cambia la dimensión de los vectores
    """
    # Crear instancia de QdrantService
    qdrant_service = QdrantService()
    
    # Verificar si la colección existe
    if await qdrant_service.collection_exists():
        # Eliminar la colección
        try:
            qdrant_service.client.delete_collection(
                collection_name=qdrant_service.collection_name
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error eliminando la colección: {str(e)}")
    
    # Crear la colección nuevamente
    if not await qdrant_service.initialize_collection():
        raise HTTPException(status_code=500, detail="Error recreando la colección")
    
    return {"message": f"Colección {qdrant_service.collection_name} reiniciada correctamente"}

@router.get("/metadata")
async def get_documents_metadata() -> Dict[str, Any]:
    """
    Obtiene los metadatos de todos los documentos almacenados en Qdrant
    """
    logger = getLogger(__name__)
    logger.info("Obteniendo metadatos de documentos")
    
    # Crear instancia de QdrantService
    qdrant_service = QdrantService()
    
    try:
        # Obtener todos los puntos de la colección
        collection_info = await qdrant_service.get_collection_info()
        points_count = collection_info.get("points_count", 0)
        
        # Recuperar todos los documentos con un límite alto
        # En producción esto debería paginarse
        search_results = await qdrant_service.search(
            query_vector=[0.0] * qdrant_service.vector_size,  # Vector vacío para obtener todos los documentos
            limit=min(points_count, 100),  # Limitar a 100 máximo
            score_threshold=0.0  # Sin umbral mínimo
        )
        
        # Agrupar por nombre de archivo
        documents_by_file = {}
        for result in search_results:
            file_name = result["metadata"].get("file_name", "unknown")
            
            if file_name not in documents_by_file:
                documents_by_file[file_name] = {
                    "file_name": file_name,
                    "document_summary": result["metadata"].get("document_summary", ""),
                    "document_type": result["metadata"].get("document_type", "general"),
                    "chunk_count": 1,
                    "sample_text": result["text"][:150] + "..." if len(result["text"]) > 150 else result["text"]
                }
            else:
                documents_by_file[file_name]["chunk_count"] += 1
        
        # Convertir a lista
        document_list = list(documents_by_file.values())
        
        return {
            "total_documents": len(document_list),
            "total_chunks": points_count,
            "documents": document_list,
            "collection_name": qdrant_service.collection_name
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo metadatos de documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/langgraph-svg")
async def get_langgraph_svg():
    """
    Genera y devuelve una visualización SVG del grafo de LangGraph
    que se utiliza en el agente conversacional.
    
    Returns:
        Archivo SVG para visualizar el flujo del agente
    """
    try:
        # Definir nombre de archivo y rutas
        filename = "langgraph_workflow.svg"
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
        svg_path = os.path.join(static_dir, filename)
        
        # Crear directorio estático si no existe
        os.makedirs(static_dir, exist_ok=True)
        
        # Verificar si el archivo ya existe y no es demasiado antiguo (< 1 hora)
        cache_valid = False
        if os.path.exists(svg_path):
            file_age = time.time() - os.path.getmtime(svg_path)
            if file_age < 3600:  # 1 hora en segundos
                cache_valid = True
                logger.info(f"Usando archivo SVG cacheado: {svg_path}")
        
        # Si no existe o es muy antiguo, regenerarlo
        if not cache_valid:
            # Generar nuevo SVG con el agente
            try:
                agent = GemeloAgent()
                svg_path = agent.export_workflow_svg(filename)
                logger.info(f"Generado nuevo archivo SVG: {svg_path}")
            except Exception as e:
                # Si falla la generación pero existe un archivo anterior, usar ese
                if os.path.exists(svg_path):
                    logger.warning(f"Error generando SVG, usando versión cacheada: {str(e)}")
                else:
                    raise
        
        # Verificar que el archivo existe antes de devolverlo
        if not os.path.exists(svg_path):
            return JSONResponse(
                status_code=500, 
                content={"error": "No se pudo generar o encontrar el archivo SVG"})
        
        # Devolver el archivo como respuesta
        return FileResponse(
            path=svg_path,
            media_type="image/svg+xml",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"Error en endpoint langgraph-svg: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generando grafo LangGraph: {str(e)}"})
