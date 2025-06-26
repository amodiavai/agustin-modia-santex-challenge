#!/bin/bash
set -e

echo "🚀 Iniciando Gemelo Digital..."

# Verificar variables de entorno
echo "🔍 Verificando configuración..."
cd backend && python check_env.py

if [ $? -ne 0 ]; then
    echo "❌ Error en la configuración. Por favor, revisa las variables de entorno."
    exit 1
fi

echo "✅ Configuración verificada"

# Inicializar datos si es necesario
echo "📊 Inicializando datos..."
python init_data.py

# Iniciar servidor
echo "🌐 Iniciando servidor..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}