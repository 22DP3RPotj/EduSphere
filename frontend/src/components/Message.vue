<script setup>
import { computed, ref } from 'vue';
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
  return props.message.user?.username || props.message.user || '[Unknown User]';
});

const userAvatar = computed(() => {
  if (props.message.userAvatar) return props.message.userAvatar;
  if (props.message.user?.avatar) return `/media/${props.message.user?.avatar}`;
  return '/media/default-avatar.png';
});

function handleMessageDelete() {
  emit('delete-message', props.message.id);
}

function startEditing() {
  editBody.value = props.message.body;
  isEditing.value = true;
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
</script>

<template>
  <div class="message-item" :class="{ 'edited': props.message.edited }">
    <div class="message-header">
      <div class="message-author">
        <img 
          :src="userAvatar" 
          alt="User avatar" 
          class="avatar-tiny" 
        />
        <span class="username">{{ userDisplayName }}</span>
      </div>
      <div class="message-meta">
        <span 
          class="message-time" 
          :title="new Date(props.message.created).toLocaleString()"
        >
          {{ formattedTimestamp }}
          <span v-if="props.message.edited" class="edited-indicator">(edited)</span>
        </span>
        
        <div v-if="isMessageOwner" class="message-actions">
          <button 
            v-if="!isEditing"
            @click="startEditing"
            class="edit-message-button"
            title="Edit message"
          >
            Edit
          </button>
          <button 
            v-if="!isEditing"
            @click="handleMessageDelete"
            class="delete-message-button"
            title="Delete message"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
    
    <!-- Message content - edit mode -->
    <div v-if="isEditing" class="message-edit-form">
      <textarea 
        v-model="editBody"
        class="message-edit-input"
        rows="1"
        @keydown.esc="cancelEditing"
        @keydown.enter.prevent="saveEdit"
      ></textarea>
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
</template>

<style scoped>
.message-body {
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
  overflow-x: hidden;
}

.message-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-author {
  display: flex;
  align-items: center;
}

.avatar-tiny {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.message-meta {
  display: flex;
  align-items: center;
}

.message-time {
  margin-right: 0.5rem;
  color: #666;
  font-size: 0.85rem;
}

.edited-indicator {
  font-style: italic;
  margin-left: 5px;
  font-size: 0.8rem;
  color: #999;
}

.message-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-message-button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.delete-message-button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.message-edit-form {
  margin-top: 0.5rem;
}

.message-edit-input {
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  font-family: inherit;
  font-size: inherit;
  resize: none;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.cancel-edit-button {
  background-color: #ddd;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.save-edit-button {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.save-edit-button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}
</style>