#!/bin/bash
set -e

# Esperar a que Qdrant esté disponible antes de continuar
echo "🔄 Esperando a que el servicio Qdrant esté disponible..."
until curl --silent --fail http://${QDRANT_HOST}:${QDRANT_PORT}/healthz; do
  echo "⏳ Qdrant no está disponible todavía... esperando 5 segundos"
  sleep 5
done
echo "✅ Qdrant está disponible!"

# Ejecutar script de inicialización para verificar y procesar el archivo CV
echo "🚀 Verificando documento inicial..."
python -m app.init_data

# Iniciar la aplicación FastAPI
echo "🌐 Iniciando servidor FastAPI..."
exec "$@"
