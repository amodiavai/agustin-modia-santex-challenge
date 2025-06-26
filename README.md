# Gemelo Digital - Proyecto Conversacional

Este proyecto implementa un gemelo digital conversacional que replica la personalidad y conocimientos de Agustín Modia, permitiendo subir documentos PDF para entrenar el modelo y mantener conversaciones contextualizadas. Utiliza un enfoque RAG (Retrieval-Augmented Generation) con una base de datos vectorial para proporcionar respuestas precisas y contextualizadas.

## Arquitectura

La aplicación está construida con la siguiente arquitectura:

```
Vue.js Frontend → FastAPI Backend → LangGraph Agent → Qdrant (vectores) + OpenAI API
```

### Inicialización Automática de Datos

Al iniciar por primera vez, el sistema verifica automáticamente la existencia del archivo CV (`Modia_Agustin_resume_gemelo_digital.pdf`) en la base de datos de vectores Qdrant. Si no está presente, procesa y vectoriza automáticamente este documento, que sirve como base de conocimiento fundamental para el gemelo digital.

## Tecnologías Utilizadas

- **Backend**: 
  - FastAPI para la API REST
  - LangGraph para el agente conversacional
  - PyPDF2 para procesamiento de documentos
  - Qdrant para base de datos vectorial
  - OpenAI API para embeddings y generación de texto

- **Frontend**:
  - Vue.js 3 para la interfaz de usuario
  - CSS personalizado con tema futurista teal/cyan
  - Axios para comunicación con la API

- **Servicios**:
  - Qdrant para almacenamiento de vectores
  - Docker y Docker Compose para containerización

- **Modelos de OpenAI**:
  - `text-embedding-3-large`: Para generación de embeddings con dimensión 3072
  - `gpt-4o-mini` (configurable): Para generación de respuestas

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

1. Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tu clave API de OpenAI y configuración personalizada:

```
# API Key de OpenAI
OPENAI_API_KEY=tu-clave-api-aqui

# Modelo de OpenAI a utilizar
OPENAI_MODEL=gpt-4o-mini

# Configuración de Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
COLLECTION_NAME=gemelo_agustin_large
```

## Iniciar la Aplicación

Para iniciar todos los servicios:

```bash
docker-compose up --build
```

En el primer inicio, el sistema:
1. Levanta los servicios de Qdrant, backend y frontend
2. Verifica la existencia del archivo `Modia_Agustin_resume_gemelo_digital.pdf` en la base de datos vectorial
3. Si no existe, procesa automáticamente el documento `backend/uploads/Modia_Agustin_resume_gemelo_digital.pdf`
4. Inicia la API del gemelo digital

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

### Gestión de Documentos / entrenamiento del gemelo

1. Navega a la pestaña "Entrenar Gemelo"
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

- **Embeddings**: El sistema utiliza `text-embedding-3-large` con dimensión 3072 para vectorizar documentos
  - Este modelo ofrece una representación vectorial de alta calidad para búsquedas semánticas precisas
  - La alta dimensionalidad (3072) permite capturar matices semánticos complejos

- **Modelo de Lenguaje**: Se utiliza `gpt-4o-mini` por defecto, pero es configurable via variable de entorno
  - Ofrece un buen balance entre calidad de respuestas y rendimiento

- **Procesamiento de documentos**:
  - Los PDFs se dividen en chunks optimizados para búsqueda semántica
  - Se mantienen metadatos para rastrear la fuente original

- **Inicialización automática**:
  - El CV de Agustín se procesa automáticamente al primer inicio
  - Garantiza que el gemelo digital siempre tiene la información base disponible

- **Interfaz de chat**:
  - Implementa streaming para respuestas en tiempo real
  - Diseño futurista con paleta de colores teal/cyan para mejor UX

- **Agente RAG**:
  - El agente LangGraph determina dinámicamente cuándo usar información de los documentos
  - Mantiene consistencia en las respuestas relacionadas con la información del CV

---

## Licencia

Este proyecto es privado y confidencial.
