<template>
  <div class="home-container">
    <!-- Main content -->
    <main class="main-content">
      <div class="sidebar" :class="{ 'sidebar-visible': showSidebar, 'mobile-sidebar': isMobileView }">
        <div class="sidebar-header">
          <h3 class="sidebar-title">Filters</h3>
          <button v-if="isMobileView" class="close-sidebar-button" @click="toggleSidebar">
            <font-awesome-icon icon="times" />
          </button>
        </div>

        <div class="sidebar-section">
          <div class="filter-group">
            <label>Topics</label>
            <div class="topic-search">
              <input 
                v-model="topicSearchQuery" 
                type="text" 
                placeholder="Search topics..." 
                class="topic-search-input"
              />
            </div>
            <div class="topic-filters">
              <div 
                v-for="topic in filteredTopics" 
                :key="topic.name"
                :class="['topic-filter', { active: pendingTopics.includes(topic.name) }]"
                @click="toggleTopic(topic.name)"
              >
                {{ topic.name }}
              </div>
            </div>
          </div>
          
          <button class="btn-apply-filters" @click="applyFilters">
            <font-awesome-icon icon="filter" />
            Apply Filters
          </button>
          
          <button v-if="hasActiveFilters" class="btn-reset-filters" @click="resetFilters">
            <font-awesome-icon icon="times-circle" />
            Reset Filters
          </button>
        </div>
      </div>

      <div class="content-area">
        <!-- Search bar for homepage only -->
        <div class="home-search">
          <div class="search-input-container">
            <font-awesome-icon icon="search" class="search-icon" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search rooms..." 
              @keyup.enter="applyFilters"
            />
          </div>
          <button class="btn-search" @click="applyFilters">
            Search
          </button>
          <button v-if="isMobileView" class="filter-toggle-btn" @click="toggleSidebar">
            <font-awesome-icon icon="sliders-h" />
          </button>
        </div>

        <!-- Welcome section -->
        <section class="welcome-section">
          <div class="welcome-content">
            <h1>Welcome to Chat App</h1>
            <p class="welcome-subtitle">Join conversations on topics that matter to you</p>
            <div class="welcome-actions">
              <router-link v-if="isAuthenticated" to="/create-room" class="btn-create-room">
                <font-awesome-icon icon="plus-circle" />
                Create Room
              </router-link>
              <router-link v-if="!isAuthenticated" to="/login" class="btn-login">
                Login to join rooms
              </router-link>
            </div>
          </div>
        </section>

        <!-- Rooms section -->
        <section class="rooms-section">
          <div class="section-header">
            <h2>
              <font-awesome-icon :icon="['fas', 'comments']" />
              Active Rooms
            </h2>
            <div v-if="!isMobileView" class="section-controls">
              <button 
                class="view-toggle-btn"
                :title="isGridView ? 'Switch to list view' : 'Switch to grid view'"
                @click="toggleView"
              >
                <font-awesome-icon :icon="isGridView ? 'list' : 'th-large'" />
              </button>
            </div>
          </div>

          <!-- Loading state -->
          <div v-if="loadingRooms" class="rooms-loading">
            <div class="spinner"></div>
            <p>Loading rooms...</p>
          </div>

          <!-- No results state -->
          <div v-else-if="filteredRooms.length === 0" class="no-rooms">
            <font-awesome-icon icon="comment-slash" size="3x" />
            <p>No rooms found matching your criteria</p>
            <button class="btn-reset-filters" @click="resetFilters">Reset filters</button>
          </div>

          <!-- Rooms grid/list -->
          <div :class="['rooms-container', isGridView ? 'grid-view' : 'list-view']">
            <div 
              v-for="room in filteredRooms" 
              :key="room.id"
              class="room-card"
              @click="navigateToRoom(room)"
            >
              <div class="room-card-header">
                <h3 class="room-name">{{ room.name }}</h3>
                <span v-if="room.topic" class="room-topic">{{ room.topic.name }}</span>
              </div>
              <p class="room-description">{{ room.description }}</p>
              <div class="room-meta">
                <span class="room-date">
                  <font-awesome-icon icon="calendar-alt" />
                  {{ formatDate(room.created) }}
                </span>
                <span class="room-host">
                  <font-awesome-icon icon="user" />
                  {{ room.host.username }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Your Rooms Section (if authenticated) -->
        <section v-if="isAuthenticated" class="rooms-section joined-rooms-section">
          <div class="section-header">
            <h2>
              <font-awesome-icon :icon="['fas', 'user-circle']" />
              Joined Rooms
            </h2>
          </div>

          <!-- Loading state -->
          <div v-if="loadingUserRooms" class="rooms-loading">
            <div class="spinner"></div>
            <p>Loading your rooms...</p>
          </div>

          <!-- No rooms state -->
          <div v-else-if="userRooms.length === 0" class="no-rooms">
            <font-awesome-icon icon="door-closed" size="2x" />
            <p>You haven't joined any rooms yet</p>
            <router-link to="/create-room" class="btn-create-room-small">Create your first room</router-link>
          </div>

          <!-- User rooms grid -->
          <div class="rooms-container grid-view">
            <div 
              v-for="room in userRooms" 
              :key="room.slug"
              class="room-card"
              @click="navigateToRoom(room)"
            >
              <div class="room-card-header">
                <h3 class="room-name">{{ room.name }}</h3>
                <span v-if="room.topic" class="room-topic">{{ room.topic.name }}</span>
              </div>
              <p class="room-description">{{ room.description }}</p>
              <div class="room-meta">
                <span class="room-date">
                  <font-awesome-icon icon="calendar-alt" />
                  {{ formatDate(room.created) }}
                </span>
                <span class="room-host">
                  <font-awesome-icon icon="user" />
                  {{ room.host.username }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Recommendations Section -->
        <section v-if="isAuthenticated" class="rooms-section recommended-section">
          <div class="section-header">
            <h2>
              <font-awesome-icon :icon="['fas', 'star']" />
              Recommended For You
            </h2>
          </div>

          <!-- Loading state -->
          <div v-if="loadingRecommendations" class="rooms-loading">
            <div class="spinner"></div>
            <p>Finding recommendations...</p>
          </div>

          <!-- No recommendation state -->
          <div v-else-if="recommendedRooms.length === 0" class="no-rooms">
            <font-awesome-icon icon="compass" size="2x" />
            <p>No recommendations available right now</p>
          </div>

          <!-- Recommended rooms grid -->
          <div class="rooms-container grid-view">
            <div 
              v-for="room in recommendedRooms" 
              :key="room.slug"
              class="room-card"
              @click="navigateToRoom(room)"
            >
              <div class="room-card-header">
                <h3 class="room-name">{{ room.name }}</h3>
                <span v-if="room.topic" class="room-topic">{{ room.topic.name }}</span>
              </div>
              <p class="room-description">{{ room.description }}</p>
              <div class="room-meta">
                <span class="room-date">
                  <font-awesome-icon icon="calendar-alt" />
                  {{ formatDate(room.created) }}
                </span>
                <span class="room-host">
                  <font-awesome-icon icon="user" />
                  {{ room.host.username }}
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useNotifications } from '@/composables/useNotifications';
import { apolloClient } from '@/api/apollo.client';

import { 
  ROOMS_QUERY, 
  TOPIC_QUERY, 
  ROOMS_PARTICIPATED_BY_USER_QUERY,
  ROOMS_NOT_PARTICIPATED_BY_USER_QUERY,
  USER_QUERY
} from '@/api/graphql';

import type { User, Room, Topic } from '@/types';

const router = useRouter();
const authStore = useAuthStore();
const notifications = useNotifications();

// User state
const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = ref<User | null>(null);

// UI state
const isGridView = ref<boolean>(true);
const loadingRooms = ref<boolean>(true);
const loadingUserRooms = ref<boolean>(false);
const loadingRecommendations = ref<boolean>(false);
const showSidebar = ref<boolean>(window.innerWidth > 768);
const isMobileView = ref<boolean>(window.innerWidth <= 768);

// Room data
const allRooms = ref<Room[]>([]);
const filteredRoomsResult = ref<Room[]>([]);
const userRooms = ref<Room[]>([]);
const recommendedRooms = ref<Room[]>([]);
const topics = ref<Topic[]>([]);

// Filter state
const searchQuery = ref<string>('');
const topicSearchQuery = ref<string>('');
const selectedTopics = ref<string[]>([]);
const pendingTopics = ref<string[]>([]);
const pendingSearch = ref<string>('');

// Get filtered topics based on search query
const filteredTopics = computed(() => {
  if (!topicSearchQuery.value) {
    return topics.value;
  }
  
  const query = topicSearchQuery.value.toLowerCase();
  return topics.value.filter(topic => 
    topic.name.toLowerCase().includes(query)
  );
});

// Check if filters are active
const hasActiveFilters = computed(() => {
  return selectedTopics.value.length > 0 || searchQuery.value !== '';
});

// Get filtered rooms based on applied filters
const filteredRooms = computed(() => {
  return filteredRoomsResult.value;
});

// Helper function to format dates
function formatDate(dateString: string) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// Handle window resize
function handleResize() {
  isMobileView.value = window.innerWidth <= 768;
  
  if (!isMobileView.value) {
    showSidebar.value = true;
  } else {
    showSidebar.value = false;
  }
}

// Toggle sidebar visibility (mobile)
function toggleSidebar() {
  showSidebar.value = !showSidebar.value;
}

// Functions for search and filters
// function clearSearch() {
//   searchQuery.value = '';
//   pendingSearch.value = '';
//   applyFilters();
// }

function toggleTopic(topicName: string) {
  if (pendingTopics.value.includes(topicName)) {
    pendingTopics.value = pendingTopics.value.filter(t => t !== topicName);
  } else {
    pendingTopics.value.push(topicName);
  }
}

function applyFilters() {
  selectedTopics.value = [...pendingTopics.value];
  pendingSearch.value = searchQuery.value;
  fetchRooms();
}

function resetFilters() {
  searchQuery.value = '';
  pendingSearch.value = '';
  selectedTopics.value = [];
  pendingTopics.value = [];
  topicSearchQuery.value = '';
  fetchRooms();
}

function toggleView() {
  isGridView.value = !isGridView.value;
}

// Navigation functions
function navigateToRoom(room: Room) {
  router.push(`/u/${room.host?.username}/${room.slug}`);
}

// Data fetching functions
async function fetchCurrentUser() {
  if (!authStore.user?.username) return;
  
  try {
    const { data } = await apolloClient.query({
      query: USER_QUERY,
      variables: { username: authStore.user.username },
      fetchPolicy: 'network-only'
    });
    
    currentUser.value = data.user;
  } catch (error) {
    console.error('Error fetching current user:', error);
  }
}

async function fetchRooms() {
  try {
    loadingRooms.value = true;
    
    const variables = {
      search: pendingSearch.value || null,
      topic: selectedTopics.value.length > 0 ? selectedTopics.value : null
    };
    
    const { data } = await apolloClient.query({
      query: ROOMS_QUERY,
      variables,
      fetchPolicy: 'network-only'
    });
    
    allRooms.value = data.rooms || [];
    filteredRoomsResult.value = allRooms.value;
  } catch (error) {
    notifications.error('Error loading rooms');
    console.error(error);
  } finally {
    loadingRooms.value = false;
  }
}

async function fetchTopics() {
  try {
    const { data } = await apolloClient.query({
      query: TOPIC_QUERY,
      fetchPolicy: 'network-only'
    });
    
    topics.value = data.topics || [];
  } catch (error) {
    console.error('Error loading topics:', error);
  }
}

async function fetchUserRooms() {
  if (!authStore.isAuthenticated || !currentUser.value) return;
  
  try {
    loadingUserRooms.value = true;
    
    const { data } = await apolloClient.query({
      query: ROOMS_PARTICIPATED_BY_USER_QUERY,
      variables: { userSlug: currentUser.value.username },
      fetchPolicy: 'network-only'
    });
    
    userRooms.value = data.roomsParticipatedByUser || [];
  } catch (error) {
    console.error('Error loading user rooms:', error);
  } finally {
    loadingUserRooms.value = false;
  }
}

async function fetchRecommendedRooms() {
  if (!authStore.isAuthenticated || !currentUser.value) return;
  
  try {
    loadingRecommendations.value = true;
    
    // TODO: refactor this to use a more sophisticated recommendation algorithm
    // Using the not-participated-by-user query as a simple recommendation system
    const { data } = await apolloClient.query({
      query: ROOMS_NOT_PARTICIPATED_BY_USER_QUERY,
      variables: { userSlug: currentUser.value.username },
      fetchPolicy: 'network-only'
    });
    
    // Show only a few recommendations
    recommendedRooms.value = (data.roomsNotParticipatedByUser || []).slice(0, 3);
  } catch (error) {
    console.error('Error loading recommended rooms:', error);
  } finally {
    loadingRecommendations.value = false;
  }
}

// Lifecycle hooks
onMounted(async () => {
  try {
    window.addEventListener('resize', handleResize);
    handleResize(); // Initialize the view state
    
    await authStore.initialize();
    
    // Fetch initial data
    await Promise.all([
      fetchRooms(),
      fetchTopics()
    ]);
    
    pendingTopics.value = [...selectedTopics.value];
    
    // Fetch user-specific data
    if (authStore.isAuthenticated) {
      await fetchCurrentUser();
      
      if (currentUser.value) {
        await Promise.all([
          fetchUserRooms(),
          fetchRecommendedRooms()
        ]);
      }
    }
  } catch (error) {
    notifications.error('Error initializing home page');
    console.error(error);
  }
});

// Watch for authentication changes
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await fetchCurrentUser();
    if (currentUser.value) {
      await Promise.all([
        fetchUserRooms(),
        fetchRecommendedRooms()
      ]);
    }
  } else {
    currentUser.value = null;
    userRooms.value = [];
    recommendedRooms.value = [];
  }
});

