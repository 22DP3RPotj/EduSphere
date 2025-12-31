<template>
  <div class="room-container">
    <!-- Edit Form Modal -->
    <div v-if="showEditForm" class="edit-modal-overlay" @click="handleEditCancel">
      <div class="edit-modal-content" @click.stop>
        <EditRoomForm 
          :room="room"
          @cancel="handleEditCancel"
          @updated="handleEditComplete"
        />
      </div>
    </div>

    <ConfirmationModal
      :is-visible="showDeleteConfirmation"
      title="Are you sure?"
      message="You want to delete this room?"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmRoomDeletion"
      @cancel="cancelRoomDeletion"
      @close="cancelRoomDeletion"
    />

    <!-- Loading state -->
    <div v-if="loading" class="room-loading">
      <div class="spinner"></div>
      <p>Loading room...</p>
    </div>
    
    <!-- Room content -->
    <div v-else-if="room" class="room-content">
      <!-- Room header -->
      <div class="room-header">
        <div class="room-header-left">
          <button class="back-button" @click="$router.back()">
            <font-awesome-icon icon="arrow-left" />
          </button>
          <h2>{{ room.name }}</h2>
          <div class="room-topics">
            <span 
              v-for="topic in room.topics" 
              :key="topic.name" 
              class="room-topic"
            >
              {{ topic.name }}
            </span>
          </div>
          <span class="participants-count">
            <font-awesome-icon icon="users" /> {{ participants.length }}
          </span>
          
          <!-- Connection status -->
          <div
            v-if="canSendMessage" 
            class="connection-dot" 
            :class="connectionStatus"
            :title="connectionStatusTitle"
            @click="(connectionStatus === 'error' || connectionStatus === 'disconnected') && retryWebSocketConnection()"
          ></div>
        </div>
        
        <div class="room-header-right">
          <button v-if="isMobileView" class="sidebar-toggle" @click="toggleSidebar">
            <font-awesome-icon :icon="showSidebar ? 'times' : 'users'" />
          </button>
          
          <!-- Room Actions Menu for Host -->
          <div v-if="isHost" class="room-actions-menu" @click.stop>
            <button class="room-actions-button" @click="toggleRoomActionsMenu">
              <font-awesome-icon icon="ellipsis-vertical" />
            </button>
            <div v-if="showRoomActionsMenu" class="room-actions-dropdown">
              <button class="room-action-item" @click="handleEditRoom">
                <font-awesome-icon icon="edit" />
                <span>Edit Room</span>
              </button>
              <button class="room-action-item delete-action" @click="handleRoomDelete">
                <font-awesome-icon icon="trash" />
                <span>Delete Room</span>
              </button>
            </div>
          </div>
          
          <button v-if="!isParticipant && authStore.isAuthenticated" class="join-button" @click="handleJoin">
            Join Room
          </button>
        </div>
      </div>
      
      <!-- Error display for room operations -->
      <div v-if="roomErrors.generalErrors.length > 0" class="error-message room-error-banner">
        <font-awesome-icon icon="exclamation-circle" />
        <div class="error-list">
          <p v-for="(errMsg, index) in roomErrors.generalErrors" :key="index">{{ errMsg }}</p>
        </div>
        <button class="btn-retry" @click="retryRoomOperations">Retry</button>
      </div>

      <!-- Error display for WebSocket -->
      <div v-if="websocketErrors.generalErrors.length > 0" class="error-message websocket-error-banner">
        <font-awesome-icon icon="exclamation-triangle" />
        <div class="error-list">
          <p v-for="(errMsg, index) in websocketErrors.generalErrors" :key="index">{{ errMsg }}</p>
        </div>
        <button class="btn-retry" @click="retryWebSocketConnection">Reconnect</button>
      </div>
      
      <!-- Main content area with sidebar and conversation -->
      <div class="room-main-content">
        <!-- Sidebar with participants -->
        <div class="room-sidebar" :class="{ 'sidebar-visible': showSidebar, 'mobile-sidebar': isMobileView }">
          <div class="sidebar-header">
            <h3 class="sidebar-title">Participants</h3>
            <button v-if="isMobileView" class="close-sidebar-button" @click="toggleSidebar">
              <font-awesome-icon icon="times" />
            </button>
          </div>
          <div class="participants-list">
            <div 
              v-for="participant in participants" 
              :key="participant.id" 
              class="participant-item"
              @click="navigateToUserProfile(participant.username)"
            >
              <img 
                :src="participant.avatar ? `/media/${participant.avatar}` : '/default.svg'" 
                :alt="`${participant.username}`"
                class="participant-avatar"
              />
              <div class="participant-info">
                <span class="participant-name">{{ participant.username }}</span>
                <span v-if="participant.isHost" class="host-badge">Host</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Room conversation -->
        <div class="room-conversation">
          <div ref="messagesContainerRef" class="messages-container">
            <!-- Error state for messages -->
            <div v-if="messageErrors.generalErrors.length > 0" class="error-state">
              <font-awesome-icon icon="exclamation-triangle" size="2x" />
              <p>Failed to load messages</p>
              <button class="btn-retry" @click="retryMessages">Retry</button>
            </div>

            <!-- Messages content -->
            <MessageView
              v-for="message in messages" 
              :key="message.id" 
              :message="message"
              :current-user-id="authStore.user?.id"
              :is-host="message.user.id === room?.host?.id"
              @delete-message="handleMessageDelete"
              @update-message="handleMessageUpdate"
            />
          </div>
          
          <!-- Message input -->
          <div v-if="canSendMessage" class="message-input-container">
            <!-- Error display for message operations -->
            <div v-if="messageOperationErrors.generalErrors.length > 0" class="error-message message-error">
              <font-awesome-icon icon="exclamation-circle" />
              <div class="error-list">
                <p v-for="(errMsg, index) in messageOperationErrors.generalErrors" :key="index">{{ errMsg }}</p>
              </div>
            </div>

            <form id="messageForm" @submit.prevent="sendMessage">
              <div class="input-wrapper">
                <input 
                  id="messageInput"
                  v-model="messageInput"
                  type="text"
                  maxlength="2048"
                  placeholder="Type your message here..."
                />
                <div class="char-count" :class="{ 'char-limit-warning': messageInput.length === 500 }">
                  {{ messageInput.length }}/2048
                </div>
              </div>
              <button type="submit" :disabled="!messageInput.trim()">
                <font-awesome-icon icon="paper-plane" />
              </button>
            </form>
          </div>
          <div v-else-if="!authStore.isAuthenticated" class="auth-prompt">
            <p>Please <router-link to="/login">login</router-link> to join the conversation</p>
          </div>
          <div v-else class="join-prompt">
            <p>You need to join this room to participate in the conversation</p>
            <button class="join-button" @click="handleJoin">
              Join Room
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error state -->
    <div v-else class="room-error">
      <font-awesome-icon icon="door-closed" size="3x" />
      <p>Room not found or you don't have access.</p>
      <router-link to="/" class="btn-home">Go back to home</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomQuery, useRoomMessagesQuery, useDeleteRoom, useJoinRoom } from '@/composables/useRooms';
