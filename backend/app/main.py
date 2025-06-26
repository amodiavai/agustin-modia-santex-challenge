from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

from app.api import chat, documents, admin

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

# Incluir routers
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(admin.router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
