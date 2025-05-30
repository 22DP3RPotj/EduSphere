<script setup>
import { computed, ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { format } from 'timeago.js';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['delete-message', 'update-message']);

const isEditing = ref(false);
const editBody = ref('');
const showActions = ref(false);
const editTextarea = ref(null);

const isMessageOwner = computed(() => {
  return (props.message.user?.id || props.message.user_id) === props.currentUserId;
});

const formattedTimestamp = computed(() => {
  try {
    const date = new Date(props.message.created);
    return format(date);
  } catch (error) {
    return props.message.created;
  }
});

const userDisplayName = computed(() => {
  return props.message.user?.username || props.message.user || '[Unknown]';
});

const userAvatar = computed(() => {
  const avatar = props.message.user?.avatar || props.message.userAvatar;
  return avatar ? `/media/${avatar}` : '/default.svg';
})

function handleMessageDelete() {
  showActions.value = false;
  emit('delete-message', props.message.id);
}

async function startEditing() {
  editBody.value = props.message.body;
  showActions.value = false;
  isEditing.value = true;
  
  await nextTick();
  if (editTextarea.value) {
    editTextarea.value.focus();
    editTextarea.value.setSelectionRange(editBody.value.length, editBody.value.length);
    adjustTextareaHeight({ target: editTextarea.value });
  }
}

function cancelEditing() {
  isEditing.value = false;
  editBody.value = '';
}

function saveEdit() {
  if (editBody.value.trim() && editBody.value !== props.message.body) {
    emit('update-message', props.message.id, editBody.value);
  }
  isEditing.value = false;
}

function toggleActions() {
  showActions.value = !showActions.value;
}

function closeActions(event) {
  if (showActions.value && !event.target.closest('.message-actions')) {
    showActions.value = false;
  }
}

function handleEscKey(event) {
  if (event.key === 'Escape') {
    if (isEditing.value) {
      cancelEditing();
    } else if (showActions.value) {
      showActions.value = false;
    }
  }
}

// Auto-resize textarea
function adjustTextareaHeight(event) {
  const textarea = event.target;
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
}

// Handle keyboard shortcuts in edit mode
function handleEditKeydown(event) {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault();
    saveEdit();
  } else if (event.key === 'Escape') {
    event.preventDefault();
    cancelEditing();
  }
}

onMounted(() => {
  document.addEventListener('click', closeActions);
  document.addEventListener('keydown', handleEscKey);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', closeActions);
  document.removeEventListener('keydown', handleEscKey);
});
</script>

<template>
  <div class="message-item" :class="{ 'edited': props.message.edited, 'own-message': isMessageOwner }">
    <div class="message-avatar">
      <img 
        :src="userAvatar" 
        :alt="`${userDisplayName}'s avatar`" 
        class="avatar-img" 
      />
    </div>
    <div class="message-content">
      <div class="message-header">
        <div class="message-author">
          <span class="username">{{ userDisplayName }}</span>
          <span 
            class="message-time" 
            :title="new Date(props.message.created).toLocaleString()"
          >
            {{ formattedTimestamp }}
            <span v-if="props.message.edited" class="edited-indicator">(edited)</span>
          </span>
        </div>
        
        <div v-if="isMessageOwner && !isEditing" class="message-actions">
          <button 
            @click="toggleActions"
            class="action-toggle-button"
            :class="{ 'active': showActions }"
          >
            <font-awesome-icon icon="ellipsis-v" />
          </button>
          
          <transition name="dropdown">
            <div v-if="showActions" class="action-dropdown">
              <button 
                @click="startEditing"
                class="dropdown-action"
              >
                <font-awesome-icon icon="edit" class="action-icon" />
                Edit
              </button>
              <button 
                @click="handleMessageDelete"
                class="dropdown-action delete-action"
              >
                <font-awesome-icon icon="trash" class="action-icon" />
                Delete
              </button>
            </div>
          </transition>
        </div>
      </div>
      
      <!-- Message content - edit mode -->
      <div v-if="isEditing" class="message-edit-form">
        <textarea 
          ref="editTextarea"
          v-model="editBody"
          class="message-edit-input"
          rows="1"
          @input="adjustTextareaHeight"
          @keydown="handleEditKeydown"
          placeholder="Edit your message..."
        ></textarea>
        <div class="edit-hint">Press Ctrl+Enter to save, Esc to cancel</div>
        <div class="edit-actions">
          <button @click="cancelEditing" class="cancel-edit-button">
            Cancel
          </button>
          <button @click="saveEdit" class="save-edit-button" :disabled="!editBody.trim()">
            Save
          </button>
        </div>
      </div>
      
      <!-- Message content - display mode -->
      <div v-else class="message-body">{{ props.message.body }}</div>
    </div>
  </div>
</template>

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 1rem;
  position: relative;
}

.message-avatar {
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  flex: 1;
  min-width: 0; /* Ensures text wrapping works properly */
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.25rem;
}

.message-author {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.username {
  font-weight: 600;
  color: var(--text-color);
}

.message-time {
  color: var(--text-light);
  font-size: 0.75rem;
}

.edited-indicator {
  font-style: italic;
  margin-left: 2px;
  font-size: 0.7rem;
  color: var(--text-light);
}

.message-body {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text-color);
  line-height: 1.5;
  max-width: 100%;
  overflow-x: hidden;
  padding: 0.25rem 0;
}

.message-actions {
  position: relative;
}

.action-toggle-button {
  background: none;
  border: none;
  color: var(--text-light);
  padding: 0.25rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-toggle-button:hover,
.action-toggle-button.active {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.action-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  width: 120px;
  background-color: var(--white);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  z-index: 10;
}

.dropdown-action {
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: var(--transition);
  color: var(--text-color);
}

.dropdown-action:hover {
  background-color: var(--bg-color);
}

.action-icon {
  margin-right: 0.5rem;
  font-size: 0.8rem;
}

.delete-action {
  color: var(--error-color);
}

.message-edit-form {
  margin-top: 0.5rem;
}

.message-edit-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 0.5rem;
  font-family: inherit;
  font-size: inherit;
  resize: none;
  overflow-y: hidden;
  min-height: 38px;
  transition: var(--transition);
}

.message-edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.edit-hint {
  font-size: 0.75rem;
  color: var(--text-light);
  margin: 0.25rem 0 0.5rem;
  text-align: right;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.cancel-edit-button {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
}

.cancel-edit-button:hover {
  background-color: var(--bg-color);
}

.save-edit-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
}

.save-edit-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.save-edit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Styling for own messages */
.own-message {
  justify-content: flex-start;
}

.own-message .message-body {
  color: var(--text-color);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
</style>