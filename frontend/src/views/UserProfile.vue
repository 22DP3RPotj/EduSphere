<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apolloClient } from '@/api/apollo.client';
import { useNotifications } from '@/composables/useNotifications';

import {
    USER_QUERY,
    MESSAGES_BY_USER_QUERY,
    ROOMS_QUERY,
    ROOM_PARTICIPATED_BY_USER_QUERY
} from '@/api/graphql/room.queries';

import UserAvatar from '@/components/UserAvatar.vue';

const route = useRoute();
const router = useRouter();
const notifications = useNotifications();

const user = ref(null);
const loading = ref(true);
const error = ref(null);

// Tab data
const activeTab = ref('messages');
const tabsData = ref({
  messages: {
    loaded: false,
    loading: false,
    data: [],
    error: null
  },
  hostedRooms: {
    loaded: false,
    loading: false,
    data: [],
    error: null
  },
  joinedRooms: {
    loaded: false,
    loading: false,
    data: [],
    error: null
  }
});

async function fetchUser() {
  loading.value = true;
  error.value = null;
  
  try {
    const { data } = await apolloClient.query({
      query: USER_QUERY,
      variables: { username: route.params.userSlug },
      fetchPolicy: 'network-only'
    });
    
    user.value = data.user;
    
    loadTabData(activeTab.value);
  } catch (err) {
    error.value = err;
    notifications.error('Error loading user profile');
  } finally {
    loading.value = false;
  }
}

async function loadTabData(tab) {
  if (tabsData.value[tab].loaded || tabsData.value[tab].loading) {
    return;
  }
  
  tabsData.value[tab].loading = true;
  tabsData.value[tab].error = null;
  
  try {
    switch (tab) {
      case 'messages':
        await fetchUserMessages();
        break;
      case 'hostedRooms':
        await fetchHostedRooms();
        break;
      case 'joinedRooms':
        await fetchJoinedRooms();
        break;
    }
    
    tabsData.value[tab].loaded = true;
  } catch (err) {
    tabsData.value[tab].error = err;
    notifications.error(`Error loading ${tab}`);
  } finally {
    tabsData.value[tab].loading = false;
  }
}

