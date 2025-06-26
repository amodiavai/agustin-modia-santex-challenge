#!/bin/bash

echo "🚀 Preparando proyecto para Railway..."

# Usar Dockerfile en lugar de Nixpacks
if [ -f "Dockerfile.railway" ]; then
    echo "📦 Configurando Dockerfile para Railway..."
    cp Dockerfile.railway Dockerfile
    echo "✅ Dockerfile copiado"
fi

# Remover archivos que pueden causar conflictos
if [ -f "nixpacks.toml" ]; then
    echo "🗑️  Removiendo nixpacks.toml para usar Dockerfile..."
    rm nixpacks.toml
fi

echo "📋 Archivos de configuración Railway disponibles:"
echo "   - Dockerfile ✅"
echo "   - railway.json ✅"
echo "   - Procfile ✅"
echo "   - .railwayignore ✅"

echo ""
echo "📌 SIGUIENTE PASO:"
echo "1. Sube el código a GitHub"
echo "2. Ve a railway.app"
echo "3. Deploy desde GitHub repo"
echo "4. Configura las variables de entorno"
echo ""
echo "📖 Ver RAILWAY_DEPLOY.md para instrucciones completas"