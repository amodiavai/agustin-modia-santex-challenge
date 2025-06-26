#!/bin/bash
# Script para mostrar los metadatos de documentos en el contenedor Docker

echo "Ejecutando script de metadatos en el contenedor backend..."
docker-compose exec backend python -m app.tools.show_metadata
