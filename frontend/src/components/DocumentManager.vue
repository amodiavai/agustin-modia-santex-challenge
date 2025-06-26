<template>
  <div class="card fade-in">
    <div class="card-header flex justify-between items-center">
      <h2>Documentos Procesados</h2>
      <button class="button button-secondary" @click="refreshDocuments">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
          <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
        </svg>
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-4">
      <div class="loading-spinner"></div>
      <p class="mt-2">Cargando información de documentos...</p>
    </div>
    
    <div v-else-if="error" class="alert alert-error mt-4">
      Error: {{ error }}
    </div>
    
    <div v-else-if="documents.length === 0" class="empty-state">
      <div class="empty-icon mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
          <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
        </svg>
      </div>
      <h3>No hay documentos procesados</h3>
      <p class="text-sm text-muted mt-2">Subí documentos PDF desde la sección de "Subir Documentos"</p>
    </div>
    
    <div v-else>
      <div class="stats-container flex gap-4 mb-4">
        <div class="stat-card">
          <div class="stat-title">Total Documentos</div>
          <div class="stat-value">{{ collectionInfo.total_documents || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">Estado</div>
          <div class="stat-value">
            <span class="badge" :class="{'badge-success': isCollectionActive, 'badge-error': !isCollectionActive}">
              {{ isCollectionActive ? 'Activa' : 'Inactiva' }}
            </span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-title">Colección</div>
          <div class="stat-value text-sm">{{ collectionInfo.collection_name || 'N/A' }}</div>
        </div>
      </div>
      
      <h3 class="mb-2">Documentos</h3>
      <div v-if="documents.length > 0" class="documents-list">
        <div 
          v-for="(doc, index) in documents" 
          :key="index"
          class="document-item"
        >
          <div class="document-info">
            <div class="document-name">{{ doc.filename }}</div>
            <div class="document-meta text-sm">
              <span class="badge" :class="{
                'badge-success': doc.status === 'completed',
                'badge-warning': doc.status === 'processing',
                'badge-error': doc.status === 'failed'
              }">
                {{ doc.status }}
              </span>
              <span class="document-date">{{ formatDate(doc.created_at) }}</span>
            </div>
          </div>
          
          <div class="document-actions">
            <button 
              class="button button-danger button-icon" 
              @click="confirmDelete(doc.filename)"
              title="Eliminar documento"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal de confirmación de eliminación -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <h3>¿Eliminar documento?</h3>
        <p>¿Estás seguro de que querés eliminar el documento "{{ documentToDelete }}"? Esta acción no se puede deshacer.</p>
        <div class="modal-actions mt-4">
          <button class="button button-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="button button-danger" @click="deleteDocument">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DocumentManager',
  data() {
    return {
      documents: [],
      collectionInfo: {},
      loading: true,
      error: null,
      showDeleteModal: false,
      documentToDelete: '',
      refreshInterval: null
    };
  },
  computed: {
    isCollectionActive() {
      return this.collectionInfo.collection_status === 'active';
    }
  },
  methods: {
    async refreshDocuments() {
      this.loading = true;
      this.error = null;
      
      try {
        // Obtener la información básica de la colección
        const collectionResponse = await axios.get('/api/documents/list');
        
        if (collectionResponse.data) {
          this.collectionInfo = collectionResponse.data;
        }
        
        // Obtener la lista detallada de documentos desde el nuevo endpoint
        const documentsResponse = await axios.get('/api/documents/detail');
        
        if (documentsResponse.data && documentsResponse.data.documents) {
          // Usar los documentos reales de Qdrant
          this.documents = documentsResponse.data.documents;
        } else {
          this.documents = [];
        }
      } catch (error) {
        console.error('Error obteniendo documentos:', error);
        this.error = error.response?.data?.detail || error.message;
      } finally {
        this.loading = false;
      }
    },
    
    confirmDelete(filename) {
      this.documentToDelete = filename;
      this.showDeleteModal = true;
    },
    
    async deleteDocument() {
      try {
        const response = await axios.delete(`/api/documents/${this.documentToDelete}`);
        
        if (response.data && response.data.status === 'success') {
          // Eliminar documento de la lista local
          this.documents = this.documents.filter(doc => doc.filename !== this.documentToDelete);
          
          // Actualizar estadísticas
          await this.refreshDocuments();
        }
      } catch (error) {
        console.error('Error eliminando documento:', error);
        this.error = error.response?.data?.detail || error.message;
      } finally {
        this.showDeleteModal = false;
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  },
  mounted() {
    // Cargar documentos al montar el componente
    this.refreshDocuments();
    
    // Actualizar cada 30 segundos
    this.refreshInterval = setInterval(() => {
      this.refreshDocuments();
    }, 30000);
  },
  beforeUnmount() {
    // Limpiar intervalo al desmontar componente
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
}
</script>

<style scoped>
.card-header {
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 0;
  color: var(--color-text-light);
}

.empty-icon {
  color: var(--color-text-light);
}

.stats-container {
  display: flex;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  padding: 1rem;
  background-color: var(--color-background);
  border-radius: var(--radius);
  margin-right: 0.5rem;
}

.stat-title {
  font-size: 0.875rem;
  color: var(--color-text-light);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
}

.documents-list {
  margin-top: 1rem;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--color-background);
  border-radius: var(--radius);
  margin-bottom: 0.5rem;
  transition: background-color var(--transition);
}

.document-item:hover {
  background-color: rgba(79, 70, 229, 0.05);
}

.document-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.document-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-light);
}

.document-date {
  font-size: 0.75rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid rgba(79, 70, 229, 0.3);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  margin: 0 auto;
  animation: spinner 1s linear infinite;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.modal-content {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

@keyframes spinner {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .stats-container {
    flex-direction: column;
  }
  
  .stat-card {
    margin-right: 0;
    margin-bottom: 0.5rem;
  }
}
</style>