import { useWebSocket } from '@/composables/useWebSocket';
import { parseGraphQLError } from '@/utils/errorParser';

import MessageView from '@/components/common/MessageView.vue';
import EditRoomForm from '@/components/forms/EditRoom.vue';
import ConfirmationModal from '@/components/layout/ConfirmationModal.vue';
import type { User, Room, Participant } from '@/types';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const hostSlug = route.params.hostSlug as string;
const roomSlug = route.params.roomSlug as string;

const messageInput = ref<string>('');
const messagesContainerRef = ref<HTMLElement | null>(null);
const showSidebar = ref<boolean>(window.innerWidth > 768);
const isMobileView = ref<boolean>(window.innerWidth <= 768);
const showEditForm = ref<boolean>(false);
const showRoomActionsMenu = ref<boolean>(false);
const showDeleteConfirmation = ref<boolean>(false);
const isWebSocketInitialized = ref<boolean>(false);

// Use WebSocket messages when available, otherwise use initial GraphQL messages
const messages = computed(() => {
  return websocketMessages.value.length > 0 ? websocketMessages.value : initialMessages.value;
});

const shouldShowMessages = computed(() => {
  return isParticipant.value;
});

// Error handling
const roomErrors = computed(() => {
  const errors = [];
  if (roomError.value) errors.push(roomError.value);
  if (deleteError.value) errors.push(deleteError.value);
  if (joinError.value) errors.push(joinError.value);
  
  if (errors.length === 0) return { fieldErrors: {}, generalErrors: [] };
  
  const combinedError = new Error(errors.map(err => err.message).join('; '));
  return parseGraphQLError(combinedError);
});

const messageErrors = computed(() => {
  if (!messagesError.value || !shouldShowMessages.value) return { fieldErrors: {}, generalErrors: [] };
  return parseGraphQLError(messagesError.value);
});

const websocketErrors = computed(() => {
  if (!websocketError.value) return { fieldErrors: {}, generalErrors: [] };
  return { fieldErrors: {}, generalErrors: [websocketError.value] };
});

