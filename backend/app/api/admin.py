from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, JSONResponse
from logging import getLogger
from typing import List, Dict, Any
import os
from pathlib import Path

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
        # Crear instancia del agente
        agent = GemeloAgent()
        
        # Exportar el grafo a SVG
        filename = "langgraph_workflow.svg"
        svg_path = agent.export_workflow_svg(filename)
        
        # Verificar si el archivo existe
        if not os.path.exists(svg_path):
            return JSONResponse(
                status_code=500,
                content={"error": f"No se pudo generar el archivo SVG: {svg_path}"})
        
        # Devolver el archivo como respuesta
        return FileResponse(
            path=svg_path,
            media_type="image/svg+xml",
            filename=filename
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generando grafo LangGraph: {str(e)}"})
