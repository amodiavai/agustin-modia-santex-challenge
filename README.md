# Gemelo Digital - Proyecto Conversacional

Este proyecto implementa un gemelo digital conversacional que replica la personalidad y conocimientos de Agustín Modia, permitiendo subir documentos PDF para entrenar el modelo y mantener conversaciones contextualizadas.

## Arquitectura

La aplicación está construida con la siguiente arquitectura:

```
Vue.js Frontend → FastAPI Backend → LangGraph Agent → Qdrant (vectores) + OpenAI API
```

## Tecnologías Utilizadas

- **Backend**: 
  - FastAPI para la API REST
  - LangGraph para el agente conversacional
  - PyPDF2 para procesamiento de documentos
  - Qdrant para base de datos vectorial
  - OpenAI API para embeddings y generación de texto

- **Frontend**:
  - Vue.js 3 para la interfaz de usuario
  - CSS personalizado para el diseño
  - Axios para comunicación con la API

- **Servicios**:
  - Qdrant para almacenamiento de vectores
  - Docker y Docker Compose para containerización

## Características Principales

- **Chat Conversacional**: Interacción en tiempo real con streaming de respuestas
- **Procesamiento de Documentos**: Subida y procesamiento de PDFs
- **Búsqueda Semántica**: Recuperación de información relevante
- **Personalización**: Sistema de prompts separado para fácil ajuste
- **Dockerización**: Despliegue sencillo con Docker Compose

## Estructura del Proyecto

```
gemelo-digital/
├── docker-compose.yml          # Orquestación de servicios
├── backend/                    # API FastAPI + LangGraph
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/                # Endpoints
│   │   ├── services/           # Servicios
│   │   ├── agents/             # Agentes LangGraph  
│   │   └── prompts/            # Sistema de prompts
│   └── uploads/                # Almacenamiento de PDFs
└── frontend/                   # Interfaz Vue.js
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── components/
    │   ├── services/
    │   └── assets/
    └── public/
```

## Requisitos Previos

- Docker y Docker Compose
- Clave API de OpenAI

## Configuración

1. Crea un archivo `.env` en el directorio raíz con tu clave API de OpenAI:

```
OPENAI_API_KEY=tu_clave_api_aquí
```

## Iniciar la Aplicación

Para iniciar todos los servicios:

```bash
docker-compose up --build
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- API Backend: http://localhost:8000
- Qdrant Dashboard: http://localhost:6333/dashboard

## Sistema de Prompts

Los prompts del sistema se encuentran en archivos individuales en `backend/app/prompts/` para facilitar su modificación:

- `system.txt`: Personalidad principal del gemelo digital
- `classify.txt`: Clasificación de consultas para determinar si necesitan RAG
- `router.txt`: Enrutamiento de consultas
- `rag.txt`: Generación de respuestas con contexto

## Uso de la Aplicación

### Chat Conversacional

1. Navega a la pestaña "Chat"
2. Escribe tu mensaje y envíalo
3. El gemelo digital responderá en tiempo real
4. Las fuentes utilizadas se mostrarán debajo de la respuesta

### Gestión de Documentos

1. Navega a la pestaña "Documentos"
2. Sube archivos PDF mediante la interfaz de arrastrar y soltar
3. Monitorea el progreso del procesamiento
4. Consulta y gestiona los documentos subidos

## Desarrollo

Para desarrollo local sin Docker:

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notas Técnicas

- El sistema utiliza OpenAI GPT-4o-mini para las respuestas y text-embedding-3-small para los embeddings
- El procesamiento de documentos divide los PDFs en chunks optimizados para búsqueda semántica
- La interfaz de chat implementa un sistema de streaming para respuestas en tiempo real
- El agente LangGraph determina dinámicamente cuándo usar información de los documentos

---

## Consideraciones Futuras

- Agregar sistema de autenticación
- Implementar almacenamiento persistente para historial de chat
- Añadir más tipos de documentos (no solo PDF)
- Mejorar el procesamiento de documentos con OCR para PDFs escaneados

## Licencia

Este proyecto es privado y confidencial.