const messageOperationErrors = ref<{ fieldErrors: Record<string, string[]>; generalErrors: string[] }>({ 
  fieldErrors: {}, 
  generalErrors: [] 
});

const connectionStatusTitle = computed(() => {
  switch (connectionStatus.value) {
    case 'connected': return 'Connected to chat';
    case 'connecting': return 'Connecting to chat...';
    case 'error': return 'Connection error - click to reconnect';
    case 'disconnected': return 'Disconnected - click to reconnect';
    default: return 'Connection status unknown';
  }
});

const loading = computed(() => roomLoading.value || messagesLoading.value || deleteLoading.value || joinLoading.value);

const isHost = computed(() => {
  return room.value?.host?.id === authStore.user?.id;
});

const canSendMessage = computed(() => {
  return authStore.isAuthenticated && isParticipant.value;
});

type ParticipantWithHost = Room['participants'][number] & { isHost?: boolean };

const participants = computed<ParticipantWithHost[]>(() => {
  if (!room.value) return [];
  
  const allParticipants: ParticipantWithHost[] = [...room.value.participants];

  // Mark the host in the existing participants list
  const hostIndex = allParticipants.findIndex(p => p.id === room.value!.host.id);
  if (hostIndex !== -1) {
    allParticipants[hostIndex] = {
      ...allParticipants[hostIndex],
      isHost: true
    } as User;
  }
  
  return allParticipants;
});

const isParticipant = computed(() => {
  const user = authStore.user;
  if (!room.value || !user || !room.value.participants) return false;
  
  return room.value.participants.some((p: Participant) => p.user.id === user.id);
});

const { 
  room, 
  loading: roomLoading, 
  error: roomError, 
  refetch: refetchRoom 
} = useRoomQuery(hostSlug, roomSlug);

const { 
  messages: initialMessages, 
  loading: messagesLoading, 
  error: messagesError,
  refetch: refetchMessages 
} = useRoomMessagesQuery(hostSlug, roomSlug, { enabled: isParticipant });

const { 
  deleteRoom: deleteRoomMutation, 
  loading: deleteLoading, 
  error: deleteError 
} = useDeleteRoom();

const { 
  joinRoom: joinRoomMutation, 
  loading: joinLoading, 
  error: joinError 
} = useJoinRoom();

const {
  messages: websocketMessages,
  initializeWebSocket,
  sendMessage: sendWebSocketMessage,
  deleteMessage: deleteWebSocketMessage,
  updateMessage: updateWebSocketMessage,
  closeWebSocket,
  connectionError: websocketError,
  connectionStatus,
  isConnected
} = useWebSocket(hostSlug, roomSlug);

// Error recovery functions
function retryRoomOperations() {
  refetchRoom();
}

async function retryWebSocketConnection() {
  if (authStore.isAuthenticated && isParticipant.value && room.value) {
    clearMessageOperationErrors();
    
    closeWebSocket();
    isWebSocketInitialized.value = false;
    
    // Reconnection delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    try {
      await initializeWebSocket();
      isWebSocketInitialized.value = true;
      
      console.log('WebSocket reconnected successfully');
    } catch (error) {
      console.error('Failed to reconnect WebSocket:', error);
      isWebSocketInitialized.value = false;
    }
  }
}

function retryMessages() {
  refetchMessages();
}

function clearMessageOperationErrors() {
  messageOperationErrors.value = { fieldErrors: {}, generalErrors: [] };
}

async function handleMessageDelete(messageId: string) {
  clearMessageOperationErrors();
  try {
    const success = deleteWebSocketMessage(messageId);
    
    if (!success) {
      messageOperationErrors.value = {
        fieldErrors: {},
        generalErrors: ['Failed to delete message. Please try again.']
      };
    }
  } catch (error) {
    messageOperationErrors.value = parseGraphQLError(error);
  }
}

async function handleMessageUpdate(messageId: string, newBody: string) {
  clearMessageOperationErrors();
  try {
    const success = updateWebSocketMessage(messageId, newBody);
    
    if (!success) {
      messageOperationErrors.value = {
        fieldErrors: {},
        generalErrors: ['Failed to update message. Please try again.']
      };
    }
  } catch (error) {
    messageOperationErrors.value = parseGraphQLError(error);
  }
}

async function handleRoomDelete() {
  showRoomActionsMenu.value = false;
  showDeleteConfirmation.value = true;
}

