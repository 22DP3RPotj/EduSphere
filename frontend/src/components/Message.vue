<script setup>
import { computed } from 'vue';
import { format } from 'timeago.js';
import { useAuthStore } from '@/stores/auth.store';

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isHost: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['delete-message']);

const authStore = useAuthStore();

const canDeleteMessage = computed(() => {
  return props.isHost || props.message.userId === authStore.user?.id;
});

const formattedTimestamp = computed(() => {
  try {
    // Ensure we're parsing a valid date and using local time
    const date = new Date(props.message.created);
    return format(date);
  } catch (error) {
    return props.message.created;
  }
});

const userDisplayName = computed(() => {
  // Handle both backend and dynamically generated message formats
  return props.message.user?.username || props.message.user || 'Unknown User';
});

const userAvatar = computed(() => {
  if (props.message.userAvatar) return props.message.userAvatar;
  if (props.message.user?.avatar) return `/media/${props.message.user?.avatar}`;
  return '/media/default-avatar.png';
});

function handleMessageDelete() {
  emit('delete-message', props.message.id);
}
</script>

<template>
  <div class="message-item">
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
        </span>
        <button 
          v-if="canDeleteMessage"
          @click="handleMessageDelete"
          class="delete-message-button"
        >
          Delete
        </button>
      </div>
    </div>
    <div class="message-body">{{ props.message.body }}</div>
  </div>
</template>

<style scoped>
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
}

.delete-message-button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
</style>