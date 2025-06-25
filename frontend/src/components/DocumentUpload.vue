<template>
  <div class="card fade-in">
    <h2>Subir Documentos</h2>
    <p class="text-sm text-muted mb-4">Subí documentos PDF para entrenar al gemelo digital</p>
    
    <div 
      class="upload-container" 
      :class="{ 'active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleFileDrop"
      @click="triggerFileInput"
    >
      <input 
        type="file"
        ref="fileInput"
        accept=".pdf"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <div v-if="!isUploading">
        <div class="upload-icon mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
          </svg>
        </div>
        <h3>Arrastrá un archivo PDF o hacé click para seleccionarlo</h3>
        <p class="text-sm text-muted mt-2">Solo archivos PDF de hasta 10MB</p>
      </div>
      
      <div v-else class="upload-progress">
        <h3>{{ currentFile.name }}</h3>
        <div class="progress-bar mt-4 mb-2">
          <div class="progress-bar-fill" :style="{ width: `${uploadProgress}%` }"></div>
        </div>
        <p>{{ uploadStatus }}</p>
      </div>
    </div>
    
    <!-- Mensajes de error o éxito -->
    <div v-if="message" :class="['alert', `alert-${messageType}`, 'mt-4']">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DocumentUpload',
  emits: ['document-added'],
  data() {
    return {
      isDragging: false,
      isUploading: false,
      currentFile: null,
      uploadProgress: 0,
      uploadStatus: '',
      message: '',
      messageType: 'info', // 'info', 'success', 'error'
      uploadCheckInterval: null
    };
  },
  methods: {
    triggerFileInput() {
      if (!this.isUploading) {
        this.$refs.fileInput.click();
      }
    },
    
    handleFileSelect(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },
    
    handleFileDrop(event) {
      this.isDragging = false;
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },
    
    processFile(file) {
      // Validar que sea un PDF
      if (file.type !== 'application/pdf') {
        this.showMessage('Solo se permiten archivos PDF', 'error');
        return;
      }
      
      // Validar tamaño máximo (10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        this.showMessage('El archivo excede el tamaño máximo de 10MB', 'error');
        return;
      }
      
      // Iniciar upload
      this.uploadFile(file);
    },
    
    async uploadFile(file) {
      try {
        // Preparar datos para el upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Actualizar estado
        this.currentFile = file;
        this.isUploading = true;
        this.uploadProgress = 0;
        this.uploadStatus = 'Preparando archivo...';
        this.message = '';
        
        // Realizar upload
        const response = await axios.post('/api/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round((progressEvent.loaded * 50) / progressEvent.total); // 50% para upload
            this.uploadStatus = 'Subiendo archivo...';
          }
        });
        
        // Verificar respuesta
        if (response.data && response.data.document_id) {
          this.uploadStatus = 'Procesando documento...';
          this.uploadProgress = 50;
          
          // Comenzar a verificar estado de procesamiento
          this.checkProcessingStatus(response.data.document_id);
        } else {
          throw new Error('Respuesta inválida del servidor');
        }
      } catch (error) {
        console.error('Error al subir documento:', error);
        this.isUploading = false;
        this.showMessage(`Error al subir el documento: ${error.response?.data?.detail || error.message}`, 'error');
      }
    },
    
    async checkProcessingStatus(documentId) {
      try {
        // Limpiar intervalo anterior si existe
        if (this.uploadCheckInterval) {
          clearInterval(this.uploadCheckInterval);
        }
        
        // Revisar estado cada 2 segundos
        this.uploadCheckInterval = setInterval(async () => {
          const response = await axios.get(`/api/documents/status/${documentId}`);
          
          if (response.data) {
            const { status, progress, message } = response.data;
            
            // Actualizar progreso
            this.uploadProgress = 50 + (progress * 50); // 50% restante para procesamiento
            this.uploadStatus = message || `Procesando (${Math.round(progress * 100)}%)`;
            
            // Si completó o falló, detener verificación
            if (status === 'completed' || status === 'failed') {
              clearInterval(this.uploadCheckInterval);
              this.isUploading = false;
              
              if (status === 'completed') {
                this.showMessage('¡Documento procesado exitosamente!', 'success');
                // Notificar que se agregó un documento para refrescar la lista
                this.$emit('document-added');
              } else {
                this.showMessage(`Error al procesar el documento: ${message}`, 'error');
              }
            }
          }
        }, 2000);
      } catch (error) {
        console.error('Error verificando estado:', error);
        clearInterval(this.uploadCheckInterval);
        this.isUploading = false;
        this.showMessage('Error al verificar estado del procesamiento', 'error');
      }
    },
    
    showMessage(text, type = 'info') {
      this.message = text;
      this.messageType = type;
      
      // Limpiar mensaje después de unos segundos
      setTimeout(() => {
        this.message = '';
      }, 5000);
    }
  },
  beforeUnmount() {
    // Limpiar intervalo al desmontar componente
    if (this.uploadCheckInterval) {
      clearInterval(this.uploadCheckInterval);
    }
  }
}
</script>

<style scoped>
.upload-icon {
  color: var(--color-primary);
}

.upload-progress {
  width: 100%;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  font-size: 0.875rem;
}

.alert-info {
  background-color: #e0f2fe;
  color: #0369a1;
}

.alert-success {
  background-color: #dcfce7;
  color: #15803d;
}

.alert-error {
  background-color: #fee2e2;
  color: #b91c1c;
}
</style>
