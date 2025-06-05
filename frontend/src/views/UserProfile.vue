<template>
  <div class="profile-container">
    <!-- Header with back button -->
    <div class="profile-header">
      <button class="back-button" @click="$router.back()">
        <font-awesome-icon icon="arrow-left" />
      </button>
      <h1>Profile</h1>
      
      <!-- Edit button for own profile -->
      <div v-if="isOwnProfile && !isEditing" class="header-actions">
        <button class="edit-button" @click="startEditing">
          <font-awesome-icon icon="edit" />
          Edit
        </button>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="profile-loading">
      <div class="spinner"></div>
      <p>Loading profile...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="profile-error">
      <p>Sorry, we couldn't load this profile.</p>
      <button class="retry-button" @click="fetchUser">
        <font-awesome-icon icon="sync" />
        Retry
      </button>
    </div>
    
    <!-- User profile content -->
    <div v-else-if="user" class="profile-content">
      <div class="profile-overview" :class="{ 'edit-mode': isEditing }">
        <!-- Editing mode -->
        <div v-if="isEditing" class="edit-profile">
          <div class="edit-header">
            <h3>Edit Profile</h3>
          </div>
          
          <form class="edit-form" @submit.prevent="saveProfile">
            <div class="form-content">
              <!-- Avatar upload -->
              <div class="form-group">
                <label class="form-label">Profile Picture</label>
                <div class="avatar-upload">
                  <div class="current-avatar">
                    <UserAvatar 
                      v-if="!avatarPreview" 
                      :user="user" 
                      size="large" 
                    />
                    <img 
                      v-else 
                      :src="avatarPreview" 
                      alt="Avatar preview" 
                      class="avatar-preview"
                    />
                  </div>
                  <input
                    id="avatar-input"
                    type="file"
                    accept=".svg, .png, .jpg, .jpeg"
                    class="avatar-input"
                    @change="handleAvatarChange"
                  />
                  <label for="avatar-input" class="avatar-upload-button">
                    <font-awesome-icon icon="camera" />
                    Change Picture
                  </label>
                </div>
              </div>
              
              <!-- Name input -->
              <div class="form-group">
                <label for="name-input" class="form-label">Display Name</label>
                <input
                  id="name-input"
                  v-model="editForm.name"
                  type="text"
                  class="form-input"
                  placeholder="Enter your display name"
                  maxlength="150"
                />
              </div>
              
              <!-- Bio input -->
              <div class="form-group bio-group">
                <label for="bio-input" class="form-label">Bio</label>
                <textarea
                  id="bio-input"
                  v-model="editForm.bio"
                  class="form-textarea"
                  placeholder="Tell us about yourself..."
                  maxlength="500"
                ></textarea>
                <div class="char-count">
                  {{ editForm.bio.length }}/500
                </div>
              </div>
            </div>
            
            <!-- Action buttons -->
            <div class="form-actions">
              <button 
                type="button" 
                class="cancel-button" 
                :disabled="editLoading"
                @click="cancelEditing"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                class="save-button"
                :disabled="editLoading"
              >
                <font-awesome-icon v-if="editLoading" icon="spinner" spin />
                <font-awesome-icon v-else icon="check" />
                {{ editLoading ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
        
        <!-- View mode -->
        <div v-else class="profile-main">
          <UserAvatar :user="user" size="large" />
          
          <div class="profile-names">
            <h2 class="profile-name">{{ user.name || user.username }}</h2>
            <p class="profile-username">@{{ user.username }}</p>
          </div>
        </div>
        
        <!-- Bio section (only in view mode) -->
        <div v-if="!isEditing">
          <div v-if="user.bio" class="profile-bio">
            {{ user.bio }}
          </div>
          <div v-else class="profile-bio no-bio">
            {{ isOwnProfile ? "You haven't added a bio yet." : "This user hasn't added a bio yet." }}
          </div>
        </div>
      </div>
      
      <!-- Profile tabs (hidden during editing) -->
      <div v-if="!isEditing" class="profile-tabs">
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
      
      <!-- Tab content (hidden during editing) -->
      <div v-if="!isEditing" class="tab-content">
        <!-- Messages Tab -->
        <div v-if="activeTab === 'messages'" class="messages-tab">
          <div v-if="tabsData.messages.loading" class="tab-loading">
            <div class="spinner"></div>
            <p>Loading messages...</p>
          </div>
          
          <div v-else-if="tabsData.messages.error" class="tab-error">
            <p>Failed to load messages</p>
            <button class="retry-button-small" @click="loadTabData('messages')">
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
                <button class="view-room-button" @click="navigateToRoom(message.room)">
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
            <button class="retry-button-small" @click="loadTabData('hostedRooms')">
              <font-awesome-icon icon="sync" /> Retry
            </button>
          </div>
          
          <div v-else-if="tabsData.hostedRooms.data.length === 0" class="empty-tab">
            <font-awesome-icon icon="door-closed" size="2x" />
            <p>No rooms hosted yet</p>
          </div>
          
          <div v-else class="rooms-list">
            <div v-for="room in tabsData.hostedRooms.data" :key="room.id" class="room-card" @click="navigateToRoom(room)">
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
            <button class="retry-button-small" @click="loadTabData('joinedRooms')">
              <font-awesome-icon icon="sync" /> Retry
            </button>
          </div>
          
          <div v-else-if="tabsData.joinedRooms.data.length === 0" class="empty-tab">
            <font-awesome-icon icon="door-open" size="2x" />
            <p>Not participating in any rooms yet</p>
          </div>
          
          <div v-else class="rooms-list">
            <div v-for="room in tabsData.joinedRooms.data" :key="room.id" class="room-card" @click="navigateToRoom(room)">
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
      <button class="back-link" @click="$router.back()">
        Go back
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apolloClient } from '@/api/apollo.client';
import { useNotifications } from '@/composables/useNotifications';
import { useAuthStore } from '@/stores/auth.store';
import { useAuthApi } from '@/api/auth.api';

import UserAvatar from '@/components/common/UserAvatar.vue';
import type { User, Room, Message } from '@/types';

import {
    USER_QUERY,
    MESSAGES_BY_USER_QUERY,
    ROOMS_QUERY,
    ROOMS_PARTICIPATED_BY_USER_QUERY
} from '@/api/graphql';

const route = useRoute();
const router = useRouter();
const notifications = useNotifications();
const authStore = useAuthStore();
const authApi = useAuthApi();

const user = ref<User | null>(null);
const loading = ref<boolean>(true);
const error = ref<Error | null>(null);

// Edit mode state
type EditForm = { name: string; bio: string; avatar: File | null };
const isEditing = ref<boolean>(false);
const editLoading = ref<boolean>(false);
const editForm = ref<EditForm>({
  name: '',
  bio: '',
  avatar: null
});
const avatarPreview = ref<string | null>(null);

// Tab data
type TabKey = 'messages' | 'hostedRooms' | 'joinedRooms';
type TabData<T> = {
  loaded: boolean;
  loading: boolean;
  data: T[];
  error: Error | null;
};
interface TabTypes {
  messages: Message;
  hostedRooms: Room;
  joinedRooms: Room;
}

const activeTab = ref<TabKey>('messages');
const tabsData = ref<{ [K in TabKey]: TabData<TabTypes[K]> }>({
  messages: { loaded: false, loading: false, data: [], error: null },
  hostedRooms: { loaded: false, loading: false, data: [], error: null },
  joinedRooms: { loaded: false, loading: false, data: [], error: null }
});

// Check if current user is viewing their own profile
const isOwnProfile = computed(() => {
  return authStore.user && user.value && authStore.user.username === user.value.username;
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
    
    // Initialize edit form with current user data
    if (user.value) {
      editForm.value = {
        name: user.value.name || '',
        bio: user.value.bio || '',
        avatar: null
      };
    }
    
    loadTabData(activeTab.value);
  } catch (err) {
    error.value = err instanceof Error ? err : new Error(String(err));
    notifications.error('Error loading user profile');
  } finally {
    loading.value = false;
  }
}

async function loadTabData(tab: TabKey) {
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
    tabsData.value[tab].error = err instanceof Error ? err : new Error(String(err));
    notifications.error(`Error loading ${tab}`);
  } finally {
    tabsData.value[tab].loading = false;
  }
}