async function confirmRoomDeletion() {
  showDeleteConfirmation.value = false;
  clearMessageOperationErrors();

  if (!room.value) return;

  const result = await deleteRoomMutation(room.value.id);
  if (result.success) {
    router.push('/');
  } else {
    messageOperationErrors.value = {
      fieldErrors: {},
      generalErrors: [result.error || 'Failed to delete room']
    };
  }
}

function cancelRoomDeletion() {
  showDeleteConfirmation.value = false;
}

function handleEditRoom() {
  showRoomActionsMenu.value = false;
  showEditForm.value = true;
}

function handleEditCancel() {
  showEditForm.value = false;
}

async function handleEditComplete() {
  showEditForm.value = false;
}

function toggleRoomActionsMenu() {
  showRoomActionsMenu.value = !showRoomActionsMenu.value;
}

function closeRoomActionsMenu() {
  showRoomActionsMenu.value = false;
}

function handleResize() {
  isMobileView.value = window.innerWidth <= 768;
  
  if (!isMobileView.value) {
    showSidebar.value = true;
  } else if (!showSidebar.value) {
    showSidebar.value = false;
  }
}

function toggleSidebar() {
  if (isMobileView.value) {
    showSidebar.value = !showSidebar.value;
  }
}

async function handleJoin() {
  if (!room.value) return;
  
  clearMessageOperationErrors();

  const result = await joinRoomMutation(room.value.id);
  if (result.success) {
    await refetchRoom();
    
    nextTick(() => {
      scrollToBottom();
    });
  } else {
    messageOperationErrors.value = {
      fieldErrors: {},
      generalErrors: [result.error || 'Failed to join room']
    };
  }
}

function sendMessage() {
  if (!messageInput.value.trim()) return;
  
  clearMessageOperationErrors();

  if (!isConnected.value) {
    messageOperationErrors.value = {
      fieldErrors: {},
      generalErrors: ['Connection not ready. Please wait a moment.']
    };
    return;
  }
  
  try {
    const success = sendWebSocketMessage(messageInput.value);
    if (success) {
      messageInput.value = '';
    } else {
      messageOperationErrors.value = {
        fieldErrors: {},
        generalErrors: ['Failed to send message. Please try again.']
      };
    }
  } catch (err) {
    messageOperationErrors.value = {
      fieldErrors: {},
      generalErrors: ['Failed to send message: ' + (err instanceof Error ? err.message : String(err))]
    };
  }
}

function navigateToUserProfile(userSlug: string) {
  router.push(`/u/${userSlug}`);
}

function scrollToBottom() {
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight;
  }
}

// Lifecycle hooks
onMounted(async () => {
  try {
    authStore.initialize();
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('click', closeRoomActionsMenu);
    
    nextTick(() => {
      scrollToBottom();
    });
  } catch (error) {
    console.error('Error initializing room:', error);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('click', closeRoomActionsMenu);
});

watch([() => room.value, () => authStore.isAuthenticated, () => isParticipant.value], 
  ([newRoom, isAuthenticated, isParticipant]) => {
    if (newRoom && isAuthenticated && isParticipant) {
      initializeWebSocket();
    } else {
      closeWebSocket();
    }
  }, 
  { immediate: true }
);

watch(() => messages.value.length, (newLength, oldLength) => {
  if (newLength > oldLength) {
    const lastMessage = messages.value[messages.value.length - 1];
    if (lastMessage?.user?.id === authStore.user?.id) {
      nextTick(() => {
        scrollToBottom();
      });
    }
  }
});
</script>

<style scoped>
.room-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  background-color: var(--bg-color);
}

