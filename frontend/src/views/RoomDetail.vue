<script setup>
import { ref, inject, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from '@/api/room.api';
import { useWebSocket } from '@/api/websocket';
import { useNotifications } from '@/composables/useNotifications';

import Message from '@/components/Message.vue';
import EditRoomForm from '@/components/EditRoomForm.vue';

const Swal = inject('$swal');
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const notifications = useNotifications();
const { deleteRoom, joinRoom, fetchRoom } = useRoomApi();

const room = ref(null);
const loading = ref(false);
const messageInput = ref('');
const messagesContainerRef = ref(null);
const showSidebar = ref(window.innerWidth > 768);
const isMobileView = ref(window.innerWidth <= 768);
const showEditForm = ref(false);

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
  return authStore.isAuthenticated && isParticipant.value;
});

const participants = computed(() => {
  if (!room.value) return [];
  
  const allParticipants = [...room.value.participants];

  // Mark the host in the existing participants list
  const hostIndex = allParticipants.findIndex(p => p.id === room.value.host.id);
  if (hostIndex !== -1) {
    allParticipants[hostIndex] = {
      ...allParticipants[hostIndex],
      isHost: true
    };
  }
  
  return allParticipants;
});

async function handleMessageDelete(messageId) {
  try {
    const success = deleteWebSocketMessage(messageId);
    
    if (!success) {
      notifications.warning('Failed to delete message. WebSocket connection may be lost.');
    }
  } catch (error) {
    notifications.error('Error deleting message: ' + error.message);
  }
}

async function handleMessageUpdate(messageId, newBody) {
  try {
    const success = updateWebSocketMessage(messageId, newBody);
    
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
    await deleteRoom(room.value.host.username, room.value.slug);
    router.push('/');
  }
}

function handleEditRoom() {
  showEditForm.value = true;
}

function handleEditCancel() {
  showEditForm.value = false;
}

async function handleEditComplete(updatedRoom) {
  showEditForm.value = false;
  room.value = updatedRoom;
  notifications.success('Room updated successfully!');
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
  await joinRoom(room.value.host.username, room.value.slug);
  loading.value = true;
  room.value = await fetchRoom(room.value.host.username, room.value.slug);
  loading.value = false;
  
  if (authStore.isAuthenticated && isParticipant.value) {
    await initializeWebSocket();
  }
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

function navigateToUserProfile(userSlug) {
  router.push(`/user/${userSlug}`);
}

// Lifecycle hooks
onMounted(async () => {
  try {
    await authStore.initialize();
    loading.value = true;
    room.value = await fetchRoom(route.params.hostSlug, route.params.roomSlug);
    loading.value = false;
    
    if (authStore.isAuthenticated && isParticipant.value) {
      await initializeWebSocket();
    }
    
    window.addEventListener('resize', handleResize);
  } catch (error) {
    notifications.error(error);
  }
});

onBeforeUnmount(() => {
  closeWebSocket();
  window.removeEventListener('resize', handleResize);
});

watch(() => authStore.isAuthenticated, async (newValue) => {
  if (newValue && isParticipant.value && room.value) {
    await initializeWebSocket();
  } else if (!newValue) {
    closeWebSocket();
  }
});

watch(() => route.params.room, async () => {
  closeWebSocket();
  if (authStore.isAuthenticated && isParticipant.value) {
    await initializeWebSocket();
  }
});
</script>

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
          <button @click="$router.back()" class="back-button">
            <font-awesome-icon icon="arrow-left" />
          </button>
          <h2>{{ room.name }}</h2>
          <span class="room-topic" v-if="room.topic">{{ room.topic.name }}</span>
          <span class="participants-count">
            <font-awesome-icon icon="users" /> {{ participants.length }}
          </span>
        </div>
        
        <div class="room-header-right">
          <button v-if="isMobileView" @click="toggleSidebar" class="sidebar-toggle">
            <font-awesome-icon :icon="showSidebar ? 'times' : 'users'" />
          </button>
          <button v-if="isHost" @click="handleEditRoom" class="edit-button" title="Edit Room">
            <font-awesome-icon icon="edit" />
          </button>
          <button v-if="isHost" @click="handleRoomDelete" class="delete-button" title="Delete Room">
            <font-awesome-icon icon="trash" />
          </button>
          <button v-if="!isParticipant && authStore.isAuthenticated" @click="handleJoin" class="join-button">
            Join Room
          </button>
        </div>
      </div>
      
      <!-- Main content area with sidebar and conversation -->
      <div class="room-main-content">
        <!-- Sidebar with participants -->
        <div class="room-sidebar" :class="{ 'sidebar-visible': showSidebar, 'mobile-sidebar': isMobileView }">
          <div class="sidebar-header">
            <h3 class="sidebar-title">Participants</h3>
            <button v-if="isMobileView" @click="toggleSidebar" class="close-sidebar-button">
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
                :alt="`${participant.username}'s avatar`" 
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
                <font-awesome-icon icon="paper-plane" />
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
    </div>
    
    <!-- Error state -->
    <div v-else class="room-error">
      <p>Room not found or you don't have access.</p>
      <router-link to="/">Go back to home</router-link>
    </div>
  </div>
</template>

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
  border-radius: var(--radius);
  box-shadow: var(--shadow);
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
    transform: translateY(-20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
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

.room-topic {
  margin-left: 1rem;
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

.edit-button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
  cursor: pointer;
}

.edit-button:hover {
  background-color: var(--primary-hover);
}

.delete-button {
  background-color: var(--error-color);
  color: var(--white);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.delete-button:hover {
  opacity: 0.9;
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
  padding: 0, 0.5rem;
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
}

.message-input-container {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--white);
}

.message-input-container form {
  display: flex;
  gap: 0.5rem;
}

.message-input-container input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-family: inherit;
  font-size: 1rem;
  transition: var(--transition);
}

.message-input-container input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
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