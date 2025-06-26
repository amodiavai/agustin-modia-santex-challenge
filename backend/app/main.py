from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from dotenv import load_dotenv
import pathlib

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

# Ruta principal
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

# Crear directorio para archivos estáticos si no existe
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# Montar directorio de archivos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
