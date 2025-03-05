<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from '@/api/room.api';
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

const room = ref(null);
const messages = ref([]);
const loading = ref(false);
const messageInput = ref('');
const messagesContainerRef = ref(null);
const socket = ref(null);
const newMessageCount = ref(0);
const userScrolledUp = ref(false);
const highlightedMessageIds = ref(new Set());
const timestampInterval = ref(null);

// Query to fetch room details
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

// Query to fetch room messages
const MESSAGES_QUERY = gql`
  query GetRoomMessages($hostSlug: String!, $roomSlug: String!) {
    messages(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      id
      body
      created
      user {
        id
        username
        slug
        avatar
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

// Methods
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

async function fetchMessages() {
  try {
    const { data } = await apolloClient.query({
      query: MESSAGES_QUERY,
      variables: route.params,
      fetchPolicy: 'network-only'
    });
    messages.value = data.messages;
    
    // Schedule scroll to bottom
    setTimeout(scrollToBottom, 100);
  } catch (error) {
    notifications.error(error);
  }
}

function formatTimestamp(timestamp) {
  return format(new Date(timestamp));
}

// Update all message timestamps every minute
function setupTimestampUpdates() {
  const interval = setInterval(() => {
    // Force update of component to refresh timestamps
    messages.value = [...messages.value];
  }, 60000); // every minute
  
  return interval;
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

function setupWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/room/${route.params.hostSlug}/${route.params.roomSlug}`;

  socket.value = new WebSocket(wsUrl);

  socket.value.onopen = () => {
    console.log('WebSocket connection established');
  };
  
  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Filter out message type events
    if (data.type === 'chat_message') {
      // Create a full message object
      const newMessage = {
        id: data.id,
        body: data.message,
        created: data.created,
        user: {
          id: data.user_id,
          username: data.user,
          avatar: data.user_avatar
        }
      };
      
      // Add message to our list
      messages.value.unshift(newMessage);
      
      // Highlight this message
      highlightNewMessage(data.id);
      
      // If we're not scrolled up, scroll to bottom
      if (!userScrolledUp.value) {
        scrollToBottom();
      } else {
        // Increment unread counter if user has scrolled up
        newMessageCount.value++;
        // Show notification
        showMessageNotification(newMessage);
      }
    }
  };
  
  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error);
    notifications.error('Connection error. Reconnecting...');
    setTimeout(setupWebSocket, 3000);
  };
  
  socket.value.onclose = () => {
    console.log('WebSocket connection closed');
  };
}

function sendMessage() {
  if (!messageInput.value.trim() || !socket.value) return;
  
  socket.value.send(JSON.stringify({
    message: messageInput.value
  }));
  
  messageInput.value = '';
}

function highlightNewMessage(messageId) {
  highlightedMessageIds.value.add(messageId);
  
  // Remove highlight after 2 seconds
  setTimeout(() => {
    highlightedMessageIds.value.delete(messageId);
  }, 2000);
}

function showMessageNotification(message) {
  if (!document.hidden) return; // Don't show notification if page is visible
  
  // Check if browser supports notifications
  if ("Notification" in window) {
    if (Notification.permission === "granted") {
      new Notification(`New message in ${room.value.name}`, {
        body: `${message.user.username}: ${message.body.substring(0, 50)}${message.body.length > 50 ? '...' : ''}`,
        icon: message.user.avatar
      });
    } else if (Notification.permission !== "denied") {
      Notification.requestPermission();
    }
  }
}

function scrollToBottom() {
  if (!messagesContainerRef.value) return;
  
  const container = messagesContainerRef.value;
  container.scrollTop = container.scrollHeight;
  
  // Reset unread counter
  newMessageCount.value = 0;
  userScrolledUp.value = false;
}

function handleScroll(event) {
  if (!messagesContainerRef.value) return;
  
  const container = messagesContainerRef.value;
  const atBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
  
  userScrolledUp.value = !atBottom;
  
  if (atBottom) {
    newMessageCount.value = 0;
  }
}

