FROM node:18-alpine

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 3000

# Comando para ejecutar el servidor de desarrollo de Vite en modo host
# Esto permite acceso desde fuera del contenedor y es compatible con desarrollo y producción
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