.edit-modal-overlay {
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

.edit-modal-content {
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideIn 0.2s ease-out;
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

.room-loading, .room-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.room-error {
  color: #f44336;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: var(--primary-color);
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
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  z-index: 10;
}

.room-header-left {
  display: flex;
  align-items: center;
}

.back-button {
  margin-right: 1rem;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.back-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.room-header-right {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

/* Room Actions Menu Styles */
.room-actions-menu {
  position: relative;
}

.room-actions-button {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.room-actions-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.room-actions-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  z-index: 1000;
  min-width: 150px;
  margin-top: 0.25rem;
  animation: fadeIn 0.15s ease-out;
}

.room-action-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  font-size: 0.9rem;
  text-align: left;
  transition: var(--transition);
}

.room-action-item:hover {
  background-color: var(--bg-color);
}

.room-action-item:first-child {
  border-radius: var(--radius) var(--radius) 0 0;
}

.room-action-item:last-child {
  border-radius: 0 0 var(--radius) var(--radius);
}

.room-action-item.delete-action {
  color: var(--error-color);
}

.room-action-item.delete-action:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

/* Error states */
.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #f44336;
  padding: 0.75rem;
  margin: 0.5rem 1rem;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}

.room-error-banner {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
}

.websocket-error-banner {
  background-color: #fffbeb;
  border-color: #fed7aa;
  color: #ea580c;
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
}

.error-message svg {
  flex-shrink: 0;
}

.error-list {
  flex: 1;
}

.error-list p {
  margin: 0;
  font-size: 0.875rem;
}

.btn-retry {
  padding: 0.4rem 0.75rem;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.8rem;
  white-space: nowrap;
}

.btn-retry:hover {
  background-color: #b91c1c;
}

.websocket-error-banner .btn-retry {
  background-color: #ea580c;
}

.websocket-error-banner .btn-retry:hover {
  background-color: #c2410c;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #f44336;
  gap: 1rem;
}

.error-state svg {
  margin-bottom: 0.5rem;
  opacity: 0.7;
}

.error-state p {
  margin: 0;
  font-weight: 500;
}

.message-error {
  margin: 0 0 0.75rem 0;
  padding: 0.5rem 0.75rem;
}

.btn-home {
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  display: inline-block;
}

.btn-home:hover {
  background-color: var(--primary-hover);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.close-sidebar-button {
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

.close-sidebar-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.mobile-sidebar {
  position: absolute;
  left: -280px;
  top: 0;
  bottom: 0;
  z-index: 20;
  box-shadow: var(--shadow);
}

.mobile-sidebar.sidebar-visible {
  left: 0;
}

/* Update media query */
@media (max-width: 768px) {
  .room-sidebar {
    position: absolute;
    left: -280px;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: var(--shadow);
  }
  
  .sidebar-visible {
    left: 0;
  }
}

.sidebar-toggle {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.sidebar-toggle:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.room-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-left: 1rem;
}

.room-topic {
  background-color: var(--bg-color);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  color: var(--primary-color);
  font-weight: 500;
}

.participants-count {
  margin-left: 1rem;
  background-color: var(--bg-color);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.join-button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  transition: var(--transition);
}

.join-button:hover {
  background-color: var(--primary-hover);
}

.room-main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.room-sidebar {
  width: 280px;
  background-color: var(--white);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: var(--transition);
}

@media (max-width: 768px) {
  .room-sidebar {
    position: absolute;
    left: -280px;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: var(--shadow);
  }
  
  .sidebar-visible {
    left: 0;
  }
}

.sidebar-title {
  padding: 1rem;
  margin: 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.1rem;
  font-weight: 600;
}

.participants-list {
  padding: 0.5rem;
}

.participant-item {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
  margin: 0.5rem 0;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
}

.participant-item:hover {
  background-color: var(--bg-color);
}

.participant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 0.75rem;
}

.participant-info {
  display: flex;
  flex-direction: column;
}

.participant-name {
  font-weight: 500;
}

.host-badge {
  font-size: 0.7rem;
  color: var(--primary-color);
  margin-top: 0.1rem;
  font-weight: 500;
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
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message-input-container {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--white);
}

.message-input-container form {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.message-input-container input {
  width: 100%;
  padding: 0.75rem 1rem;
  padding-right: 4rem; /* Make room for character counter */
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-family: inherit;
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--bg-color);
  transition: var(--transition);
  box-sizing: border-box;
}

.message-input-container input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.char-count {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  color: var(--text-light);
  background-color: var(--bg-color);
  padding: 0.125rem 0.25rem;
  border-radius: var(--radius-sm);
  pointer-events: none;
  user-select: none;
}

.char-limit-warning {
  color: var(--error-color);
  font-weight: 500;
}

.message-input-container button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  cursor: pointer;
  flex-shrink: 0;
}

.message-input-container button:hover {
  background-color: var(--primary-hover);
}

.message-input-container button:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
}

.auth-prompt, .join-prompt {
  padding: 1rem;
  text-align: center;
  border-top: 1px solid var(--border-color);
  background-color: var(--white);
}

.auth-prompt a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-prompt a:hover {
  text-decoration: underline;
}

.connection-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 0.75rem;
  transition: all 0.3s ease;
}

.connection-dot.connected {
  background-color: #10b981; /* green */
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.connection-dot.connecting {
  background-color: #f59e0b; /* amber */
  animation: pulse 1.5s infinite;
}

.connection-dot.error, .connection-dot.disconnected {
  background-color: #ef4444; /* red */
  cursor: pointer;
}

.connection-dot.error:hover, .connection-dot.disconnected:hover {
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.3);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>