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
          class="document-item expanded-doc-item"
        >
          <div class="document-header">
            <div class="document-info">
              <div class="document-name-wrapper">
                <div class="document-name">{{ doc.filename }}</div>
                <span class="document-type-badge" :class="{'document-type-resume': doc.document_type === 'resume'}">
                  {{ doc.document_type === 'resume' ? 'CV/Resumen' : 'General' }}
                </span>
              </div>
              <div class="document-meta text-sm">
                <span class="badge" :class="{
                  'badge-success': doc.status === 'completed',
                  'badge-warning': doc.status === 'processing',
                  'badge-error': doc.status === 'failed'
                }">
                  {{ doc.status }}
                </span>
                <span class="document-date">{{ formatDate(doc.created_at) }}</span>
                <span class="chunks-count">{{ doc.chunk_count || 0 }} chunks</span>
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

          <!-- Sección de metadatos del documento -->
          <div class="document-metadata" v-if="doc.document_summary">
            <div class="metadata-title">Resumen del documento:</div>
            <div class="document-summary">
              {{ doc.document_summary }}
            </div>
          </div>
          <div class="document-metadata" v-else>
            <div class="metadata-title">Sin resumen disponible</div>
            <div class="document-summary text-muted">
              Este documento no tiene un resumen generado. Los documentos procesados recientemente incluyen resúmenes automáticos.
            </div>
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
          <button class="button button-danger" @click="deleteDocument" :disabled="isDeleting">
            <span v-if="isDeleting">Eliminando...</span>
            <span v-else>Eliminar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de éxito -->
    <div v-if="showSuccessModal" class="modal-overlay success-modal">
      <div class="modal-content success-content" @click.stop>
        <div class="success-icon mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
          </svg>
        </div>
        <h3>¡Operación exitosa!</h3>
        <p>{{ successMessage }}</p>
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
      refreshInterval: null,
      showDeleteModal: false,
      showSuccessModal: false,
      documentToDelete: null,
      successMessage: '',
      isDeleting: false,
    }
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
        // Cambiar el cursor a 'wait' para indicar que está procesando
        document.body.style.cursor = 'wait';
        this.isDeleting = true;
        
        // Realizar la solicitud de eliminación
        const response = await axios.delete(`/api/documents/${this.documentToDelete}`);
        
        // Cerrar el modal de confirmación
        this.showDeleteModal = false;
        
        if (response.data && (response.data.status === 'success' || response.data.status === 'warning')) {
          // Mostrar mensaje de éxito
          this.successMessage = `Documento "${this.documentToDelete}" eliminado correctamente`;
          this.showSuccessModal = true;
          
          // Actualizar estadísticas y lista completa de documentos
          await this.refreshDocuments();
          
          // Configurar temporizador para cerrar automáticamente el mensaje
          setTimeout(() => {
            this.showSuccessModal = false;
            this.successMessage = '';
          }, 2000);
        }
      } catch (error) {
        console.error('Error eliminando documento:', error);
        this.error = error.response?.data?.detail || error.message;
        // Mostrar algún error visual si es necesario
        this.showDeleteModal = false;
      } finally {
        // Restaurar el cursor
        document.body.style.cursor = 'default';
        this.isDeleting = false;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-item {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s ease;
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.expanded-doc-item {
  padding: 1rem;
}

.document-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.document-name-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.document-name {
  font-weight: 600;
}

.document-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-muted);
}

.document-date {
  white-space: nowrap;
}

.chunks-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  background-color: var(--secondary-bg);
  padding: 0.15rem 0.5rem;
  border-radius: 1rem;
}

.document-type-badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 1rem;
  background-color: #e9ecef;
  color: #495057;
}

.document-type-resume {
  background-color: #cff4fc;
  color: #055160;
}

.document-metadata {
  background-color: #f8f9fa;
  border-radius: 0.375rem;
  padding: 0.75rem 1rem;
  margin-top: 0.75rem;
  border-left: 3px solid #dee2e6;
}

.metadata-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.document-summary {
  font-size: 0.875rem;
  line-height: 1.5;
  color: #212529;
  word-break: break-word;
}

.badge {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 1rem;
  background-color: var(--badge-bg);
  color: var(--badge-text);
}

.badge-success {
  background-color: #d1e7dd;
  color: #0a3622;
}

.badge-warning {
  background-color: #fff3cd;
  color: #664d03;
}

.badge-error {
  background-color: #f8d7da;
  color: #842029;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  transition: all 0.15s ease-in-out;
  cursor: pointer;
}

.button-icon {
  padding: 0.375rem;
}

.button-secondary {
  background-color: var(--secondary-bg);
  color: var(--secondary-text);
  border-color: var(--border-color);
}

.button-secondary:hover {
  background-color: var(--secondary-hover-bg);
}

.button-danger {
  background-color: #f8d7da;
  color: #842029;
  border-color: #f5c2c7;
}

.button-danger:hover {
  background-color: #f5c2c7;
}

.loading-spinner {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  border: 0.25rem solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  color: var(--border-color);
}

.stats-container {
  border-bottom: 1px solid var(--border-color);
  padding: 1rem;
}

.stat-card {
  flex: 1;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
}

.stat-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.text-sm {
  font-size: 0.875rem;
}

.text-muted {
  color: var(--text-muted);
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
  z-index: 999;
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: 0.5rem;
  padding: 1.5rem;
  max-width: 30rem;
  width: 100%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.success-modal {
  background-color: rgba(0, 0, 0, 0.8);
}

.success-content {
  background-color: var(--card-bg);
  text-align: center;
  padding: 2rem;
  border-radius: 0.5rem;
}

.success-icon {
  color: #198754;
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