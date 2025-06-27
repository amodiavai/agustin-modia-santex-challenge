<template>
  <div class="app">
    <!-- Show login form if not authenticated -->
    <LoginForm v-if="!isAuthenticated" @login-success="handleLoginSuccess" />
    
    <!-- Show main app if authenticated -->
    <div v-else>
      <header class="app-header">
        <div class="container app-header-content">
          <div class="app-brand">
            <div class="app-logo">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>
              </svg>
            </div>
            <h1>Gemelo Digital <span class="author-tag">Agustín Modia</span></h1>
          </div>
          <div class="nav-controls">
            <button 
              class="nav-button" 
              @click="activeTab = 'chat'" 
              :class="{ 'nav-button-active': activeTab === 'chat' }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1h-2.5a2 2 0 0 0-1.6.8L8 14.333 6.1 11.8a2 2 0 0 0-1.6-.8H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2.5a1 1 0 0 1 .8.4l1.9 2.533a1 1 0 0 0 1.6 0l1.9-2.533a1 1 0 0 1 .8-.4H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>
              </svg>
              <span>Chat</span>
            </button>
            <button 
              class="nav-button" 
              @click="activeTab = 'documents'" 
              :class="{ 'nav-button-active': activeTab === 'documents' }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
              </svg>
              <span>Entrenar Gemelo</span>
            </button>
            <button 
              class="nav-button graph-button" 
              @click="showWorkflowGraph"
              title="Ver flujo del agente"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M6 0a.5.5 0 0 1 .5.5V3h3V.5a.5.5 0 0 1 1 0V3h1a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5h-1v3h1a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5h-1v2.5a.5.5 0 0 1-1 0V13h-3v2.5a.5.5 0 0 1-1 0V13H4a.5.5 0 0 1-.5-.5v-3a.5.5 0 0 1 .5-.5h1V6H4a.5.5 0 0 1-.5-.5v-3A.5.5 0 0 1 4 2h1V.5A.5.5 0 0 1 6 0zM4 3v2h1.5a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5H4v2h1.5a.5.5 0 0 1 .5.5v2H9v-2a.5.5 0 0 1 .5-.5H11V9H9.5a.5.5 0 0 1-.5-.5V6a.5.5 0 0 1 .5-.5H11V3H9.5a.5.5 0 0 1-.5-.5V1H6v1.5a.5.5 0 0 1-.5.5H4z"/>
              </svg>
             
            </button>
            <button class="nav-button logout-button" @click="handleLogout">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
                <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
              </svg>
              <span>Salir</span>
            </button>
          </div>
        </div>
      </header>
      
      <main class="app-main">
        <div class="container">
          <div v-if="activeTab === 'chat'">
            <ChatInterface />
          </div>
          <div v-if="activeTab === 'documents'">
            <DocumentUpload @document-added="refreshDocuments" />
            <div class="mt-4"></div>
            <DocumentManager :key="documentRefreshKey" />
          </div>
        </div>
      </main>
      
      <footer class="app-footer">
        <div class="container">
          <div class="footer-content">
            <p class="copyright">Gemelo Digital <span class="accent-text">|</span> Santex Challenge © {{ new Date().getFullYear() }}</p>
            <div class="footer-links">
              <a href="#" class="footer-link">Acerca de</a>
              <span class="footer-separator"></span>
              <a href="#" class="footer-link">Documentación</a>
              <span class="footer-separator"></span>
              <a href="#" class="footer-link">Contacto</a>
            </div>
          </div>
        </div>
      </footer>
      
      <!-- Modal para mostrar el grafo -->
      <div v-if="showGraphModal" class="modal-overlay" @click="closeGraphModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Flujo del Agente LangGraph</h3>
            <button class="close-button" @click="closeGraphModal">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="graphLoading" class="loading-state">
              <div class="spinner"></div>
              <p>Generando grafo...</p>
            </div>
            <div v-else-if="graphError" class="error-state">
              <p>Error: {{ graphError }}</p>
              <button class="retry-button" @click="loadWorkflowGraph">Reintentar</button>
            </div>
            <div v-else class="graph-container">
              <div v-html="graphSvg"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChatInterface from './components/ChatInterface.vue'
import DocumentUpload from './components/DocumentUpload.vue'
import DocumentManager from './components/DocumentManager.vue'
import LoginForm from './components/LoginForm.vue'
import { authService } from './services/api.js'

