<template>
  <div
    class="message-item"
    :class="{ 
      'edited': props.message.edited, 
      'own-message': isMessageOwner,
      'host-message': props.isHost 
  }">
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
          <span v-if="props.isHost" class="host-badge">Host</span>
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
            class="action-toggle-button"
            :class="{ 'active': showActions }"
            @click="toggleActions"
          >
            <font-awesome-icon icon="ellipsis-v" />
          </button>
          
          <transition name="dropdown">
            <div v-if="showActions" class="action-dropdown">
              <button 
                class="dropdown-action"
                @click="startEditing"
              >
                <font-awesome-icon icon="edit" class="action-icon" />
                Edit
              </button>
              <button 
                class="dropdown-action delete-action"
                @click="handleMessageDelete"
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
          placeholder="Edit your message..."
          @input="adjustTextareaHeight"
          @keydown="handleEditKeydown"
        ></textarea>
        <div class="edit-hint">Press Ctrl+Enter to save, Esc to cancel</div>
        <div class="edit-actions">
          <button class="cancel-edit-button" @click="cancelEditing">
            Cancel
          </button>
          <button class="save-edit-button" :disabled="!editBody.trim()" @click="saveEdit">
            Save
          </button>
        </div>
      </div>
      
      <!-- Message content - display mode -->
      <div v-else class="message-body">{{ props.message.body }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
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
  },
  isHost: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['delete-message', 'update-message']);

const isEditing = ref<boolean>(false);
const editBody = ref<string>('');
const showActions = ref<boolean>(false);
const editTextarea = ref<HTMLTextAreaElement | null>(null);

const isMessageOwner = computed(() => {
  return (props.message.user?.id || props.message.user_id) === props.currentUserId;
});

const formattedTimestamp = computed(() => {
  try {
    const date = new Date(props.message.created);
    return format(date);
  } catch {
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
    adjustTextareaHeight(editTextarea.value);
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

function closeActions(event: MouseEvent) {
  if (showActions.value && !(event.target as HTMLElement).closest('.message-actions')) {
    showActions.value = false;
  }
}

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    if (isEditing.value) {
      cancelEditing();
    } else if (showActions.value) {
      showActions.value = false;
    }
  }
}

function adjustTextareaHeight(eventOrElement: Event | HTMLTextAreaElement) {
  let textarea: HTMLTextAreaElement | null = null;
  if (eventOrElement instanceof Event) {
    textarea = eventOrElement.target as HTMLTextAreaElement;
  } else {
    textarea = eventOrElement;
  }
  if (textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
}

function handleEditKeydown(event: KeyboardEvent) {
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

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 1rem;
  position: relative;
}

/* Own message styling - move to right */
.own-message {
  flex-direction: row-reverse;
  justify-content: flex-start;
}

.own-message .message-avatar {
  margin-left: 0.75rem;
  margin-right: 0;
}

.own-message .message-content {
  text-align: right;
  max-width: 70%;
}

.own-message .message-header {
  flex-direction: row-reverse;
}

.own-message .message-author {
  flex-direction: row-reverse;
}

.message-body {
  background-color: var(--border-color);
  color: var(--text-color);
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  border-bottom-left-radius: 0.25rem;
  max-width: 100%;
  word-break: break-word;
}

.own-message .message-body {
  text-align: left;
  border-bottom-right-radius: 0.25rem
}

.message-item:not(.own-message) .message-body {
  text-align: right;
  border-bottom-left-radius: 0.25rem
}

.own-message .edit-actions {
  justify-content: flex-start;
}

/* Regular message styling */
.message-item:not(.own-message) .message-content {
  max-width: 70%;
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
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
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

.host-badge {
  font-size: 0.7rem;
  color: var(--primary-color);
  background-color: rgba(79, 70, 229, 0.1);
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.own-message .host-badge {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.message-time {
  color: var(--text-light);
  font-size: 0.75rem;
}

.own-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.edited-indicator {
  font-style: italic;
  margin-left: 2px;
  font-size: 0.7rem;
  color: var(--text-light);
}

.own-message .edited-indicator {
  color: rgba(255, 255, 255, 0.7);
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

.own-message .action-dropdown {
  right: auto;
  left: 0;
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
  background-color: var(--bg-color);
  color: var(--text-color);
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

.own-message .edit-hint {
  text-align: left;
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

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .own-message .message-content,
  .message-item:not(.own-message) .message-content {
    max-width: 85%;
  }
}
</style>
