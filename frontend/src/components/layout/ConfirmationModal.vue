<template>
  <div v-if="isVisible" class="confirmation-overlay" @click="handleOverlayClick">
    <div class="confirmation-modal" @click.stop>
      <div class="confirmation-container">
        <div class="confirmation-header">
          <h2 class="modal-title">{{ title }}</h2>
        </div>
        
        <div class="confirmation-body">
          <p>{{ message }}</p>
        </div>
        
        <div class="confirmation-actions">
          <button class="btn btn-secondary" @click="handleCancel">
            {{ cancelText }}
          </button>
          <button class="btn btn-danger" @click="handleConfirm">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { watch } from 'vue';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Are you sure?'
  },
  message: {
    type: String,
    default: 'This action cannot be undone.'
  },
  confirmText: {
    type: String,
    default: 'Delete'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  allowOutsideClick: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['confirm', 'cancel', 'close']);

function handleConfirm() {
  emit('confirm');
  emit('close');
}

function handleCancel() {
  emit('cancel');
  emit('close');
}

function handleOverlayClick() {
  if (props.allowOutsideClick) {
    handleCancel();
  }
}

function handleEscapeKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.isVisible) {
    handleCancel();
  }
}

watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    document.addEventListener('keydown', handleEscapeKey);
    document.body.style.overflow = 'hidden';
  } else {
    document.removeEventListener('keydown', handleEscapeKey);
    document.body.style.overflow = '';
  }
});
</script>

<style scoped>
.confirmation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.confirmation-modal {
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.2s ease-out;
}

.confirmation-container {
  padding: 2.5rem;
}

.confirmation-header {
  margin-bottom: 2rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.close-button {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.close-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.confirmation-body {
  margin-bottom: 2.5rem;
}

.confirmation-body p {
  margin: 0;
  color: var(--text-color);
  line-height: 1.5;
  font-size: 1rem;
}

.confirmation-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius);
  font-weight: 500;
  font-size: 1rem;
  transition: var(--transition);
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--border-color);
}

.btn-danger {
  background-color: #f44336;
  color: var(--white);
}

.btn-danger:hover {
  background-color: #b91c1c;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 768px) {
  .confirmation-modal {
    margin: 1rem;
    width: calc(100% - 2rem);
  }

  .confirmation-container {
    padding: 1.5rem;
  }
  
  .confirmation-actions {
    flex-direction: column-reverse;
    gap: 0.75rem;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>