async function handleDeleteMessage(messageId) {
  try {
    await api.call(
      () => deleteMessage(messageId),
      'Message deleted successfully'
    );
    
    // Remove message from local state
    messages.value = messages.value.filter(msg => msg.id !== messageId);
  } catch (error) {
    // Error is already handled by api.call
  }
}

onMounted(async () => {
  try {
    await authStore.initialize();
    await fetchRoom();
    await fetchMessages();
    
    // Setup WebSocket
    setupWebSocket();
    
    // Setup interval to update timestamps
    timestampInterval.value = setupTimestampUpdates();
  } catch (error) {
    notifications.error(error);
  }
});

// Move cleanup logic to a separate function
function cleanupResources() {
  // Close WebSocket
  if (socket.value) {
    socket.value.close();
    socket.value = null;
  }
  
  // Clear timestamp interval
  if (timestampInterval.value) {
    clearInterval(timestampInterval.value);
    timestampInterval.value = null;
  }
}

// Use onBeforeUnmount correctly
onBeforeUnmount(() => {
  cleanupResources();
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
            <font-awesome-icon :icon="['fas', 'trash']" />
            Delete
          </button>
          <button v-if="!isParticipant && authStore.isAuthenticated" @click="handleJoin" class="join-button">
            Join Room
          </button>
        </div>
      </div>
      
      <!-- Room details -->
      <div class="room-details">
        <div class="room-host">
          <img :src="room.host.avatar" alt="Host avatar" class="avatar-small" />
          <span>Hosted by <strong>{{ room.host.username }}</strong></span>
          <span class="created-at">{{ formatTimestamp(room.created) }}</span>
        </div>
        <p class="room-description" v-if="room.description">{{ room.description }}</p>
      </div>
      
      <!-- Room conversation -->
      <div class="room-conversation">
        <div 
          ref="messagesContainerRef" 
          class="messages-container" 
          @scroll="handleScroll"
        >
          <div 
            v-for="message in messages" 
            :key="message.id" 
            class="message-item"
            :class="{
              'message-own': message.user.id === authStore.user?.id,
              'message-highlighted': highlightedMessageIds.has(message.id)
            }"
          >
            <div class="message-header">
              <div class="message-author">
                <img :src="message.user.avatar" alt="User avatar" class="avatar-tiny" />
                <router-link :to="`/profile/${message.user.slug}`" class="username">
                  {{ message.user.username }}
                </router-link>
              </div>
              <div class="message-meta">
                <span class="message-time">{{ formatTimestamp(message.created) }}</span>
                <button 
                  v-if="message.user.id === authStore.user?.id" 
                  @click="handleDeleteMessage(message.id)" 
                  class="delete-message-btn"
                >
                  <i class="fas fa-times"></i>
                  Delete
                </button>
              </div>
            </div>
            <div class="message-body">{{ message.body }}</div>
          </div>
        </div>
        
        <!-- New messages notification -->
        <div v-if="newMessageCount > 0" class="new-messages-notification" @click="scrollToBottom">
          {{ newMessageCount }} new message{{ newMessageCount > 1 ? 's' : '' }}
          <i class="fas fa-chevron-down"></i>
        </div>
        
        <!-- Message input -->
        <div v-if="canSendMessage" class="message-input-container">
          <form @submit.prevent="sendMessage">
            <input 
              v-model="messageInput" 
              type="text" 
              placeholder="Type your message here..." 
              :disabled="!socket"
            />
            <button type="submit" :disabled="!messageInput.trim() || !socket">
              <i class="fas fa-paper-plane"></i>
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
      
      <!-- Participants sidebar -->
      <div class="participants-sidebar">
        <h3>Participants ({{ room.participants.length }})</h3>
        <div class="participants-list">
          <div v-for="participant in room.participants" :key="participant.id" class="participant-item">
            <span>{{ participant.username }}</span>
          </div>
          <div v-if="room.participants.length === 0" class="no-participants">
            No participants yet
          </div>
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