async function fetchUserMessages() {
  const { data } = await apolloClient.query({
    query: MESSAGES_BY_USER_QUERY,
    variables: { userSlug: user.value!.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.messages.data = data.messagesByUser || [];
}

async function fetchHostedRooms() {
  const { data } = await apolloClient.query({
    query: ROOMS_QUERY,
    variables: { hostSlug: user.value!.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.hostedRooms.data = data.rooms || [];
}

async function fetchJoinedRooms() {
  const { data } = await apolloClient.query({
    query: ROOMS_PARTICIPATED_BY_USER_QUERY,
    variables: { userSlug: user.value!.username },
    fetchPolicy: 'network-only'
  });
  
  tabsData.value.joinedRooms.data = data.roomsParticipatedByUser || [];
}

function setActiveTab(tab: TabKey) {
  activeTab.value = tab;
  loadTabData(tab);
}

// Navigation to room
function navigateToRoom(room: Room) {
  router.push(`/u/${room.host.username}/${room.slug}`);
}

// Format date for display
function formatDate(dateString: string) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Edit profile functions
function startEditing() {
  isEditing.value = true;
  editForm.value = {
    name: user.value!.name || '',
    bio: user.value!.bio || '',
    avatar: null
  };
  avatarPreview.value = null;
}

function cancelEditing() {
  isEditing.value = false;
  editForm.value = {
    name: user.value!.name || '',
    bio: user.value!.bio || '',
    avatar: null
  };
  avatarPreview.value = null;
}

function handleAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files && target.files[0];
  if (file) {
    editForm.value.avatar = file;
    
    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = (e.target as FileReader).result as string;
    };
    reader.readAsDataURL(file);
  }
}

function mergeUserData(
  original: User,
  incoming: Partial<User>
): User {
  return {
    id: incoming.id ?? original.id,
    username: incoming.username ?? original.username,
    name: incoming.name ?? original.name,
    bio: incoming.bio ?? original.bio,
    avatar: incoming.avatar ?? original.avatar
  };
}


async function saveProfile() {
  editLoading.value = true;
  
  try {
    const updateData: { name?: string; bio?: string; avatar?: File | null } = {};
    if (editForm.value.name.trim()) {
      updateData.name = editForm.value.name.trim();
    }

    updateData.bio = editForm.value.bio.trim();

    // Add avatar if selected
    if (editForm.value.avatar) {
      updateData.avatar = editForm.value.avatar;
    }
    
    const result = await authApi.updateUser(updateData);
    
    if (result.success) {
      // Update local user data
      // TODO: refactor this to use a store or state management
      user.value = mergeUserData(user.value!, result.user!);
      
      // Check if username changed, if so redirect
      if (result.user!.username !== route.params.userSlug) {
        router.replace(`/u/${result.user!.username}`);
      }
      
      isEditing.value = false;
      avatarPreview.value = null;
    } else {
      notifications.error('Failed to update profile');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    notifications.error('An error occurred while updating your profile');
  } finally {
    editLoading.value = false;
  }
}

onMounted(() => {
  fetchUser();
});

// Watch for route changes to reload when username changes
watch(() => route.params.userSlug, (newUsername) => {
  if (newUsername) {
    // Reset all tabs data when user changes
    (Object.keys(tabsData.value) as TabKey[]).forEach(tab => {
      tabsData.value[tab].loaded = false;
      tabsData.value[tab].data = [];
    });
    
    // Cancel editing if switching users
    isEditing.value = false;
    
    fetchUser();
  }
});
</script>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  height: 100vh;
  background-color: var(--bg-color);
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  flex-shrink: 0;
  z-index: 10;
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
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.9rem;
}

.edit-button:hover {
  background-color: var(--primary-hover);
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
  overflow: hidden;
}

.profile-overview {
  padding: 2rem 1rem;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.profile-overview.edit-mode {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
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

/* Edit profile styles */
.edit-profile {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.edit-header {
  padding: 2rem 2rem 1rem 2rem;
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-color);
}

.edit-profile h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.edit-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.form-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.bio-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.form-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
  flex-shrink: 0;
}

.form-input, .form-textarea {
  box-sizing: border-box;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 1rem;
  transition: var(--transition);
  color: var(--text-color);
  background-color: var(--white);
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(65, 105, 225, 0.1);
}

.form-textarea {
  resize: none;
  flex: 1;
  min-height: 200px;
  font-family: inherit;
}

.char-count {
  align-self: flex-end;
  font-size: 0.8rem;
  color: var(--text-light);
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-avatar {
  flex-shrink: 0;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--white);
  box-shadow: var(--shadow);
}

.avatar-input {
  display: none;
}

.avatar-upload-button {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
  font-size: 0.9rem;
}

.avatar-upload-button:hover {
  background-color: var(--primary-color);
  color: var(--white);
  border-color: var(--primary-color);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--white);
  flex-shrink: 0;
}

.cancel-button, .save-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.cancel-button {
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.cancel-button:hover:not(:disabled) {
  background-color: var(--border-color);
}

.save-button {
  background-color: var(--primary-color);
  color: var(--white);
}

.save-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.cancel-button:disabled, .save-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--white);
  flex-shrink: 0;
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
  overflow-y: auto;
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
  
  .form-content {
    padding: 1rem;
  }
  
  .form-actions {
    padding: 1rem;
  }
  
  .edit-header {
    padding: 1rem;
  }
}
</style>
