<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from '@/api/room.api';
import { useWebSocket } from '@/api/websocket';
import { useNotifications } from '@/composables/useNotifications';
import { apolloClient } from '@/api/apollo.client';
import { inject } from 'vue';
import Message from '@/components/Message.vue';

import {
  ROOM_QUERY
} from '@/api/graphql/room.queries';

const Swal = inject('$swal');
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const notifications = useNotifications();
const { deleteRoom, joinRoom } = useRoomApi();

const room = ref(null);
const loading = ref(false);
const messageInput = ref('');
const messagesContainerRef = ref(null);

const {
  messages,
  initializeWebSocket,
  sendMessage: sendWebSocketMessage,
  deleteMessage: deleteWebSocketMessage,
  updateMessage: updateWebSocketMessage,
  closeWebSocket,
} = useWebSocket(route.params.hostSlug, route.params.roomSlug);

const isHost = computed(() => {
  return room.value?.host?.id === authStore.user?.id;
});

const isParticipant = computed(() => {
  if (!room.value || !authStore.user) return false;
  return room.value.participants.some(p => p.id === authStore.user.id);
});

const canSendMessage = computed(() => {
  return authStore.isAuthenticated && (isHost.value || isParticipant.value);
});

async function fetchRoom() {
  try {
    loading.value = true;
    const { data } = await apolloClient.query({
      query: ROOM_QUERY,
      variables: route.params,
      fetchPolicy: 'network-only'
    });
    room.value = data.room;
  } catch (error) {
    notifications.error(error);
    router.push('/');
  } finally {
    loading.value = false;
  }
}

async function handleMessageDelete(messageId) {
  try {
    const success = await deleteWebSocketMessage(messageId);
    
    if (!success) {
      notifications.warning('Failed to delete message. WebSocket connection may be lost.');
    }
  } catch (error) {
    notifications.error('Error deleting message: ' + error.message);
  }
}

async function handleMessageUpdate(messageId, newBody) {
  try {
    const success = await updateWebSocketMessage(messageId, newBody);
    
    if (!success) {
      notifications.warning('Failed to update message. WebSocket connection may be lost.');
    }
  } catch (error) {
    notifications.error('Error updating message: ' + error.message);
  }
}

async function handleRoomDelete() {
  const result = await Swal.fire({
        title: '<h3>Are you sure?</h3>',
        html: '<p>You want to delete this room?</p>',
        background: '#f7f5f4',
        showCloseButton: true,
        closeButtonHtml: '&times;',
        showCancelButton: true,
        showConfirmButton: true,
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        buttonsStyling: false,
        reverseButtons: true,
        customClass: {
            popup: 'minimal-popup',
            confirmButton: 'btn-confirm',
            cancelButton: 'btn-cancel',
            actions: 'center-buttons',
            closeButton: 'close-btn',
        },
    });

  if (result.isConfirmed) {
    await deleteRoom(room.value.host.slug, room.value.slug);
    router.push('/');
  }
}

// Scroll to bottom when messages update
watch(messages, async () => {
  await nextTick();
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight;
  }
});

async function handleJoin() {
    await joinRoom(room.value.host.slug, room.value.slug);
    await fetchRoom();
}

function sendMessage() {
  if (!messageInput.value.trim()) return;
  
  try {
    sendWebSocketMessage(messageInput.value);
    messageInput.value = '';
  } catch (err) {
    notifications.error(err);
  }
}

// Lifecycle hooks
onMounted(async () => {
  try {
    await authStore.initialize();
    await fetchRoom();
    
    await initializeWebSocket();
  } catch (error) {
    notifications.error(error);
  }
});

onBeforeUnmount(() => {
  closeWebSocket();
});
</script>

