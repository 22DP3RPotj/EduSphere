<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from '@/api/room.api';
import { useWebSocket } from '@/api/websocket';
import { useNotifications } from '@/composables/useNotifications';
import { useApi } from '@/composables/useApi';
import { apolloClient } from '@/api/apollo.client';
import { gql } from '@apollo/client/core';
import { format } from 'timeago.js';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const notifications = useNotifications();
const api = useApi();
const { deleteRoom, joinRoom, deleteMessage } = useRoomApi();

// Room and WebSocket state
const room = ref(null);
const loading = ref(false);
const messageInput = ref('');
const messagesContainerRef = ref(null);

// WebSocket specific state
const {
  messages,
  initializeWebSocket,
  sendMessage: sendWebSocketMessage,
  closeWebSocket
} = useWebSocket(route.params.hostSlug, route.params.roomSlug);

// Queries remain the same as in your previous implementation
const ROOM_QUERY = gql`
  query GetRoom($hostSlug: String!, $roomSlug: String!) {
    room(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      id
      name
      slug
      description
      created
      host {
        id
        username
        slug
        avatar
      }
      participants {
        id
        username
        avatar
      }
      topic {
        name
      }
    }
  }
`;

// Computed properties
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

// Existing methods with minor modifications
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

async function handleRoomDelete() {
  if (!confirm('Are you sure you want to delete this room?')) return;
  
  try {
    await api.call(
      () => deleteRoom(room.value.host.slug, room.value.slug),
      'Room deleted successfully'
    );
    router.push('/');
  } catch (error) {
    // Error handled by api.call
  }
}

async function handleJoin() {
  try {
    await api.call(
      () => joinRoom(room.value.host.slug, room.value.slug),
      'Successfully joined room'
    );
    await fetchRoom();
  } catch (error) {
    // Error handled by api.call
  }
}

// Modified send message to use WebSocket hook
function sendMessage() {
  if (!messageInput.value.trim()) return;
  
  sendWebSocketMessage(messageInput.value);
  messageInput.value = '';
}

// Lifecycle hooks
onMounted(async () => {
  try {
    await authStore.initialize();
    await fetchRoom();
    
    // Initialize WebSocket
    await initializeWebSocket();
  } catch (error) {
    notifications.error(error);
  }
});

// Cleanup WebSocket on component unmount
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
            <i class="fas fa-arrow-left"></i>
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
          <div 
            v-for="message in messages" 
            :key="message.id" 
            class="message-item"
          >
            <div class="message-header">
              <div class="message-author">
                <img :src="message.userAvatar" alt="User avatar" class="avatar-tiny" />
                <span class="username">{{ message.user }}</span>
              </div>
              <div class="message-meta">
                <span class="message-time">{{ message.created }}</span>
              </div>
            </div>
            <div class="message-body">{{ message.body }}</div>
          </div>
        </div>
        
        <!-- Message input -->
        <div v-if="canSendMessage" class="message-input-container">
          <form @submit.prevent="sendMessage">
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
