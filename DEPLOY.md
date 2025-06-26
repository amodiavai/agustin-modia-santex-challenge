# Despliegue en Railway - Gemelo Digital

Este documento explica cómo desplegar el Gemelo Digital completo en Railway en un solo servicio.

## Preparativos antes del despliegue

### 1. Configurar Qdrant Cloud (Recomendado)

1. Ve a [Qdrant Cloud](https://cloud.qdrant.io/)
2. Crea una cuenta y un cluster gratuito
3. Anota la URL y API Key de tu cluster

### 2. Configurar OpenAI API

1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Genera una API Key
3. Anótala para configurarla en Railway

## Despliegue en Railway

### Opción 1: Deploy directo desde GitHub

1. **Fork este repositorio** a tu cuenta de GitHub
2. Ve a [Railway](https://railway.app/)
3. Conecta tu cuenta de GitHub
4. Selecciona "Deploy from GitHub repo"
5. Elige tu fork del proyecto

### Opción 2: Deploy con Railway CLI

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login en Railway
railway login

# Inicializar proyecto
railway init

# Desplegar
railway up
```

## Variables de Entorno Requeridas

Configura estas variables en el panel de Railway:

### OpenAI (Obligatorio)
```
OPENAI_API_KEY=sk-proj-tu-clave-api-aqui
OPENAI_MODEL=gpt-4o-mini
```

### Qdrant Cloud (Recomendado)
```
QDRANT_URL=https://tu-cluster.qdrant.cloud:6333
QDRANT_API_KEY=tu-api-key-qdrant
COLLECTION_NAME=gemelo_agustin_large
```

### Autenticación
```
ADMIN_USER=admin-gd
ADMIN_PASSWORD=tu-password-seguro
SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria-para-jwt
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Sistema
```
PORT=8000
```

## Configuración Automática

El proyecto está configurado para:

- ✅ **Build automático**: Construye el frontend y backend
- ✅ **Archivos estáticos**: El backend sirve el frontend construido
- ✅ **Routing SPA**: Maneja las rutas del frontend correctamente
- ✅ **Health checks**: Endpoint `/health` para Railway
- ✅ **Inicialización automática**: Procesa el CV de Agustín al primer inicio

## Estructura del Deploy

```
Railway Service
├── Frontend (Vue.js) → Build estático
├── Backend (FastAPI) → Servidor principal
├── Qdrant → Servicio externo (Qdrant Cloud)
└── OpenAI API → Servicio externo
```

## URLs después del deploy

- **Aplicación completa**: `https://tu-app.railway.app/`
- **API**: `https://tu-app.railway.app/api/`
- **Health check**: `https://tu-app.railway.app/health`

## Solución de Problemas

### Build Fallido
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs en Railway Dashboard

### Error de Conexión Qdrant
- Verifica que `QDRANT_URL` y `QDRANT_API_KEY` sean correctos
- Asegúrate de que el cluster de Qdrant esté activo

### Frontend no Carga
- El backend debe construir el frontend primero
- Verifica que el build de `npm run build` sea exitoso

### Problemas de Autenticación
- Verifica `SECRET_KEY`, `ADMIN_USER`, y `ADMIN_PASSWORD`
- Asegúrate de que `SECRET_KEY` tenga al menos 32 caracteres

## Escalabilidad

Para producción, considera:

- **Base de datos externa**: PostgreSQL en lugar de SQLite
- **Qdrant dedicado**: Cluster Qdrant con más recursos
- **Monitoreo**: Configurar logs y métricas
- **Backup**: Exportar/importar datos de Qdrant regularmente

## Comandos Útiles

```bash
# Ver logs en tiempo real
railway logs

# Abrir la aplicación
railway open

# Configurar variables
railway variables set OPENAI_API_KEY=sk-proj-...

# Ver estado del servicio
railway status
```