<template>
  <div class="room-container">
    <!-- Loading state -->
    <div v-if="loading || authStore.isLoadingUser" class="room-loading">
      <div class="spinner"></div>
      <p>Loading room...</p>
    </div>
    
    <!-- Room content -->
    <div v-else-if="room" class="room-content">
      <!-- Room header -->
      <div class="room-header">
        <div class="room-header-left">
          <button @click="$router.push('/')" class="back-button">
            <font-awesome-icon icon="arrow-left" />
            Back
          </button>
          <h2>{{ room.name }}</h2>
          <span class="room-topic" v-if="room.topic">{{ room.topic.name }}</span>
        </div>
        
        <div class="room-header-right">
          <button v-if="isHost" @click="handleRoomDelete" class="delete-button">
            Delete
          </button>
          <button v-if="!isParticipant && authStore.isAuthenticated" @click="handleJoin" class="join-button">
            Join Room
          </button>
        </div>
      </div>
      
      <!-- Room conversation -->
      <div class="room-conversation">
        <div ref="messagesContainerRef" class="messages-container">
          <Message 
            v-for="message in messages" 
            :key="message.id" 
            :message="message"
            :current-user-id="authStore.user?.id"
            @delete-message="handleMessageDelete"
            @update-message="handleMessageUpdate"
          />
        </div>
        
        <!-- Message input -->
        <div v-if="canSendMessage" class="message-input-container">
          <form id="messageForm" @submit.prevent="sendMessage">
            <input 
              v-model="messageInput"
              type="text"
              placeholder="Type your message here..."
            />
            <button type="submit" :disabled="!messageInput.trim()">
              Submit
            </button>
          </form>
        </div>
        <div v-else-if="!authStore.isAuthenticated" class="auth-prompt">
          <p>Please <router-link to="/login">login</router-link> to join the conversation</p>
        </div>
        <div v-else class="join-prompt">
          <p>You need to join this room to participate in the conversation</p>
          <button @click="handleJoin" class="join-button">
            Join Room
          </button>
        </div>
      </div>
    </div>
    
    <!-- Error state -->
    <div v-else class="room-error">
      <p>Room not found or you don't have access.</p>
      <router-link to="/">Go back to home</router-link>
    </div>
  </div>
</template>

<style scoped>
/* Existing styles remain the same */
.room-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.room-loading, .room-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.room-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.room-header-left {
  display: flex;
  align-items: center;
}

.back-button {
  margin-right: 1rem;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
}

.room-topic {
  margin-left: 1rem;
  background-color: #f0f0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.delete-button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.join-button {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.room-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.message-input-container {
  padding: 1rem;
  border-top: 1px solid #eee;
  background-color: #f9f9f9;
}

.message-input-container form {
  display: flex;
  gap: 0.5rem;
}

.message-input-container input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.message-input-container button {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.message-input-container button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.auth-prompt, .join-prompt {
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #eee;
}
</style>

<style>
.minimal-popup {
    width: 425px;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #BDC3C7;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.center-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
}

.btn-confirm {
    background-color: #f34075;
    color: #ffffff;
    font-family: Open Sans, sans-serif;
    font-size: 14px;
    font-weight: bold;
    padding: 15px 30px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.btn-confirm:hover {
    background-color: #d53064;
}

.btn-cancel {
    background-color: #f7f5f4;
    color: #2C3E50;
    font-family: Montserrat, sans-serif;
    font-size: 14px;
    font-weight: bold;
    padding: 15px 30px;
    border: 1px solid black;
    border-radius: 5px;
    cursor: pointer;
}

.btn-cancel:hover {
    background-color: #e6e3e2;
}


.minimal-popup h3 {
    color: #2C3E50;
    font-size: 24px;
    font-family: Montserrat, sans-serif;
    font-weight: bold;
    margin: 0 0 10px;
    margin-bottom: 10px;
}

.minimal-popup p {
    color: #2C3E50;
    font-size: 14px;
    font-family: Open Sans, sans-serif;
    margin: 0 0 20px;
    margin-bottom: 10px;
}

.close-btn {
    font-size: 30px;
    color: #2C3E50;
    font-weight: bold;
    position: absolute;
    cursor: pointer;
    background-color: transparent;
    border-radius: 5px;
}

.close-btn:hover {
    color: #1A252F;
    background-color: #ececec;
}
</style>