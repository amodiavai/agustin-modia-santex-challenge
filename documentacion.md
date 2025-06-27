# Gemelo Digital - Documentación Técnica Completa

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Frontend (Vue.js 3)](#frontend-vuejs-3)
6. [Backend (FastAPI)](#backend-fastapi)
7. [Sistema de Agentes LangGraph](#sistema-de-agentes-langgraph)
8. [Base de Datos](#base-de-datos)
9. [Microservicios Docker](#microservicios-docker)
10. [API Endpoints](#api-endpoints)
11. [Sistema de Autenticación](#sistema-de-autenticación)
12. [Procesamiento de Documentos](#procesamiento-de-documentos)
13. [Base de Datos Vectorial](#base-de-datos-vectorial)
14. [Variables de Entorno](#variables-de-entorno)
15. [Despliegue y Configuración](#despliegue-y-configuración)

---

## 🚀 Descripción General

**Gemelo Digital** es una aplicación conversacional de IA que crea un gemelo digital de "Agustín Modia" con capacidades de carga de documentos para conversaciones contextualizadas. Desarrollado para el Santex Challenge.

### Características Principales
- 🤖 **Gemelo Digital IA**: Conversación personalizada como Agustín Modia
- 📄 **Procesamiento de Documentos**: Carga y análisis de PDFs
- 🔍 **Búsqueda Semántica**: RAG (Retrieval-Augmented Generation)
- 💬 **Chat en Tiempo Real**: Streaming de respuestas
- 🔐 **Autenticación JWT**: Sistema de login seguro
- 📊 **Visualización de Flujos**: Diagrama LangGraph interactivo

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Frontend      │    │     Backend      │    │   Bases de Datos   │
│   (Vue.js 3)    │◄──►│   (FastAPI)      │◄──►│                     │
│   Puerto: 3000  │    │   Puerto: 8000   │    │ PostgreSQL: 5432    │
└─────────────────┘    └──────────────────┘    │ Qdrant: 6333        │
                                               └─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   LangGraph      │
                    │   Agent          │
                    │   (OpenAI API)   │
                    └──────────────────┘
```

### Flujo de Datos
1. **Usuario** → Frontend (Vue.js)
2. **Frontend** → Backend API (FastAPI)
3. **Backend** → LangGraph Agent
4. **Agent** → Qdrant (búsqueda vectorial) + PostgreSQL (historial)
5. **Agent** → OpenAI API (LLM + embeddings)
6. **Respuesta** ← Streaming hacia el usuario

---

## 🔧 Stack Tecnológico

### Frontend
- **Vue.js 3** - Framework progresivo
- **Vite** - Build tool y dev server
- **Axios** - Cliente HTTP
- **Marked** - Renderizado Markdown
- **Highlight.js** - Syntax highlighting

### Backend
- **FastAPI** - Framework web async
- **SQLAlchemy** - ORM para PostgreSQL
- **LangChain/LangGraph** - Orquestación de agentes
- **OpenAI API** - LLM (gpt-4o-mini) + embeddings
- **PyPDF2** - Procesamiento de PDFs
- **python-jose** - JWT authentication

### Bases de Datos
- **PostgreSQL 15** - Base de datos relacional
- **Qdrant** - Base de datos vectorial

### DevOps
- **Docker & Docker Compose** - Containerización
- **Nginx** (en producción) - Reverse proxy
- **Linux** - Sistema operativo

---

## 📁 Estructura del Proyecto

```
gemelo-digital/
├── 📄 docker-compose.yml          # Orquestación de contenedores
├── 📄 .env                        # Variables de entorno
├── 📄 CLAUDE.md                   # Instrucciones para Claude Code
├── 📄 documentacion.md            # Esta documentación
├── 📁 frontend/                   # Aplicación Vue.js
│   ├── 📄 Dockerfile              # Imagen del frontend
│   ├── 📄 package.json            # Dependencias NPM
│   ├── 📄 vite.config.js          # Configuración Vite
│   └── 📁 src/
│       ├── 📄 App.vue             # Componente raíz
│       ├── 📄 main.js             # Punto de entrada
│       ├── 📁 components/         # Componentes Vue
│       │   ├── 📄 ChatInterface.vue     # Chat principal
│       │   ├── 📄 DocumentManager.vue   # Gestor de documentos
│       │   ├── 📄 DocumentUpload.vue    # Carga de archivos
│       │   └── 📄 LoginForm.vue         # Formulario de login
│       ├── 📁 services/
│       │   └── 📄 api.js          # Cliente API
│       └── 📁 assets/
│           └── 📄 main.css        # Estilos globales
├── 📁 backend/                    # Aplicación FastAPI
│   ├── 📄 Dockerfile              # Imagen del backend
│   ├── 📄 requirements.txt        # Dependencias Python
│   ├── 📁 uploads/                # Archivos subidos
│   ├── 📁 static/                 # Archivos estáticos
│   └── 📁 app/
│       ├── 📄 main.py             # Aplicación FastAPI
│       ├── 📄 database.py         # Configuración PostgreSQL
│       ├── 📁 api/                # Endpoints REST
│       │   ├── 📄 auth.py         # Autenticación
│       │   ├── 📄 chat.py         # Chat endpoints
│       │   ├── 📄 documents.py    # Gestión documentos
│       │   └── 📄 admin.py        # Utilidades admin
│       ├── 📁 agents/             # Sistema LangGraph
│       │   └── 📄 gemelo_agent.py # Agente conversacional
│       ├── 📁 services/           # Lógica de negocio
│       │   ├── 📄 auth_service.py       # Autenticación JWT
│       │   ├── 📄 chat_service.py       # Orquestación chat
│       │   ├── 📄 chat_history_service.py # Persistencia chat
│       │   ├── 📄 document_processor.py  # Procesamiento PDFs
│       │   ├── 📄 embeddings_service.py  # Embeddings OpenAI
│       │   └── 📄 qdrant_service.py      # Base datos vectorial
│       └── 📁 prompts/            # Templates de prompts
│           ├── 📄 system.txt      # Personalidad del agente
│           ├── 📄 classify.txt    # Clasificación de queries
│           ├── 📄 rag.txt         # Generación con RAG
│           └── 📄 router.txt      # Decisiones de routing
```

---

## 🎨 Frontend (Vue.js 3)

### Arquitectura de Componentes

```
App.vue (Raíz)
├── LoginForm.vue          # Autenticación JWT
├── ChatInterface.vue      # Chat con streaming
├── DocumentUpload.vue     # Carga con progreso
└── DocumentManager.vue    # Lista y gestión
```

### Componentes Principales

#### **App.vue** - Componente Raíz
- **Funciones**: Navegación, autenticación, modal del grafo
- **Estados**: Tab activo, autenticación, modal del workflow
- **Características**:
  - Sistema de tabs (Chat, Entrenar Gemelo)
  - Botón "Grafo" para visualizar LangGraph
  - Modal con SVG del flujo del agente
  - Logout con limpieza de token

#### **ChatInterface.vue** - Interfaz de Chat
- **Funciones**: Conversación en tiempo real con streaming
- **Características**:
  - Server-Sent Events (SSE) para streaming
  - Renderizado Markdown con highlight.js
  - Auto-scroll y gestión de historial
  - Indicador de escritura
  - Manejo de errores de conexión

#### **DocumentUpload.vue** - Carga de Documentos
- **Funciones**: Upload de PDFs con feedback visual
- **Características**:
  - Drag & drop interface
  - Barra de progreso en tiempo real
  - Validación de tipo de archivo
  - Feedback de éxito/error
  - Integración con FormData

#### **DocumentManager.vue** - Gestión de Documentos
- **Funciones**: Lista y administración de documentos
- **Características**:
  - Lista de documentos con metadata
  - Información de chunks y tipo
  - Eliminación de documentos
  - Estado de carga y error

### Servicios Frontend

#### **api.js** - Cliente API
```javascript
// Servicios disponibles
authService: {
  login()           // Autenticación JWT
  logout()          // Limpiar sesión
  isAuthenticated() // Verificar estado
  getToken()        // Obtener token
}

chatService: {
  sendMessage()     // Envío no-streaming
  getStreamUrl()    // URL para SSE
  getHistory()      // Historial de chat
  clearHistory()    // Limpiar historial
}

documentService: {
  uploadDocument()  // Subir PDF
  listDocuments()   // Listar documentos
  deleteDocument()  // Eliminar documento
}
```

### Styling y UX
- **Dark Theme**: Esquema de colores oscuro con acentos cyan
- **Responsive**: Mobile-first design
- **Animaciones**: Transiciones suaves y feedback visual
- **Gradientes**: Efectos visuales modernos
- **Typography**: Fuentes optimizadas para legibilidad

---

## 🚀 Backend (FastAPI)

### Arquitectura de Microservicios

```
FastAPI App
├── API Routes          # Endpoints REST
├── Services Layer      # Lógica de negocio
├── Database Layer      # PostgreSQL + Qdrant
└── LangGraph Agent     # IA Conversacional
```

### API Routes

#### **auth.py** - Autenticación
```python
POST /api/auth/login     # Login con JWT
GET  /api/auth/verify    # Verificar token
GET  /api/auth/test      # Health check
```

#### **chat.py** - Conversación
```python
POST /api/chat/send      # Mensaje no-streaming
POST /api/chat/stream    # Mensaje con streaming  
GET  /api/chat/history   # Obtener historial
DELETE /api/chat/history # Limpiar historial
```

#### **documents.py** - Documentos
```python
POST /api/documents/upload        # Subir PDF
GET  /api/documents/status/{id}   # Estado procesamiento
GET  /api/documents/list          # Listar documentos
GET  /api/documents/detail        # Metadata detallada
DELETE /api/documents/{filename}  # Eliminar documento
```

#### **admin.py** - Administración
```python
POST /api/admin/reset_collection  # Resetear Qdrant
GET  /api/admin/metadata         # Metadata documentos
GET  /api/admin/langgraph-svg    # Visualización workflow
```

### Servicios Backend

#### **auth_service.py** - Autenticación JWT
- **Funciones**: Generación/validación tokens, hashing passwords
- **Seguridad**: HS256, expiración configurable, refresh automático

#### **chat_service.py** - Orquestación de Chat
- **Funciones**: Coordinar agente, historial, streaming
- **Integración**: LangGraph agent + PostgreSQL + SSE

#### **chat_history_service.py** - Persistencia Chat
- **Base de Datos**: PostgreSQL con SQLAlchemy
- **Operaciones**: CRUD messages, paginación, filtros por sesión

#### **document_processor.py** - Procesamiento PDFs
- **Pipeline**: PDF → Texto → Chunks → Embeddings → Qdrant
- **Chunking**: Estrategia inteligente con overlap
- **Metadata**: Extracción automática de información

#### **embeddings_service.py** - Embeddings OpenAI
- **Modelo**: text-embedding-3-large (3072 dimensiones)
- **Optimización**: Batch processing, rate limiting
- **Cache**: Gestión de embeddings duplicados

#### **qdrant_service.py** - Base de Datos Vectorial
- **Operaciones**: CRUD vectores, búsqueda semántica
- **Optimización**: Indexing metadata, filtros eficientes
- **Gestión**: Collections, health checks, statistics

---

## 🧠 Sistema de Agentes LangGraph

### Arquitectura del Agente

```python
class AgentState(TypedDict):
    messages: List[Dict[str, str]]     # Historial conversación
    query: str                         # Input del usuario
    history: List[Dict[str, str]]      # Contexto chat
    needs_rag: bool                    # Flag de RAG requerido
    context: List[str]                 # Documentos recuperados
    sources: List[Dict[str, Any]]      # Metadata de fuentes
    thought_process: str               # Proceso de razonamiento
    response: str                      # Respuesta generada
    has_relevant_data: bool            # Flag de datos relevantes
```

### Flujo del Workflow

```
┌─────────┐
│  START  │
└────┬────┘
     ▼
┌──────────────────┐
│ search_knowledge │  ← Siempre busca en vectores
└────────┬─────────┘
         ▼
    ┌──────────┐
    │ ¿Datos   │
    │relevantes?│
    └─────┬────┘
          ▼
     ┌────────────────────────┐
     ▼                        ▼
┌──────────────────┐  ┌─────────────────┐
│ generate_response│  │ no_data_response│
│ (Con RAG)        │  │ (Sin info)      │
└─────────┬────────┘  └────────┬────────┘
          ▼                     ▼
         ┌─────────────────────────┐
         │         END             │
         └─────────────────────────┘
```

### Estados del Agente

#### **search_knowledge** - Búsqueda en Base de Conocimientos
```python
async def _search_knowledge(self, state: AgentState) -> AgentState:
    # 1. Generar embeddings de la query
    # 2. Búsqueda vectorial en Qdrant
    # 3. Priorizar documentos CV/resume
    # 4. Filtrar por score de relevancia (>0.2)
    # 5. Actualizar estado con contexto
```

#### **generate_response** - Generación con RAG
```python
async def _generate_response(self, state: AgentState) -> AgentState:
    # 1. Construir prompt con contexto RAG
    # 2. Incluir historial conversacional
    # 3. Generar respuesta con OpenAI
    # 4. Aplicar personalidad de Agustín Modia
```

#### **no_data_response** - Respuesta Sin Datos
```python
async def _no_data_response(self, state: AgentState) -> AgentState:
    # Mensaje estándar cuando no hay información suficiente
    return "Soy el gemelo de Agustín Modia. No tengo datos 
            suficientes para responder esa consulta."
```

### Características del Agente

#### **Always-RAG Architecture**
- **Estrategia**: Toda consulta busca en la base de conocimientos
- **Beneficios**: Máxima utilización de información disponible
- **Fallback**: Respuesta estándar cuando no hay datos relevantes

#### **Streaming Support**
- **Implementación**: AsyncGenerator con SSE
- **Performance**: Respuestas en tiempo real
- **UX**: Mejor experiencia de usuario

#### **Context Management**
- **Historial**: Últimos 5 mensajes para contexto
- **Sesiones**: Agrupación por usuario
- **Memoria**: Persistencia en PostgreSQL

#### **Personalidad Configurable**
- **Prompts Modulares**: system.txt, rag.txt, classify.txt
- **Personalidad**: Gemelo digital de Agustín Modia
- **Adaptabilidad**: Prompts editables sin redeployment

---

## 🗄️ Base de Datos

### PostgreSQL - Base de Datos Relacional

#### **Esquema de Tablas**
```sql
-- Tabla de mensajes de chat
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR DEFAULT 'default'
);

-- Índices para optimización
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
```

#### **Operaciones CRUD**
```python
# Chat History Service
save_chat_message()           # Guardar conversación
get_chat_history()           # Obtener historial con paginación  
get_recent_messages_for_context()  # Contexto conversacional
clear_chat_history()         # Limpiar historial por sesión
```

#### **Configuración de Conexión**
```python
# database.py
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Qdrant - Base de Datos Vectorial

#### **Configuración de Collection**
```python
# Colección: gemelo_agustin_large
vector_size = 3072  # text-embedding-3-large
distance = "Cosine"  # Métrica de similitud
```

#### **Estructura de Documentos**
```json
{
  "vector": [3072 dimensiones],
  "payload": {
    "text": "Contenido del chunk",
    "metadata": {
      "source": "/path/to/document.pdf",
      "file_name": "documento.pdf",
      "chunk_id": 0,
      "chunk_size": 1000,
      "document_summary": "Resumen del documento",
      "document_type": "resume|general",
      "page_number": 1
    }
  }
}
```

#### **Operaciones Vectoriales**
```python
# Qdrant Service
initialize_collection()      # Crear colección con schema
search()                    # Búsqueda de similitud
add_vectors()              # Insertar vectores con metadata
delete_by_filter()         # Eliminar por filtros
get_collection_info()      # Estadísticas de colección
```

---

## 🐳 Microservicios Docker

### Docker Compose Architecture

```yaml
version: '3.8'

services:
  # Base de datos PostgreSQL
  postgres:
    image: postgres:15-alpine
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: gemelo_digital
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d gemelo_digital"]
    
  # Base de datos vectorial Qdrant  
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes: [qdrant_data:/qdrant/storage]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      
  # Backend FastAPI
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: 
      - ./backend:/app
      - uploads_data:/app/uploads
    depends_on: [postgres, qdrant]
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
  # Frontend Vue.js
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on: [backend]
    command: ["npm", "run", "dev", "--", "--host"]

# Volúmenes persistentes
volumes:
  postgres_data: {}
  qdrant_data: {}
  uploads_data: {}

# Red compartida
networks:
  gemelo_network:
    driver: bridge
```

### Puertos y Servicios

| Servicio | Puerto | Propósito | Health Check |
|----------|--------|-----------|--------------|
| **Frontend** | 3000 | Aplicación Vue.js | HTTP 200 |
| **Backend** | 8000 | API FastAPI | /docs endpoint |
| **PostgreSQL** | 5432 | Base datos relacional | pg_isready |
| **Qdrant** | 6333/6334 | Base datos vectorial | /healthz |

### Volúmenes Persistentes

- **postgres_data**: Datos PostgreSQL persistentes
- **qdrant_data**: Índices y vectores Qdrant
- **uploads_data**: Documentos PDF subidos

### Dependencias de Servicios

```
frontend → backend → postgres + qdrant
```

### Health Checks y Restart Policies

- **Monitoring**: Health checks automáticos cada 30s
- **Recovery**: Auto-restart en caso de falla
- **Dependencies**: Inicio ordenado con wait conditions

---

## 🔐 Sistema de Autenticación

### JWT Implementation

#### **Configuración**
```python
# Auth Service
ALGORITHM = "HS256"
SECRET_KEY = "tu-clave-secreta-super-segura"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

#### **Flow de Autenticación**
1. **Login**: Usuario/contraseña → JWT token
2. **Storage**: Token en localStorage del frontend  
3. **Requests**: Bearer token en Authorization header
4. **Validation**: Verificación automática en endpoints protegidos
5. **Refresh**: Re-autenticación cuando token expira

#### **Endpoints de Autenticación**
```python
@router.post("/login")
async def login(credentials: UserCredentials):
    # 1. Validar credenciales contra ENV vars
    # 2. Generar JWT token con expiración
    # 3. Retornar access_token y tipo
    
@router.get("/verify") 
async def verify_token(current_user: dict = Depends(get_current_user)):
    # Validar token JWT y retornar info usuario
```

#### **Middleware de Seguridad**
```python
# Dependency injection para rutas protegidas
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 1. Extraer token del header Authorization
    # 2. Validar firma JWT con SECRET_KEY
    # 3. Verificar expiración
    # 4. Retornar claims del usuario
```

### Frontend Security

#### **Token Management**
```javascript
// API interceptors para token automático
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-logout en 401
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### Credenciales por Defecto

```bash
# Usuario administrador (configurable vía ENV)
ADMIN_USER=admin-gd
ADMIN_PASSWORD=Pasado_por_mail
```

---

## 📄 Procesamiento de Documentos

### Pipeline de Procesamiento

```
PDF Upload → Validation → Text Extraction → Chunking → Embeddings → Vector Storage
```

#### **1. Upload y Validación**
```python
@router.post("/upload")
async def upload_document(file: UploadFile):
    # 1. Validar tipo MIME (application/pdf)
    # 2. Verificar tamaño máximo
    # 3. Generar nombre único
    # 4. Guardar en /uploads
```

#### **2. Extracción de Texto**
```python
# document_processor.py
def extract_text_from_pdf(file_path: str) -> List[Dict]:
    # 1. Abrir PDF con PyPDF2
    # 2. Extraer texto página por página
    # 3. Limpiar y normalizar texto
    # 4. Mantener referencia de página
```

#### **3. Chunking Inteligente**
```python
def create_chunks(text: str, chunk_size: int = 4000, overlap: int = 800):
    # Estrategia de chunking:
    # - Tamaño base: ~1000 tokens (4000 chars)
    # - Overlap: 200 tokens para contexto
    # - Respeto límites de párrafo
    # - Preservación de contexto semántico
```

#### **4. Generación de Embeddings**
```python
# embeddings_service.py  
async def create_embeddings(texts: List[str]) -> List[List[float]]:
    # 1. Batch processing para eficiencia
    # 2. Modelo: text-embedding-3-large
    # 3. Dimensiones: 3072
    # 4. Rate limiting y retry logic
```

#### **5. Storage Vectorial**
```python
# qdrant_service.py
async def add_vectors(vectors, payloads, metadata):
    # 1. Preparar payload con metadata
    # 2. Insertar en colección Qdrant
    # 3. Indexar campos de metadata
    # 4. Verificar inserción exitosa
```

### Metadata Enrichment

#### **Estructura de Metadata**
```json
{
  "source": "/uploads/documento.pdf",
  "file_name": "documento.pdf", 
  "chunk_id": 0,
  "chunk_size": 1000,
  "page_number": 1,
  "document_summary": "Resumen automático",
  "document_type": "resume|general",
  "processed_at": "2024-01-01T12:00:00Z"
}
```

#### **Clasificación Automática**
- **Resume/CV**: Detección por nombre de archivo y contenido
- **General**: Documentos no clasificados como CV
- **Priority Scoring**: CVs obtienen prioridad en búsquedas

### Background Processing

#### **Async Task Management**
```python
@router.post("/upload")
async def upload_document(file: UploadFile, background_tasks: BackgroundTasks):
    # 1. Guardar archivo inmediatamente
    # 2. Retornar confirmación al usuario
    # 3. Procesar en background
    # 4. Actualizar estado vía polling
```

#### **Status Tracking**
```python
# Estados de procesamiento
PENDING = "pending"      # Archivo subido, esperando procesamiento
PROCESSING = "processing" # Extrayendo texto y generando embeddings  
COMPLETED = "completed"  # Listo para búsquedas
ERROR = "error"         # Error en procesamiento
```

---

## 🔍 Base de Datos Vectorial

### Qdrant Configuration

#### **Collection Setup**
```python
# Configuración de colección
collection_config = {
    "vector_size": 3072,  # text-embedding-3-large
    "distance": "Cosine", # Métrica de similitud
    "shard_number": 1,    # Configuración distribuida
    "replication_factor": 1
}
```

#### **Indexing Strategy**
```python
# Índices en campos de metadata para búsquedas eficientes
payload_indices = [
    "metadata.file_name",    # Filtros por archivo
    "metadata.source",       # Filtros por fuente  
    "metadata.document_type" # Filtros por tipo
]
```

### Semantic Search Implementation

#### **Search Pipeline**
```python
async def search(query_vector, limit=10, score_threshold=0.2):
    # 1. Búsqueda vectorial por similitud
    # 2. Filtrado por score de relevancia
    # 3. Priorización de documentos CV
    # 4. Ordenamiento por relevancia
    # 5. Límite de resultados
```

#### **CV Prioritization**
```python
# Estrategia de priorización
cv_results = []      # Documentos tipo CV/resume
other_results = []   # Otros documentos

# Tomar máximo 3 chunks de CV
prioritized_results = cv_results[:3]

# Completar hasta 5 con otros documentos  
remaining_slots = 5 - len(prioritized_results)
prioritized_results.extend(other_results[:remaining_slots])
```

### Data Management

#### **CRUD Operations**
```python
# Vector Operations
insert_vectors()     # Insertar nuevos vectores
search_vectors()     # Búsqueda de similitud
update_payload()     # Actualizar metadata
delete_by_filter()   # Eliminar por filtros

# Collection Management  
create_collection()  # Crear nueva colección
get_collection_info() # Estadísticas y metadata
collection_exists()  # Verificar existencia
reset_collection()   # Limpiar colección
```

#### **Batch Operations**
```python
# Optimización para grandes volúmenes
async def batch_insert(vectors, payloads, batch_size=100):
    # 1. Dividir en lotes para eficiencia
    # 2. Inserción paralela con semáforos
    # 3. Manejo de errores por lote
    # 4. Progress tracking
```

### Performance Optimization

#### **Search Optimization**
- **Caching**: Cache de embeddings frecuentes
- **Indexing**: Índices en campos críticos de metadata
- **Batch Processing**: Operaciones en lotes para eficiencia
- **Connection Pooling**: Pool de conexiones para concurrencia

#### **Storage Optimization**
- **Compression**: Compresión de vectores
- **Partitioning**: Particionado por tipo de documento
- **Backup Strategy**: Respaldos automáticos de colecciones
- **Monitoring**: Métricas de performance y espacio

---

## ⚙️ Variables de Entorno

### Archivo .env Configuration

```bash
# ==============================================
# CONFIGURACIÓN OPENAI
# ==============================================
OPENAI_API_KEY=sk-proj-...                    # Clave API OpenAI (REQUERIDA)
OPENAI_MODEL=gpt-4o-mini                      # Modelo LLM (configurable)

# ==============================================  
# CONFIGURACIÓN QDRANT (Vector Database)
# ==============================================
QDRANT_HOST=qdrant                            # Host del servicio Qdrant
QDRANT_PORT=6333                              # Puerto API Qdrant
COLLECTION_NAME=gemelo_agustin_large          # Nombre de colección vectorial

# ==============================================
# CONFIGURACIÓN POSTGRESQL 
# ==============================================
POSTGRES_HOST=postgres                        # Host del servicio PostgreSQL
POSTGRES_PORT=5432                            # Puerto PostgreSQL
POSTGRES_DB=gemelo_digital                    # Nombre de base de datos
POSTGRES_USER=admin                           # Usuario de base de datos
POSTGRES_PASSWORD=admin123                    # Contraseña (CAMBIAR EN PRODUCCIÓN)

# ==============================================
# CONFIGURACIÓN AUTENTICACIÓN
# ==============================================
ADMIN_USER=admin-gd                           # Usuario administrador
ADMIN_PASSWORD=Pasado_por_mail                # Contraseña admin 
SECRET_KEY=8f42b85e741d819...                 # Clave JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30                # Expiración token (minutos)

# ==============================================
# CONFIGURACIÓN DEVELOPMENT
# ==============================================
ENVIRONMENT=development                       # development|production
DEBUG=true                                    # Logs detallados
LOG_LEVEL=INFO                               # CRITICAL|ERROR|WARNING|INFO|DEBUG
```

### Variables por Servicio

#### **Frontend (Vue.js)**
```bash
# Configuración Vite
VITE_API_URL=http://localhost:8000           # URL del backend
VITE_WS_URL=ws://localhost:8000              # WebSocket URL (si se usa)

# Configuración desarrollo  
CHOKIDAR_USEPOLLING=true                     # Hot reload en Docker
WDS_SOCKET_PORT=0                            # Dev server WebSocket
```

#### **Backend (FastAPI)**
```bash
# Todas las variables del .env principal más:
CORS_ORIGINS=["http://localhost:3000"]        # Orígenes CORS permitidos
MAX_UPLOAD_SIZE=50                           # Tamaño máximo upload (MB)
UPLOAD_DIR=/app/uploads                      # Directorio de uploads
STATIC_DIR=/app/static                       # Directorio estáticos
```

#### **PostgreSQL**
```bash
POSTGRES_DB=gemelo_digital                   # Nombre de base de datos
POSTGRES_USER=admin                          # Usuario de base de datos  
POSTGRES_PASSWORD=admin123                   # Contraseña de base de datos
POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256  # Configuración inicial
```

#### **Qdrant**
```bash
QDRANT__SERVICE__HTTP_PORT=6333              # Puerto HTTP API
QDRANT__SERVICE__GRPC_PORT=6334              # Puerto gRPC
QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage # Path de almacenamiento
```

### Configuración de Producción

```bash
# ⚠️ IMPORTANTE: Cambiar estos valores en producción
ADMIN_PASSWORD=tu-password-super-seguro
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=password-muy-seguro

# SSL/TLS  
ENABLE_HTTPS=true
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Backup
BACKUP_SCHEDULE="0 2 * * *"                 # Cron para backups diarios
BACKUP_RETENTION_DAYS=30                    # Retención de backups
```

---

## 🚀 Despliegue y Configuración

### Quick Start (Desarrollo)

#### **1. Prerequisitos**
```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verificar instalación
docker --version
docker-compose --version
```

#### **2. Clonar y Configurar**
```bash
# Clonar repositorio
git clone <repository-url>
cd gemelo-digital

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY
```

#### **3. Levantar Servicios**
```bash
# Construir y levantar todos los servicios
docker-compose up --build

# En modo detached (background)
docker-compose up -d --build

# Ver logs en tiempo real
docker-compose logs -f
```

#### **4. Verificar Servicios**
```bash
# Health checks
curl http://localhost:3000        # Frontend Vue.js
curl http://localhost:8000/docs   # Backend API docs  
curl http://localhost:6333        # Qdrant status
curl http://localhost:5432        # PostgreSQL (debería timeout)

# Logs específicos por servicio
docker-compose logs frontend
docker-compose logs backend
docker-compose logs postgres
docker-compose logs qdrant
```

### Comandos Útiles

#### **Docker Management**
```bash
# Parar todos los servicios
docker-compose down

# Parar y limpiar volúmenes (⚠️ Borra datos)
docker-compose down -v

# Rebuild sin cache
docker-compose build --no-cache

# Ver estado de servicios
docker-compose ps

# Ejecutar comando en contenedor
docker-compose exec backend bash
docker-compose exec frontend sh
```

#### **Database Management**
```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U admin -d gemelo_digital

# Backup de PostgreSQL
docker-compose exec postgres pg_dump -U admin gemelo_digital > backup.sql

# Restore de PostgreSQL  
docker-compose exec -T postgres psql -U admin gemelo_digital < backup.sql

# Reset de colección Qdrant (vía API)
curl -X POST http://localhost:8000/api/admin/reset_collection \
  -H "Authorization: Bearer <tu-token>"
```

#### **Development Utilities**
```bash
# Ver logs específicos
docker-compose logs -f backend | grep ERROR
docker-compose logs -f frontend

# Reiniciar servicio específico
docker-compose restart backend
docker-compose restart frontend

# Escalar servicios (si es necesario)
docker-compose up --scale backend=2
```

### Configuración de Producción

#### **1. Security Hardening**
```bash
# Generar nuevas claves
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)

# Configurar firewall
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS  
ufw allow 22/tcp      # SSH
ufw deny 5432/tcp     # PostgreSQL (solo interno)
ufw deny 6333/tcp     # Qdrant (solo interno)
```

#### **2. Reverse Proxy (Nginx)**
```nginx
# /etc/nginx/sites-available/gemelo-digital
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **3. SSL/TLS con Let's Encrypt**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com

# Auto-renovación
sudo crontab -e
# 0 12 * * * /usr/bin/certbot renew --quiet
```

#### **4. Monitoring y Logs**
```bash
# Instalar monitoring stack
docker-compose -f docker-compose.prod.yml up -d

# Configurar logrotate
# /etc/logrotate.d/gemelo-digital
/var/log/gemelo-digital/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}
```

### Troubleshooting

#### **Problemas Comunes**

1. **Error de conexión OpenAI**
   ```bash
   # Verificar API key
   echo $OPENAI_API_KEY
   # Probar conexión
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```

2. **Qdrant no inicia**
   ```bash
   # Verificar permisos de volumen
   docker-compose logs qdrant
   # Limpiar volumen si es necesario
   docker-compose down -v
   ```

3. **PostgreSQL connection refused**
   ```bash
   # Verificar estado del contenedor
   docker-compose ps postgres
   # Ver logs de PostgreSQL
   docker-compose logs postgres
   ```

4. **Frontend no se conecta al backend**
   ```bash
   # Verificar CORS configuration
   docker-compose logs backend | grep CORS
   # Verificar network connectivity
   docker-compose exec frontend ping backend
   ```

#### **Performance Tuning**

1. **PostgreSQL Optimization**
   ```sql
   -- postgresql.conf
   shared_buffers = 256MB
   effective_cache_size = 1GB
   maintenance_work_mem = 64MB
   checkpoint_completion_target = 0.7
   wal_buffers = 16MB
   ```

2. **Qdrant Optimization**
   ```yaml
   # En docker-compose.yml
   environment:
     QDRANT__SERVICE__MAX_REQUEST_SIZE_MB: 32
     QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS: 4
   ```

3. **Resource Limits**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   ```

---

## 📊 Métricas y Monitoring

### API Endpoints Status
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **PostgreSQL**: puerto 5432 (interno)
- **Qdrant**: http://localhost:6333/dashboard

### Key Performance Indicators
- **Response Time**: <200ms para queries simples
- **Vector Search**: <500ms para búsquedas semánticas
- **Document Processing**: ~30s por documento PDF
- **Concurrent Users**: Hasta 100 usuarios simultáneos

---

## 🔧 Mantenimiento

### Tareas Regulares
1. **Backup diario** de PostgreSQL y Qdrant
2. **Limpieza de logs** mayores a 30 días
3. **Monitoring** de espacio en disco
4. **Actualización** de dependencias de seguridad

### Actualizaciones
```bash
# Actualizar imágenes Docker
docker-compose pull
docker-compose up -d

# Actualizar dependencias backend
pip install --upgrade -r requirements.txt

# Actualizar dependencias frontend  
npm update
```

---

*Esta documentación cubre todos los aspectos técnicos del proyecto Gemelo Digital. Para dudas específicas, consultar el código fuente o los logs de la aplicación.*