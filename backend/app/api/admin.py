from fastapi import APIRouter, Depends, HTTPException
from app.services.qdrant_service import QdrantService

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/reset_collection")
async def reset_collection():
    """
    Reinicia la colección en Qdrant (elimina y vuelve a crear)
    
    ADVERTENCIA: Este endpoint elimina todos los datos de la colección.
    """
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
