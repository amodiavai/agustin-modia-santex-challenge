from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from dotenv import load_dotenv

from app.api import chat, documents, admin, auth
from app.database import init_db

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gemelo-digital")

# Crear app FastAPI
app = FastAPI(
    title="Gemelo Digital API",
    description="API para el gemelo digital conversacional",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
init_db()

# Incluir routers
logger.info("🔐 Registrando rutas de autenticación...")
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
logger.info("💬 Registrando rutas de chat...")
app.include_router(chat.router, prefix="/api")
logger.info("📄 Registrando rutas de documentos...")
app.include_router(documents.router, prefix="/api")
logger.info("⚙️ Registrando rutas de admin...")
app.include_router(admin.router, prefix="/api")
logger.info("✅ Todas las rutas registradas correctamente")

# Configurar archivos estáticos para el frontend (solo si existe el directorio)
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    app.mount("/static", StaticFiles(directory=frontend_dist_path), name="static")
    logger.info(f"📁 Sirviendo archivos estáticos desde: {frontend_dist_path}")
    
    # Servir el frontend en la ruta raíz
    @app.get("/")
    async def serve_frontend():
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {
                "message": "Gemelo Digital API",
                "status": "online",
                "version": "1.0.0",
                "note": "Frontend no encontrado, solo API disponible"
            }
    
    # Manejar rutas del frontend (SPA routing)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Si es una ruta de API, dejar que FastAPI la maneje
        if path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        # Para todas las demás rutas, servir index.html (SPA routing)
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"error": "Frontend not found"}
else:
    # Si no hay frontend, servir solo la API
    @app.get("/")
    async def root():
        return {
            "message": "Gemelo Digital API",
            "status": "online",
            "version": "1.0.0",
        }

# Ruta de health check
@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
