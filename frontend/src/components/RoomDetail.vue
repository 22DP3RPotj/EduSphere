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
  closeWebSocket,
} = useWebSocket(route.params.hostSlug, route.params.roomSlug);

// Queries remain the same as in your previous implementation


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

async function handleMessageDelete(messageId) {
  const success = await deleteMessage(messageId);
  
  if (success) {
    messages.value = messages.value.filter(msg => msg.id !== messageId);
  }
}

async function handleRoomDelete() {
  const result = await Swal.fire({
    title: 'Are you sure?',
    text: 'Do you want to delete this room?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
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

// Modified send message to use WebSocket hook
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