async function fetchUserMessages() {
  const { data } = await apolloClient.query({
    query: MESSAGES_BY_USER_QUERY,
    variables: { userSlug: user.value.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.messages.data = data.messagesByUser || [];
}

async function fetchHostedRooms() {
  const { data } = await apolloClient.query({
    query: ROOMS_QUERY,
    variables: { hostSlug: user.value.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.hostedRooms.data = data.rooms || [];
}

async function fetchJoinedRooms() {
  const { data } = await apolloClient.query({
    query: ROOM_PARTICIPATED_BY_USER_QUERY,
    variables: { userSlug: user.value.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.joinedRooms.data = data.roomsParticipatedByUser || [];
}

function setActiveTab(tab) {
  activeTab.value = tab;
  loadTabData(tab);
}

// Navigation to room
function navigateToRoom(room) {
  router.push(`/user/${room.host?.username || user.value.username}/${room.slug}`);
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

onMounted(() => {
  fetchUser();
});

// Watch for route changes to reload when username changes
watch(() => route.params.userSlug, (newUsername) => {
  if (newUsername) {
    // Reset all tabs data when user changes
    Object.keys(tabsData.value).forEach(tab => {
      tabsData.value[tab].loaded = false;
      tabsData.value[tab].data = [];
    });
    fetchUser();
  }
});
</script>

<template>
  <div class="profile-container">
    <!-- Header with back button -->
    <div class="profile-header">
      <button @click="$router.back()" class="back-button">
        <font-awesome-icon icon="arrow-left" />
      </button>
      <h1>Profile</h1>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="profile-loading">
      <div class="spinner"></div>
      <p>Loading profile...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="profile-error">
      <p>Sorry, we couldn't load this profile.</p>
      <button @click="fetchUser" class="retry-button">
        <font-awesome-icon icon="sync" />
        Retry
      </button>
    </div>
    
    <!-- User profile content -->
    <div v-else-if="user" class="profile-content">
      <div class="profile-overview">
        <div class="profile-main">
          <UserAvatar :user="user" size="large" />
          
          <div class="profile-names">
            <h2 class="profile-name">{{ user.name || user.username }}</h2>
            <p class="profile-username">@{{ user.username }}</p>
          </div>
        </div>
        
        <!-- Bio section -->
        <div v-if="user.bio" class="profile-bio">
          {{ user.bio }}
        </div>
        <div v-else class="profile-bio no-bio">
          This user hasn't added a bio yet.
        </div>
      </div>
      
      <!-- Profile tabs -->
      <div class="profile-tabs">
        <div 
          class="tab" 
          :class="{ active: activeTab === 'messages' }"
          @click="setActiveTab('messages')"
        >
          Messages
        </div>
        <div 
          class="tab" 
          :class="{ active: activeTab === 'hostedRooms' }"
          @click="setActiveTab('hostedRooms')"
        >
          Hosted Rooms
        </div>
        <div 
          class="tab" 
          :class="{ active: activeTab === 'joinedRooms' }"
          @click="setActiveTab('joinedRooms')"
        >
          Joined Rooms
        </div>
      </div>
      
      <!-- Tab content -->
      <div class="tab-content">
        <!-- Messages Tab -->
        <div v-if="activeTab === 'messages'" class="messages-tab">
          <div v-if="tabsData.messages.loading" class="tab-loading">
            <div class="spinner"></div>
            <p>Loading messages...</p>
          </div>
          
          <div v-else-if="tabsData.messages.error" class="tab-error">
            <p>Failed to load messages</p>
            <button @click="loadTabData('messages')" class="retry-button-small">
              <font-awesome-icon icon="sync" /> Retry
            </button>
          </div>
          
          <div v-else-if="tabsData.messages.data.length === 0" class="empty-tab">
            <font-awesome-icon icon="comment-alt" size="2x" />
            <p>No messages yet</p>
          </div>
          
          <div v-else class="messages-list">
            <div v-for="message in tabsData.messages.data" :key="message.id" class="message-item-preview">
              <div class="message-room">
                <font-awesome-icon icon="comments" class="room-icon" />
                <span>{{ message.room.name }}</span>
                <span class="message-date">{{ formatDate(message.created) }}</span>
              </div>
              <div class="message-content-preview">
                {{ message.body }}
              </div>
              <div class="message-actions">
                <button @click="navigateToRoom(message.room)" class="view-room-button">
                  <font-awesome-icon icon="eye" /> View Room
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Hosted Rooms Tab -->
        <div v-if="activeTab === 'hostedRooms'" class="rooms-tab">
          <div v-if="tabsData.hostedRooms.loading" class="tab-loading">
            <div class="spinner"></div>
            <p>Loading rooms...</p>
          </div>
          
          <div v-else-if="tabsData.hostedRooms.error" class="tab-error">
            <p>Failed to load hosted rooms</p>
            <button @click="loadTabData('hostedRooms')" class="retry-button-small">
              <font-awesome-icon icon="sync" /> Retry
            </button>
          </div>
          
          <div v-else-if="tabsData.hostedRooms.data.length === 0" class="empty-tab">
            <font-awesome-icon icon="door-closed" size="2x" />
            <p>No rooms hosted yet</p>
          </div>
          
          <div v-else class="rooms-list">
            <div v-for="room in tabsData.hostedRooms.data" :key="room.slug" class="room-card" @click="navigateToRoom(room)">
              <div class="room-card-header">
                <h3 class="room-name">{{ room.name }}</h3>
                <span v-if="room.topic" class="room-topic">{{ room.topic.name }}</span>
              </div>
              <div class="room-description">{{ room.description }}</div>
              <div class="room-footer">
                <span class="room-date">Created {{ formatDate(room.created) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Joined Rooms Tab -->
        <div v-if="activeTab === 'joinedRooms'" class="rooms-tab">
          <div v-if="tabsData.joinedRooms.loading" class="tab-loading">
            <div class="spinner"></div>
            <p>Loading joined rooms...</p>
          </div>
          
          <div v-else-if="tabsData.joinedRooms.error" class="tab-error">
            <p>Failed to load joined rooms</p>
            <button @click="loadTabData('joinedRooms')" class="retry-button-small">
              <font-awesome-icon icon="sync" /> Retry
            </button>
          </div>
          
          <div v-else-if="tabsData.joinedRooms.data.length === 0" class="empty-tab">
            <font-awesome-icon icon="door-open" size="2x" />
            <p>Not participating in any rooms yet</p>
          </div>
          
          <div v-else class="rooms-list">
            <div v-for="room in tabsData.joinedRooms.data" :key="room.slug" class="room-card" @click="navigateToRoom(room)">
              <div class="room-card-header">
                <h3 class="room-name">{{ room.name }}</h3>
                <span v-if="room.topic" class="room-topic">{{ room.topic.name }}</span>
              </div>
              <div class="room-description">{{ room.description }}</div>
              <div class="room-footer">
                <span class="room-date">Created {{ formatDate(room.created) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User not found -->
    <div v-else class="profile-not-found">
      <font-awesome-icon icon="user-slash" size="3x" />
      <h2>User not found</h2>
      <p>The user you're looking for doesn't exist or is unavailable.</p>
      <button @click="$router.back()" class="back-link">
        Go back
      </button>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
  background-color: var(--bg-color);
}

.profile-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: var(--shadow);
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

.profile-header h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.profile-loading, .profile-error, .profile-not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  flex: 1;
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

.retry-button, .retry-button-small {
  margin-top: 1rem;
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: var(--transition);
}

.retry-button {
  padding: 0.5rem 1rem;
}

.retry-button-small {
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
}

.retry-button:hover, .retry-button-small:hover {
  background-color: var(--primary-hover);
}

.profile-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.profile-overview {
  padding: 2rem 1rem;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
}

.profile-main {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.profile-names {
  margin-left: 1rem;
}

.profile-name {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.profile-username {
  margin: 0.25rem 0 0;
  color: var(--text-light);
  font-size: 0.9rem;
}

.profile-bio {
  line-height: 1.6;
  max-width: 600px;
}

.no-bio {
  color: var(--text-light);
  font-style: italic;
}

.profile-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--white);
}

.tab {
  padding: 1rem;
  font-weight: 500;
  color: var(--text-light);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  text-align: center;
  flex: 1;
}

.tab:hover {
  color: var(--text-color);
}

.tab.active {
  color: var(--primary-color);
  font-weight: 600;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.tab-content {
  flex: 1;
  padding: 1rem;
  background-color: var(--white);
}

.tab-loading, .tab-error, .empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  text-align: center;
}

.tab-loading .spinner {
  width: 24px;
  height: 24px;
}

.empty-tab {
  color: var(--text-light);
}

.empty-tab svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Messages list styling */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item-preview {
  background-color: var(--bg-color);
  border-radius: var(--radius);
  padding: 1rem;
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.message-room {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
}

.room-icon {
  margin-right: 0.5rem;
  font-size: 0.8rem;
}

.message-date {
  margin-left: auto;
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: normal;
}

.message-content-preview {
  margin-bottom: 0.75rem;
  color: var(--text-color);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-actions {
  display: flex;
  justify-content: flex-end;
}

.view-room-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9rem;
}

.view-room-button:hover {
  background-color: var(--primary-hover);
}

/* Rooms list styling */
.rooms-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.room-card {
  background-color: var(--bg-color);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  padding: 1rem;
  transition: var(--transition);
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.room-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.room-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.room-name {
  margin: 0;
  color: var(--text-color);
  font-size: 1.1rem;
  font-weight: 600;
}

.room-topic {
  background-color: var(--bg-color);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  color: var(--primary-color);
  border: 1px solid var(--border-color);
}

.room-description {
  flex: 1;
  margin-bottom: 1rem;
  color: var(--text-color);
  line-height: 1.5;
  font-size: 0.95rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.room-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-light);
  font-size: 0.8rem;
}

.back-link {
  margin-top: 1.5rem;
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
}

.back-link:hover {
  background-color: var(--primary-hover);
}

@media (max-width: 768px) {
  .profile-main {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-names {
    margin-left: 0;
    margin-top: 1rem;
  }
  
  .profile-bio {
    text-align: center;
    margin: 0 auto;
  }
  
  .rooms-list {
    grid-template-columns: 1fr;
  }
  
  .tab {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
}
</style>