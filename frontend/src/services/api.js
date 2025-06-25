import axios from 'axios';

// Crear instancia de axios con configuración común
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptores para manejar errores globalmente
api.interceptors.response.use(
  response => response,
  error => {
    // Log de errores
    console.error('API Error:', error.response || error);
    return Promise.reject(error);
  }
);

// Servicios de Chat
export const chatService = {
  // Enviar mensaje y recibir respuesta completa
  sendMessage: async (message, history = []) => {
    const response = await api.post('/chat/send', { message, history });
    return response.data;
  },
  
  // Preparar URL para streaming
  getStreamUrl: () => {
    return '/api/chat/stream';
  }
};

// Servicios de Documentos
export const documentService = {
  // Subir documento
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // No usar api directamente aquí porque necesitamos FormData
    const response = await axios.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  },
  
  // Verificar estado de procesamiento
  checkProcessingStatus: async (documentId) => {
    const response = await api.get(`/documents/status/${documentId}`);
    return response.data;
  },
  
  // Listar documentos
  listDocuments: async () => {
    const response = await api.get('/documents/list');
    return response.data;
  },
  
  // Eliminar documento
  deleteDocument: async (documentName) => {
    const response = await api.delete(`/documents/${documentName}`);
    return response.data;
  }
};

// Exportar servicios
export default {
  chat: chatService,
  documents: documentService
};