export default {
  name: 'App',
  components: {
    ChatInterface,
    DocumentUpload,
    DocumentManager,
    LoginForm
  },
  data() {
    return {
      activeTab: 'chat',
      documentRefreshKey: 0,
      isAuthenticated: false,
      showGraphModal: false,
      graphLoading: false,
      graphError: null,
      graphSvg: ''
    }
  },
  mounted() {
    this.checkAuthentication()
  },
  methods: {
    refreshDocuments() {
      this.documentRefreshKey += 1
    },
    checkAuthentication() {
      this.isAuthenticated = authService.isAuthenticated()
    },
    handleLoginSuccess() {
      this.isAuthenticated = true
    },
    handleLogout() {
      authService.logout()
      this.isAuthenticated = false
    },
    showWorkflowGraph() {
      this.showGraphModal = true
      this.loadWorkflowGraph()
    },
    closeGraphModal() {
      this.showGraphModal = false
      this.graphSvg = ''
      this.graphError = null
    },
    async loadWorkflowGraph() {
      this.graphLoading = true
      this.graphError = null
      
      try {
        const response = await fetch('http://localhost:8000/api/admin/langgraph-svg', {
          headers: {
            'Authorization': `Bearer ${authService.getToken()}`
          }
        })
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`)
        }
        
        const svgContent = await response.text()
        this.graphSvg = svgContent
      } catch (error) {
        console.error('Error loading workflow graph:', error)
        this.graphError = error.message
      } finally {
        this.graphLoading = false
      }
    }
  }
}
</script>

<style scoped>
/* Estilos específicos de componente */
.ml-2 {
  margin-left: 0.5rem;
}

.app-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.app-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 208, 208, 0.15);
  color: var(--color-accent);
  border-radius: 10px;
  width: 42px;
  height: 42px;
  padding: 8px;
  box-shadow: var(--glow-sm);
  border: 1px solid rgba(0, 208, 208, 0.3);
}

.author-tag {
  font-size: 0.875rem;
  font-weight: 400;
  opacity: 0.8;
  border-left: 2px solid var(--color-accent);
  padding-left: 0.75rem;
  margin-left: 0.75rem;
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  color: var(--color-text);
  text-shadow: 0 0 15px rgba(214, 236, 236, 0.3);
}

.nav-controls {
  display: flex;
  gap: 0.75rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: rgba(10, 30, 30, 0.6);
  color: var(--color-text-light);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.nav-button:hover {
  background-color: rgba(0, 191, 191, 0.1);
  color: var(--color-text);
  border-color: var(--color-secondary);
}

.nav-button-active {
  background-color: rgba(0, 208, 208, 0.15);
  color: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: var(--glow-sm);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.copyright {
  font-size: 0.875rem;
}

.accent-text {
  color: var(--color-primary);
  margin: 0 0.25rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-link {
  color: var(--color-text-light);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: var(--color-primary);
  text-decoration: none;
}

.footer-separator {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: var(--color-border);
}

.logout-button {
  background-color: rgba(255, 69, 69, 0.1);
  border-color: rgba(255, 69, 69, 0.3);
  color: #ff6b6b;
}

.logout-button:hover {
  background-color: rgba(255, 69, 69, 0.2);
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.graph-button {
  background-color: rgba(147, 51, 234, 0.1);
  border-color: rgba(147, 51, 234, 0.3);
  color: #a855f7;
}

.graph-button:hover {
  background-color: rgba(147, 51, 234, 0.2);
  border-color: #a855f7;
  color: #a855f7;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(10, 30, 30, 0.95));
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
    -webkit-backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
}

.modal-content {
  background: linear-gradient(145deg, #0a1e1e, #0f2626);
  border: 2px solid rgba(0, 208, 208, 0.3);
  border-radius: 20px;
  max-width: 95vw;
  max-height: 95vh;
  overflow: hidden;
  box-shadow: 
    0 25px 80px rgba(0, 0, 0, 0.8),
    0 0 0 1px rgba(0, 208, 208, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    transform: scale(0.9) translateY(-20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2.5rem;
  border-bottom: 2px solid rgba(0, 208, 208, 0.2);
  background: linear-gradient(135deg, rgba(0, 208, 208, 0.1), rgba(0, 191, 191, 0.05));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1.5rem;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(0, 208, 208, 0.5);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-header h3::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--color-primary);
}

.close-button {
  background: rgba(255, 69, 69, 0.1);
  border: 2px solid rgba(255, 69, 69, 0.3);
  color: #ff8a8a;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

.close-button:hover {
  background: rgba(255, 69, 69, 0.2);
  border-color: #ff6b6b;
  color: #ff6b6b;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.3);
}

.modal-body {
  padding: 2.5rem;
  max-height: calc(95vh - 140px);
  overflow: auto;
  background: rgba(10, 30, 30, 0.3);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--color-text-light);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 2rem;
  color: #ff6b6b;
}

.retry-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  margin-top: 1rem;
  transition: all var(--transition);
}

.retry-button:hover {
  background-color: var(--color-secondary);
}

.graph-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(245, 250, 250, 0.98));
  border-radius: 16px;
  padding: 2rem;
  border: 2px solid rgba(0, 208, 208, 0.2);
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 10px 30px rgba(0, 0, 0, 0.3);
}

.graph-container svg {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff, #f8fbfb);
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}
</style>