// Cleanup event listeners
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* Main layout */
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-color);
}

/* Main content layout */
.main-content {
  display: flex;
  flex: 1;
  position: relative;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--white);
  border-right: 1px solid var(--border-color);
  padding: 0;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  transition: all 0.3s ease;
  z-index: 30;
}

.mobile-sidebar {
  position: fixed;
  left: -260px;
  top: 0;
  bottom: 0;
  height: 100vh;
  z-index: 20;
  box-shadow: var(--shadow);
}

.close-sidebar-button {
  display: flex;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.close-sidebar-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
}

.close-sidebar-button {
  display: none;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.close-sidebar-button:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.sidebar-section {
  padding: 1rem;
}

.filter-group {
  margin-bottom: 1.5rem;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-light);
}

.topic-search {
  margin-bottom: 1rem;
}

.topic-search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  box-sizing: border-box;
  border-radius: var(--radius);
  font-size: 0.9rem;
  color: var(--text-color);
  background-color: var(--bg-color);
}

.topic-search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.topic-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.topic-filter {
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  font-size: 0.85rem;
  cursor: pointer;
  transition: var(--transition);
}

.topic-filter:hover {
  border-color: var(--primary-color);
}

.topic-filter.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-apply-filters, .btn-reset-filters {
  width: 100%;
  padding: 0.6rem;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  transition: var(--transition);
}

