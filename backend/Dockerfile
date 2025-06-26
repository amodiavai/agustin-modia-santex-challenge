FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias, curl para health check y graphviz para generar diagramas
RUN apt-get update && apt-get install -y curl graphviz && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorio para archivos subidos si no existe
RUN mkdir -p uploads

# Hacer ejecutable el script de entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Configurar entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Comando para ejecutar la aplicación (se pasa al entrypoint)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
