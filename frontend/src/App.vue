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
      isAuthenticated: false
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
</style>
