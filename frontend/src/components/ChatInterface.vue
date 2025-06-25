<template>
  <div class="card fade-in">
    <h2>Chat con Agustín Digital</h2>
    <p class="text-sm text-muted mb-4">Conversá con el gemelo digital de Agustín Modia</p>
    
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
  </div>
</template>

<script>
import { marked } from 'marked';
import axios from 'axios';

export default {
  name: 'ChatInterface',
  data() {
    return {
      userInput: '',
      messages: [],
      isTyping: false,
      sources: [],
      streamController: null
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
        const response = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
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
        // Hacer una petición normal para obtener las fuentes
        const response = await axios.post('/api/chat/send', {
          message,
          history
        });
        
        if (response.data && response.data.sources) {
          this.sources = response.data.sources;
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
    }
  },
  mounted() {
    // Añadir mensaje de bienvenida al iniciar el componente
    setTimeout(() => {
      this.messages.push({
        role: 'assistant',
        content: '¡Hola! Soy el gemelo digital de Agustín Modia. ¿En qué puedo ayudarte hoy?'
      });
    }, 500);
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
</style>