.btn-apply-filters {
  background-color: var(--primary-color);
  color: white;
  border: none;
}

.btn-apply-filters:hover {
  background-color: var(--primary-hover);
}

.btn-reset-filters {
  background-color: var(--white);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-reset-filters:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

/* Content area */
.content-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  margin-left: 260px; /* Add this line to create space for the sidebar */
}

/* Home search (in content area) */
.home-search {
  display: flex;
  margin-bottom: 1.5rem;
  gap: 0.5rem;
}

.search-input-container {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
  pointer-events: none;
}

.search-input-container input {
  width: 100%;
  padding: 0.6rem 2.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  font-size: 0.9rem;
  transition: var(--transition);
  color: var(--text-color);
  background-color: var(--bg-color);
}

.search-input-container input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.btn-search {
  padding: 0 1rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-search:hover {
  background-color: var(--primary-hover);
}

.filter-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  background-color: var(--white);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.filter-toggle-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

/* Welcome section */
.welcome-section {
  background-color: var(--white);
  border-radius: var(--radius);
  padding: 2.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow);
  background-image: linear-gradient(to right, rgba(79, 70, 229, 0.1), rgba(79, 70, 229, 0.05));
  border-left: 5px solid var(--primary-color);
}

.welcome-section h1 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.75rem;
  color: var(--text-color);
}

