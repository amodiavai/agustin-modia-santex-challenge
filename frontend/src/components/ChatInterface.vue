<template>
  <div class="card fade-in">
    <div class="chat-header">
      <div>
        <h2>Chat con Agustín Digital</h2>
        <p class="text-sm text-muted mb-4">Conversá con el gemelo digital de Agustín Modia</p>
      </div>
      <div class="chat-controls">
        <button class="button button-secondary chat-control-btn" @click="loadChatHistory" :disabled="loading">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
          </svg>
          Cargar Historial
        </button>
        <button class="button button-danger chat-control-btn" @click="clearChatHistory" :disabled="loading">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
          </svg>
          Limpiar
        </button>
      </div>
    </div>
    
    <div class="chat-container">
      <div class="chat-messages" ref="chatMessages">
        <!-- Mensaje de bienvenida -->
        <div v-if="messages.length === 0" class="chat-welcome-message">
          <h3>👋 ¡Hola! Soy el gemelo digital de Agustín.</h3>
          <p>Podés hacerme preguntas sobre cualquier tema. Si tenés documentos subidos, también puedo usar esa información para responder.</p>
        </div>
        
        <!-- Mensajes de la conversación -->
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="chat-message" 
          :class="{'chat-message-user': msg.role === 'user', 'chat-message-ai': msg.role === 'assistant'}"
        >
          <div class="chat-message-content">
            <div v-if="msg.role === 'user'">{{ msg.content }}</div>
            <div v-else v-html="formatMessage(msg.content)"></div>
          </div>
        </div>
        
        <!-- Indicador de escritura -->
        <div v-if="isTyping" class="chat-message chat-message-ai">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
      
      <div class="chat-input-container">
        <textarea 
          v-model="userInput" 
          class="chat-input"
          placeholder="Escribe tu mensaje aquí..."
          @keydown.enter.prevent="sendMessage"
          :disabled="isTyping"
        ></textarea>
        <button 
          class="button button-primary chat-send-button" 
          @click="sendMessage" 
          :disabled="!userInput.trim() || isTyping"
        >
          Enviar
        </button>
      </div>
    </div>
    
    <!-- Fuentes utilizadas (si hay) -->
    <div v-if="sources.length > 0" class="chat-sources mt-4">
      <h4 class="mb-2">Fuentes utilizadas:</h4>
      <ul class="sources-list">
        <li v-for="(source, index) in sources" :key="index" class="source-item">
          <span class="source-name">{{ source.file_name }}</span>
          <span class="source-relevance">Relevancia: {{ Math.round(source.relevance * 100) }}%</span>
        </li>
      </ul>
    </div>
    
    <!-- Uso de tokens (si hay) -->
    <div v-if="tokenUsage && tokenUsage.total_tokens > 0" class="token-usage mt-4">
      <h4 class="mb-2">Uso de Tokens OpenAI:</h4>
      <div class="token-stats">
        <div class="token-stat">
          <span class="token-label">Prompt:</span>
          <span class="token-value">{{ tokenUsage.prompt_tokens }}</span>
        </div>
        <div class="token-stat">
          <span class="token-label">Respuesta:</span>
          <span class="token-value">{{ tokenUsage.completion_tokens }}</span>
        </div>
        <div class="token-stat token-total">
          <span class="token-label">Total:</span>
          <span class="token-value">{{ tokenUsage.total_tokens }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';
import axios from 'axios';
import { chatService } from '../services/api.js';

export default {
  name: 'ChatInterface',
  data() {
    return {
      userInput: '',
      messages: [],
      isTyping: false,
      sources: [],
      tokenUsage: null,
      streamController: null,
      loading: false
    };
  },
  methods: {
    async sendMessage() {
      if (!this.userInput.trim() || this.isTyping) return;
      
      // Añadir mensaje del usuario
      const userMessage = this.userInput.trim();
      this.messages.push({
        role: 'user',
        content: userMessage
      });
      this.userInput = '';
      
      // Indicar que el gemelo está escribiendo
      this.isTyping = true;
      this.sources = [];
      this.tokenUsage = null;
      
      // Scroll al final de los mensajes
      this.$nextTick(() => {
        this.scrollToBottom();
      });
      
      try {
        // Formatear el historial para la API
        const history = this.messages.slice(0, -1).map(msg => ({
          role: msg.role,
          content: msg.content
        }));
        
        // Usar API con streaming para mejorar experiencia de usuario
        await this.streamResponse(userMessage, history);
      } catch (error) {
        console.error('Error al enviar mensaje:', error);
        // Mostrar mensaje de error
        this.messages.push({
          role: 'assistant',
          content: 'Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta nuevamente.'
        });
      } finally {
        this.isTyping = false;
        
        // Scroll al final de los mensajes
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    async streamResponse(message, history) {
      try {
        // Cancelar stream anterior si existe
        if (this.streamController) {
          this.streamController.abort();
        }
        
        // Crear nuevo controlador para este stream
        this.streamController = new AbortController();
        
        // Preparar mensaje temporal para mostrar la respuesta en tiempo real
        const tempMessageIndex = this.messages.length;
        this.messages.push({
          role: 'assistant',
          content: ''
        });
        
        // Configurar la solicitud de streaming
        const token = localStorage.getItem('token');
        const response = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            message,
            history
          }),
          signal: this.streamController.signal
        });
        
        // Procesar la respuesta en streaming
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let responseText = '';
        
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          
          // Decodificar el chunk recibido
          const chunk = decoder.decode(value, { stream: true });
          
          // Procesar los eventos SSE
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6);
              
              // Verificar si es el fin del stream
              if (data === '[DONE]') {
                // Realizar consulta normal para obtener fuentes
                await this.fetchSources(message, history);
                break;
              }
              
              // Actualizar el texto de respuesta
              responseText += data;
              this.messages[tempMessageIndex].content = responseText;
              
              // Scroll mientras se reciben mensajes
              this.$nextTick(() => {
                this.scrollToBottom();
              });
            }
          }
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Error en streaming:', error);
        }
      }
    },
    
    async fetchSources(message, history) {
      try {
        console.log('Obteniendo fuentes y tokens...');
        const token = localStorage.getItem('token');
        
        // Hacer una petición normal para obtener las fuentes y tokens
        const response = await axios.post('/api/chat/send', {
          message,
          history
        }, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('Respuesta de fuentes:', response.data);
        
        if (response.data && response.data.sources) {
          this.sources = response.data.sources;
          console.log('Fuentes actualizadas:', this.sources);
        }
        
        if (response.data && response.data.token_usage) {
          this.tokenUsage = response.data.token_usage;
          console.log('Tokens actualizados:', this.tokenUsage);
        }
      } catch (error) {
        console.error('Error obteniendo fuentes:', error);
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.chatMessages;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    formatMessage(text) {
      // Convertir markdown a HTML para mejor visualización
      return marked(text);
    },
    
    async loadChatHistory() {
      this.loading = true;
      try {
        const historyData = await chatService.getHistory();
        
        // Clear current messages
        this.messages = [];
        
        // Convert history data to message format
        historyData.forEach(item => {
          this.messages.push({
            role: 'user',
            content: item.user_message
          });
          this.messages.push({
            role: 'assistant',
            content: item.assistant_response
          });
        });
        
        // If no history, show welcome message
        if (historyData.length === 0) {
          setTimeout(() => {
            this.messages.push({
              role: 'assistant',
              content: '¡Hola! Soy el gemelo digital de Agustín Modia. ¿En qué puedo ayudarte hoy?'
            });
          }, 500);
        }
        
        // Scroll to bottom after loading
        this.$nextTick(() => {
          this.scrollToBottom();
        });
        
      } catch (error) {
        console.error('Error loading chat history:', error);
        // If error loading history, show welcome message
        this.messages = [];
        setTimeout(() => {
          this.messages.push({
            role: 'assistant',
            content: '¡Hola! Soy el gemelo digital de Agustín Modia. ¿En qué puedo ayudarte hoy?'
          });
        }, 500);
      } finally {
        this.loading = false;
      }
    },
    
    async clearChatHistory() {
      if (!confirm('¿Estás seguro de que querés limpiar todo el historial de chat?')) {
        return;
      }
      
      this.loading = true;
      try {
        await chatService.clearHistory();
        this.messages = [];
        this.sources = [];
        this.tokenUsage = null;
        
        // Add welcome message after clearing
        setTimeout(() => {
          this.messages.push({
            role: 'assistant',
            content: '¡Hola! Soy el gemelo digital de Agustín Modia. ¿En qué puedo ayudarte hoy?'
          });
        }, 500);
        
      } catch (error) {
        console.error('Error clearing chat history:', error);
        alert('Error al limpiar el historial de chat');
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    // Load chat history automatically when component mounts
    this.loadChatHistory();
  }
}
</script>

<style scoped>
.chat-welcome-message {
  text-align: center;
  padding: 2rem 0;
  color: var(--color-text-light);
}

.sources-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.source-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: var(--radius);
  background-color: rgba(79, 70, 229, 0.05);
  margin-bottom: 0.5rem;
}

.source-name {
  font-weight: 500;
}

.source-relevance {
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.text-muted {
  color: var(--color-text-light);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.chat-controls {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.chat-control-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  white-space: nowrap;
}

.chat-control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-secondary {
  background-color: rgba(0, 191, 191, 0.1);
  color: var(--color-secondary);
  border: 1px solid rgba(0, 191, 191, 0.3);
}

.button-secondary:hover:not(:disabled) {
  background-color: rgba(0, 191, 191, 0.2);
  border-color: var(--color-secondary);
}

.button-danger {
  background-color: rgba(255, 69, 69, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 69, 69, 0.3);
}

.button-danger:hover:not(:disabled) {
  background-color: rgba(255, 69, 69, 0.2);
  border-color: #ff6b6b;
}

/* Token usage styles */
.token-usage {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
}

.token-usage h4 {
  color: var(--color-primary);
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.token-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.token-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  min-width: 80px;
}

.token-stat.token-total {
  background-color: rgba(0, 191, 191, 0.1);
  border: 1px solid rgba(0, 191, 191, 0.3);
}

.token-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.25rem;
}

.token-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
}

.token-total .token-value {
  color: var(--color-secondary);
}

@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chat-controls {
    justify-content: stretch;
  }
  
  .chat-control-btn {
    flex: 1;
    justify-content: center;
  }
  
  .token-stats {
    gap: 0.5rem;
  }
  
  .token-stat {
    min-width: 70px;
  }
}
</style>
