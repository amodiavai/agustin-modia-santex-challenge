<template>
  <div class="app">
    <header class="app-header">
      <div class="container app-header-content">
        <h1>Gemelo Digital - Agustín Modia</h1>
        <div>
          <button class="button button-secondary" @click="activeTab = 'chat'" :class="{ 'button-primary': activeTab === 'chat' }">
            Chat
          </button>
          <button class="button button-secondary ml-2" @click="activeTab = 'documents'" :class="{ 'button-primary': activeTab === 'documents' }">
            Documentos
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
        <p>Gemelo Digital - Santex Challenge © {{ new Date().getFullYear() }}</p>
      </div>
    </footer>
  </div>
</template>

<script>
import ChatInterface from './components/ChatInterface.vue'
import DocumentUpload from './components/DocumentUpload.vue'
import DocumentManager from './components/DocumentManager.vue'

export default {
  name: 'App',
  components: {
    ChatInterface,
    DocumentUpload,
    DocumentManager
  },
  data() {
    return {
      activeTab: 'chat',
      documentRefreshKey: 0
    }
  },
  methods: {
    refreshDocuments() {
      this.documentRefreshKey += 1
    }
  }
}
</script>

<style>
/* Estilos específicos de componente */
.ml-2 {
  margin-left: 0.5rem;
}
</style>