.welcome-subtitle {
  margin-bottom: 1.5rem;
  color: var(--text-light);
  font-size: 1.1rem;
}

.welcome-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-create-room {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border-radius: var(--radius);
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.btn-create-room:hover {
  background-color: var(--primary-hover);
}

.btn-login {
  padding: 0.75rem 1.5rem;
  background-color: var(--white);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.btn-login:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

/* Rooms sections */
.rooms-section {
  background-color: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.joined-rooms-section h2, .recommended-section h2 {
  color: var(--primary-color);
}

.section-controls {
  display: flex;
  gap: 0.5rem;
}

.view-toggle-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 0.3rem 0.6rem;
  color: var(--text-light);
  cursor: pointer;
  transition: var(--transition);
}

.view-toggle-btn:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* Room cards */
.rooms-container {
  display: grid;
  gap: 1rem;
}

.rooms-container.grid-view {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.rooms-container.list-view {
  grid-template-columns: 1fr;
}

.room-card {
  background-color: var(--bg-color);
  border-radius: var(--radius);
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  border-color: var(--primary-color);
}

.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.room-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.room-topic {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  background-color: var(--primary-color);
  color: white;
  font-weight: 500;
}

.room-description {
  flex: 1;
  margin-bottom: 1rem;
  color: var(--text-color);
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.room-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-light);
  font-size: 0.8rem;
}

.room-date, .room-host {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* Loading states */
.rooms-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
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

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .mobile-sidebar {
    display: block;
  }
  
  .mobile-sidebar.sidebar-visible {
    left: 0;
  }
  
  .filter-toggle-btn {
    display: flex;
  }
  
  .content-area {
    margin-left: 0; /* Remove margin on mobile */
  }
}
</style>
