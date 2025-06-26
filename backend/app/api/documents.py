from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import os
import uuid
import asyncio
from datetime import datetime
import shutil

from app.services.document_processor import DocumentProcessor
from app.services.embeddings_service import EmbeddingsService
from app.services.qdrant_service import QdrantService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# Modelos para respuestas
class DocumentInfo(BaseModel):
    id: str
    filename: str
    status: str
    created_at: str

class DocumentResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int

class DocumentStatus(BaseModel):
    status: str
    progress: float = 0.0
    message: str = ""

# Diccionario para almacenar estado de procesamiento de documentos
processing_status = {}

# Funciones para obtener servicios
async def get_document_processor():
    return DocumentProcessor()

async def get_embeddings_service():
    return EmbeddingsService()

async def get_qdrant_service():
    return QdrantService()

async def process_document_task(
    file_path: str, 
    document_id: str,
    document_processor: DocumentProcessor,
    embeddings_service: EmbeddingsService,
    qdrant_service: QdrantService
):
    """
    Tarea en segundo plano para procesar un documento
    """
    try:
        # Actualizar estado a "procesando"
        processing_status[document_id] = {
            "status": "processing",
            "progress": 0.1,
            "message": "Extrayendo texto del PDF..."
        }
        
        # Procesar documento
        documents = await document_processor.process_pdf(file_path)
        processing_status[document_id]["progress"] = 0.4
        processing_status[document_id]["message"] = "Generando embeddings..."
        
        # Generar embeddings
        documents_with_embeddings = await embeddings_service.process_documents(documents)
        processing_status[document_id]["progress"] = 0.7
        processing_status[document_id]["message"] = "Almacenando vectores en Qdrant..."
        
        # Inicializar colección si no existe
        await qdrant_service.initialize_collection()
        
        # Insertar documentos en Qdrant
        ids = await qdrant_service.insert_documents(documents_with_embeddings)
        
        # Actualizar estado a "completado"
        processing_status[document_id] = {
            "status": "completed",
            "progress": 1.0,
            "message": f"Procesamiento completado. Se indexaron {len(ids)} chunks."
        }
        
        logger.info(f"Documento {document_id} procesado exitosamente")
        
    except Exception as e:
        logger.error(f"Error procesando documento {document_id}: {str(e)}")
        processing_status[document_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_processor: DocumentProcessor = Depends(get_document_processor),
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    """
    Sube un documento PDF para procesamiento y vectorización
    """
    try:
        # Validar que sea un PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos PDF"
            )
            
        # Generar ID único para el documento
        document_id = str(uuid.uuid4())
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Sanitizar nombre de archivo 
        filename = file.filename.replace(" ", "_")
        
        # Guardar archivo
        file_path = document_processor.save_uploaded_file(file_content, filename)
        
        # Registrar estado inicial
        processing_status[document_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Documento en cola para procesamiento"
        }
        
        # Iniciar tarea en segundo plano
        background_tasks.add_task(
            process_document_task,
            file_path,
            document_id,
            document_processor,
            embeddings_service,
            qdrant_service
        )
        
        return {
            "document_id": document_id,
            "filename": filename,
            "status": "queued",
            "message": "Documento recibido y en cola para procesamiento"
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error subiendo documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el documento: {str(e)}"
        )

@router.get("/status/{document_id}", response_model=DocumentStatus)
async def get_document_status(document_id: str):
    """
    Obtiene el estado actual del procesamiento de un documento
    """
    if document_id not in processing_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
        
    return processing_status[document_id]

@router.get("/list")
async def list_documents(
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    """
    Lista todos los documentos procesados
    """
    try:
        # Obtener info de la colección
        collection_info = await qdrant_service.get_collection_info()
        
        # Esta es una implementación básica, en una versión real
        # necesitaríamos mantener una lista de documentos en una BD
        return {
            "total_documents": collection_info.get("count", 0),
            "collection_status": "active" if collection_info.get("exists", False) else "not_created",
            "collection_name": collection_info.get("name")
        }
        
    except Exception as e:
        logger.error(f"Error listando documentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo lista de documentos: {str(e)}"
        )

@router.get("/detail")
async def get_documents_detail(
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    """
    Obtiene una lista detallada de documentos con todos sus metadatos
    """
    try:
        if not await qdrant_service.collection_exists():
            return {"documents": [], "total": 0}
            
        # Realizar una búsqueda de todos los documentos con sus metadatos
        # scroll no es un método asíncrono, así que no usamos await
        results = qdrant_service.client.scroll(
            collection_name=qdrant_service.collection_name,
            limit=100,
            with_payload=True
        )
        
        # Extraer nombres de archivo únicos de los resultados
        unique_files = {}
        
        if results and results[0]:
            for point in results[0]:
                if "metadata" in point.payload and "file_name" in point.payload["metadata"]:
                    file_name = point.payload["metadata"]["file_name"]
                    
                    # Si este archivo ya está en nuestro diccionario, continuar
                    if file_name in unique_files:
                        continue
                        
                    # Agregar nuevo documento único
                    unique_files[file_name] = {
                        "id": str(point.id),
                        "filename": file_name,
                        "status": "completed",
                        "created_at": datetime.now().isoformat()
                    }
        
        # Convertir el diccionario en una lista
        documents = list(unique_files.values())
            
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles de documentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles de documentos: {str(e)}"
        )

@router.delete("/{document_name}")
async def delete_document(
    document_name: str,
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    """
    Elimina un documento por nombre
    """
    try:
        # Eliminar vectores del documento
        deleted_count = await qdrant_service.delete_by_filter({
            "file_name": document_name
        })
        
        if deleted_count == 0:
            return {
                "status": "warning",
                "message": f"No se encontraron vectores asociados al documento {document_name}"
            }
            
        return {
            "status": "success",
            "message": f"Documento {document_name} eliminado correctamente. Se eliminaron {deleted_count} vectores."
        }
        
    except Exception as e:
        logger.error(f"Error eliminando documento {document_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando documento: {str(e)}"
        )
