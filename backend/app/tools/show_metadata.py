#!/usr/bin/env python
"""
Script para mostrar metadatos de documentos almacenados en Qdrant
"""
import asyncio
import os
import sys
import json
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.qdrant_service import QdrantService

async def show_document_metadata():
    """
    Muestra los metadatos de todos los documentos almacenados en Qdrant
    """
    try:
        # Crear instancia de QdrantService
        qdrant_service = QdrantService()
        
        print(f"Conectando a Qdrant ({qdrant_service.host}:{qdrant_service.port})...")
        print(f"Colección: {qdrant_service.collection_name}")
        
        # Obtener información de la colección
        collection_info = await qdrant_service.get_collection_info()
        if not collection_info.get("exists", False):
            print(f"La colección {qdrant_service.collection_name} no existe")
            return
            
        points_count = collection_info.get("points_count", 0)
        print(f"Total de chunks en la colección: {points_count}")
        
        if points_count == 0:
            print("No hay documentos en la colección")
            return
            
        # Buscar todos los documentos (con vector vacío y umbral 0)
        print("Obteniendo metadatos de documentos...")
        search_results = await qdrant_service.search(
            query_vector=[0.0] * qdrant_service.vector_size,
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
        
        # Mostrar resultados
        print(f"\nTotal de documentos: {len(documents_by_file)}")
        print("=" * 60)
        
        for doc_name, doc_info in documents_by_file.items():
            print(f"\nDOCUMENTO: {doc_info['file_name']}")
            print(f"Tipo: {doc_info['document_type']}")
            print(f"Chunks: {doc_info['chunk_count']}")
            print(f"Resumen: {doc_info['document_summary']}")
            print("-" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(show_document_metadata())
