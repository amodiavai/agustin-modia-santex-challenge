# 🚀 Deploy en Railway - Instrucciones Paso a Paso

## 📋 Requisitos Previos

1. **Cuenta en Railway**: [railway.app](https://railway.app)
2. **Qdrant Cloud** (Recomendado): [cloud.qdrant.io](https://cloud.qdrant.io)
3. **OpenAI API Key**: [platform.openai.com](https://platform.openai.com)

## 🔧 Configuración de Servicios Externos

### 1. Configurar Qdrant Cloud

```bash
1. Ve a https://cloud.qdrant.io/
2. Crea una cuenta gratuita
3. Crea un nuevo cluster (Free Tier)
4. Anota:
   - URL del cluster: https://xxxxxx.europe-west3-0.gcp.cloud.qdrant.io:6333
   - API Key: qdrant_xxxxxxxxx
```

### 2. Configurar OpenAI API

```bash
1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API Key
3. Anota: sk-proj-xxxxxxxxx
```

## 🚀 Deploy en Railway

### Opción 1: Deploy desde GitHub (Recomendado)

```bash
1. Sube este código a tu repositorio GitHub
2. Ve a https://railway.app/
3. Click "Deploy from GitHub repo"
4. Selecciona tu repositorio
5. Railway detectará automáticamente la configuración
```

### Si Railway falla detectando Python:

1. **Renombrar Dockerfile**: `mv Dockerfile.railway Dockerfile`
2. **Re-deployar**: Railway usará el Dockerfile personalizado
3. **O usar CLI**: Ver Opción 2

### Opción 2: Deploy con CLI

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Crear proyecto
railway init

# Deploy
railway up
```

## ⚙️ Variables de Entorno en Railway

Configura estas variables en Railway Dashboard → Variables:

### 🔑 Obligatorias

```env
OPENAI_API_KEY=sk-proj-tu-clave-aqui
QDRANT_URL=https://tu-cluster.europe-west3-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=qdrant_tu-api-key-aqui
ADMIN_USER=admin-gd
ADMIN_PASSWORD=tu-password-seguro
SECRET_KEY=una-clave-secreta-muy-larga-de-al-menos-32-caracteres-aleatorios
```

### 📋 Opcionales

```env
OPENAI_MODEL=gpt-4o-mini
COLLECTION_NAME=gemelo_agustin_large
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🏗️ Proceso de Build Automático

Railway ejecutará automáticamente:

1. **Frontend Build**: `cd frontend && npm install && npm run build`
2. **Backend Setup**: `cd backend && pip install -r requirements.txt`
3. **Inicio**: `./start.sh` (incluye verificación de entorno e inicialización)

## ✅ Verificación del Deploy

### URLs de tu aplicación:

- **App Principal**: `https://tu-proyecto.railway.app/`
- **API**: `https://tu-proyecto.railway.app/api/`
- **Health Check**: `https://tu-proyecto.railway.app/health`

### Verificar funcionamiento:

1. **Health Check**: Debe responder `{"status": "ok"}`
2. **Login**: Usar `ADMIN_USER` y `ADMIN_PASSWORD`
3. **Chat**: Probar conversación con el gemelo
4. **Documentos**: Subir un PDF de prueba

## 🔍 Logs y Debugging

```bash
# Ver logs en tiempo real
railway logs

# Ver variables configuradas
railway variables

# Abrir la app
railway open

# Estado del servicio
railway status
```

## 🔧 Troubleshooting Común

### ❌ Build Failed

```bash
Solución:
1. Verificar que todas las variables estén configuradas
2. Revisar logs en Railway Dashboard
3. Asegurar que el repositorio tenga todos los archivos
```

### ❌ Error de Conexión Qdrant

```bash
Solución:
1. Verificar QDRANT_URL (debe incluir puerto :6333)
2. Verificar QDRANT_API_KEY
3. Asegurar que el cluster Qdrant esté activo
```

### ❌ Error de Autenticación

```bash
Solución:
1. Verificar OPENAI_API_KEY (debe empezar con sk-proj-)
2. Verificar SECRET_KEY (mínimo 32 caracteres)
3. Verificar ADMIN_USER y ADMIN_PASSWORD
```

### ❌ Frontend no carga

```bash
Solución:
1. Verificar que el build del frontend sea exitoso
2. Revisar logs de construcción
3. El backend sirve automáticamente el frontend
```

## 📊 Monitoreo

Railway proporciona automáticamente:
- **Métricas de CPU/RAM**
- **Logs en tiempo real**
- **Health checks automáticos**
- **SSL certificado**

## 🔄 Actualizaciones

Para actualizar el código:

```bash
# Con GitHub
1. Push cambios a tu repositorio
2. Railway re-desplegará automáticamente

# Con CLI
railway up
```

## 💡 Consejos

1. **Variables**: Usa Railway UI para configurar variables (más seguro)
2. **Logs**: Monitorea logs durante el primer deploy
3. **Health**: Usa `/health` endpoint para monitoring
4. **Backup**: Exporta datos de Qdrant regularmente
5. **Costos**: Monitor el uso en Railway Dashboard

## 🎯 Todo Listo

Una vez configurado, tendrás:
- ✅ Frontend y Backend en un solo servicio
- ✅ Base de datos vectorial en Qdrant Cloud
- ✅ Autenticación funcional
- ✅ Chat con IA funcionando
- ✅ Subida de documentos
- ✅ SSL automático
- ✅ Health checks

¡Tu Gemelo Digital estará disponible 24/7 en Railway! 🎉