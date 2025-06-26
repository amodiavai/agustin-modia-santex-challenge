import axios from 'axios';

// Crear instancia de axios con configuración común
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptores para agregar token de autenticación
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Interceptores para manejar errores globalmente
api.interceptors.response.use(
  response => response,
  error => {
    // Si hay error 401, limpiar token y redirigir a login
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    console.error('API Error:', error.response || error);
    return Promise.reject(error);
  }
);

// Servicios de Autenticación
export const authService = {
  // Iniciar sesión
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    return response.data;
  },
  
  // Cerrar sesión
  logout: () => {
    localStorage.removeItem('token');
  },
  
  // Verificar si está autenticado
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  
  // Obtener token de localStorage
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  // Verificar token
  verifyToken: async () => {
    const response = await api.get('/auth/verify');
    return response.data;
  }
};

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
  },
  
  // Obtener historial de chat
  getHistory: async () => {
    const response = await api.get('/chat/history');
    return response.data;
  },
  
  // Limpiar historial de chat
  clearHistory: async () => {
    const response = await api.delete('/chat/history');
    return response.data;
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
  auth: authService,
  chat: chatService,
  documents: documentService
};
