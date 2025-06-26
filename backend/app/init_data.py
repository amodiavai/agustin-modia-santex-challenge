import asyncio
import logging
import os
import sys
from pathlib import Path

# Asegurarse de que el módulo app pueda ser importado
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.qdrant_service import QdrantService
from app.services.document_processor import DocumentProcessor
from app.services.embeddings_service import EmbeddingsService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("init-data")

# Nombre del archivo a verificar
TARGET_DOCUMENT = "Modia_Agustin_resume_gemelo_digital.pdf"

async def document_exists_in_qdrant(qdrant_service, filename):
    """Verifica si un documento específico existe en la base de datos Qdrant"""
    try:
        # Verificar si la colección existe
        if not await qdrant_service.collection_exists():
            logger.info("La colección de Qdrant no existe todavía")
            return False
        
        # Buscar documentos que coincidan con el nombre del archivo
        search_results = await qdrant_service.get_documents_by_filename(filename)
        
        # Si hay resultados, el documento existe
        exists = len(search_results) > 0
        if exists:
            logger.info(f"Documento '{filename}' encontrado en Qdrant con {len(search_results)} chunks")
        else:
            logger.info(f"Documento '{filename}' no encontrado en Qdrant")
        
        return exists
    except Exception as e:
        logger.error(f"Error verificando existencia de documento: {str(e)}")
        return False

async def process_document(file_path):
    """Procesa un documento y lo guarda en Qdrant"""
    try:
        logger.info(f"Procesando documento: {file_path}")
        
        # Inicializar servicios
        document_processor = DocumentProcessor()
        embeddings_service = EmbeddingsService()
        qdrant_service = QdrantService()
        
        # Procesar documento
        logger.info("Extrayendo texto del PDF...")
        documents = await document_processor.process_pdf(file_path)
        
        # Generar embeddings
        logger.info("Generando embeddings...")
        documents_with_embeddings = await embeddings_service.process_documents(documents)
        
        # Inicializar colección si no existe
        logger.info("Inicializando colección en Qdrant...")
        await qdrant_service.initialize_collection()
        
        # Insertar documentos en Qdrant
        logger.info("Almacenando vectores en Qdrant...")
        ids = await qdrant_service.insert_documents(documents_with_embeddings)
        
        logger.info(f"✅ Documento procesado exitosamente. Se indexaron {len(ids)} chunks.")
        return True
    except Exception as e:
        logger.error(f"❌ Error procesando documento: {str(e)}")
        return False

async def init_data():
    """Función principal de inicialización"""
    try:
        logger.info("🚀 Iniciando verificación de datos iniciales...")
        
        # Inicializar servicio de Qdrant para verificar el documento
        qdrant_service = QdrantService()
        
        # Esperar a que Qdrant esté disponible
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                await qdrant_service.get_collection_info()
                break
            except Exception as e:
                retry_count += 1
                logger.warning(f"Esperando a que Qdrant esté disponible (intento {retry_count}/{max_retries}): {str(e)}")
                await asyncio.sleep(5)
        
        if retry_count == max_retries:
            logger.error("Qdrant no está disponible después de varios intentos")
            return
        
        # Ruta al documento
        upload_dir = Path("uploads")
        document_path = upload_dir / TARGET_DOCUMENT
        
        # Verificar si el archivo existe físicamente
        if not document_path.exists():
            logger.warning(f"El documento {TARGET_DOCUMENT} no existe en el directorio de uploads")
            return
        
        # Verificar si el documento ya está en Qdrant
        if not await document_exists_in_qdrant(qdrant_service, TARGET_DOCUMENT):
            logger.info(f"El documento {TARGET_DOCUMENT} no existe en Qdrant, procesando...")
            # Procesar el documento
            success = await process_document(str(document_path))
            if success:
                logger.info(f"✅ Documento {TARGET_DOCUMENT} inicializado correctamente")
            else:
                logger.error(f"❌ Falló la inicialización del documento {TARGET_DOCUMENT}")
        else:
            logger.info(f"✅ El documento {TARGET_DOCUMENT} ya existe en Qdrant, no es necesario procesarlo de nuevo")
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización de datos: {str(e)}")

if __name__ == "__main__":
    asyncio.run(init_data())
