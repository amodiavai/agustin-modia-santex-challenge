import os
import logging
from typing import List, Dict, Any
from PyPDF2 import PdfReader
import re
import textwrap

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa el procesador de documentos PDF
        
        Args:
            chunk_size: Tamaño de los chunks en cantidad de tokens aproximada
            chunk_overlap: Overlap entre chunks para mantener contexto
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        
        # Crear directorio de uploads si no existe
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    async def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Procesa un archivo PDF y extrae su contenido en chunks
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Lista de diccionarios con el texto y metadatos de cada chunk
        """
        try:
            logger.info(f"Procesando archivo PDF: {file_path}")
            
            # Validar que el archivo exista
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"El archivo {file_path} no existe")
            
            # Validar que sea un PDF
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"El archivo {file_path} no es un PDF")
            
            # Extraer el texto del PDF
            extracted_text = self._extract_text_from_pdf(file_path)
            
            # Obtener nombre del archivo sin extensión
            file_name = os.path.basename(file_path).replace('.pdf', '')
            
            # Generar un resumen del documento
            document_summary = self._generate_document_summary(extracted_text)
            logger.info(f"Resumen generado para {file_name}: {document_summary[:100]}...")
            
            # Dividir el texto en chunks
            text_chunks = self._create_chunks(extracted_text)
            
            # Crear documentos con metadatos
            documents = []
            for i, chunk in enumerate(text_chunks):
                # Crear documento con metadatos
                doc = {
                    "text": chunk,
                    "metadata": {
                        "source": file_path,
                        "file_name": file_name,
                        "chunk_id": i,
                        "chunk_size": len(chunk),
                        "document_summary": document_summary,
                        "document_type": "resume" if "resume" in file_name.lower() or "cv" in file_name.lower() else "general"
                    }
                }
                documents.append(doc)
            
            logger.info(f"Procesamiento completo. Se generaron {len(documents)} chunks")
            return documents
        
        except Exception as e:
            logger.error(f"Error procesando PDF {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """
        Extrae el texto de un PDF por páginas
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Lista de strings con el texto de cada página
        """
        text_by_page = []
        
        with open(file_path, 'rb') as f:
            pdf = PdfReader(f)
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                # Solo agregar si hay texto en la página
                if text and text.strip():
                    text_by_page.append({
                        "content": text,
                        "page": i + 1
                    })
        
        return text_by_page
    
    def _create_chunks(self, text_by_page: List[Dict[str, Any]]) -> List[str]:
        """
        Divide el texto en chunks manteniendo la integridad de párrafos
        
        Args:
            text_by_page: Lista de diccionarios con el texto y número de página
            
        Returns:
            Lista de strings con los chunks de texto
        """
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for page_info in text_by_page:
            text = page_info["content"]
            page = page_info["page"]
            
            # Aproximación simple - dividir por párrafos
            paragraphs = text.split('\n\n')
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                    
                # Estimación de tokens (aproximado: 4 caracteres = 1 token)
                paragraph_size = len(paragraph) / 4
                
                # Si el párrafo solo no excede el tamaño del chunk y el chunk actual está vacío
                if paragraph_size <= self.chunk_size and current_size == 0:
                    current_chunk = f"[Page {page}] {paragraph}"
                    current_size = paragraph_size
                    
                # Si agregar el párrafo excedería el tamaño del chunk
                elif current_size + paragraph_size > self.chunk_size and current_chunk:
                    chunks.append(current_chunk)
                    
                    # Comenzar nuevo chunk con este párrafo
                    current_chunk = f"[Page {page}] {paragraph}"
                    current_size = paragraph_size
                    
                # Si el párrafo cabe en el chunk actual
                else:
                    current_chunk += f"\n\n[Page {page}] {paragraph}"
                    current_size += paragraph_size
                    
                    # Si el chunk actual está cerca del límite, cerrarlo
                    if current_size >= self.chunk_size * 0.9:
                        chunks.append(current_chunk)
                        current_chunk = ""
                        current_size = 0
        
        # Agregar el último chunk si quedó algo
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
        
    def _generate_document_summary(self, text_by_page: List[Dict[str, Any]]) -> str:
        """
        Genera un resumen breve del documento basado en las primeras páginas
        
        Args:
            text_by_page: Lista de diccionarios con el texto y número de página
            
        Returns:
            String con un resumen del documento (máximo 500 caracteres)
        """
        try:
            # Extraer texto de las primeras dos páginas o todas si hay menos
            intro_text = ""
            for i, page_info in enumerate(text_by_page):
                if i < 2:  # Solo primeras dos páginas
                    intro_text += page_info["content"] + "\n"
                else:
                    break
            
            # Limpiar y normalizar el texto
            intro_text = re.sub(r'\s+', ' ', intro_text).strip()
            
            # Tomar las primeras 1000 caracteres para el resumen
            if len(intro_text) > 1000:
                intro_text = intro_text[:1000]
            
            # Formatear como un resumen conciso (máximo 500 caracteres)
            words = intro_text.split()
            summary_words = words[:100]  # Aproximadamente 500 caracteres
            summary = ' '.join(summary_words)
            
            # Asegurar que no exceda 500 caracteres
            if len(summary) > 500:
                summary = textwrap.shorten(summary, width=500, placeholder="...")
                
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen del documento: {str(e)}")
            return "No fue posible generar un resumen para este documento."
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Guarda un archivo subido en el directorio de uploads
        
        Args:
            file_content: Contenido binario del archivo
            filename: Nombre del archivo
            
        Returns:
            Ruta donde se guardó el archivo
        """
        # Sanitizar nombre de archivo
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ruta completa del archivo
        file_path = os.path.join(self.uploads_dir, filename)
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Archivo guardado en {file_path}")
        return file_path
