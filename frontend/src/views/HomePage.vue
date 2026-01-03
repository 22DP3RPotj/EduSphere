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
          <!-- Error display for topics -->
          <div v-if="homepageErrors.generalErrors.length > 0" class="error-message sidebar-error">
            <font-awesome-icon icon="exclamation-circle" />
            <div class="error-list">
              <p v-for="(errMsg, index) in homepageErrors.generalErrors" :key="index">{{ errMsg }}</p>
            </div>
          </div>

          <div class="filter-group">
            <label for="topic-search">Topics</label>
            <div class="autocomplete-wrapper">
              <input
                id="topic-search"
                v-model="topicSearchQuery" 
                type="text" 
                placeholder="Search topics..." 
                class="topic-search-input"
                autocomplete="off"
                @input="onTopicInput"
                @keydown.down.prevent="onArrowDown"
                @keydown.up.prevent="onArrowUp"
                @keydown.enter="onEnter"
                @blur="hideSuggestions"
                @keydown.esc="showTopicSuggestions = false"
                @focus="onTopicFocus"
              />
              <div v-show="showTopicSuggestions" class="suggestions-list">
                <div v-if="loadingHomepage && !topics.length" class="loading-suggestions">
                  <div class="spinner"></div>
                  <span>Loading topics...</span>
                </div>
                <template v-else>
                  <div
                    v-for="(topic, index) in filteredTopics"
                    :key="topic.name"
                    :class="['suggestion-item', { 
                      active: index === selectedTopicIndex,
                      selected: pendingTopics.includes(topic.name)
                    }]"
                    @mousedown="selectTopic(topic.name)"
                    @mouseenter="selectedTopicIndex = index"
                  >
                    <span>{{ topic.name }}</span>
                    <span v-if="pendingTopics.includes(topic.name)" class="selected-indicator">
                      <font-awesome-icon icon="check" />
                    </span>
                  </div>
                  <div v-if="filteredTopics.length === 0 && topicSearchQuery" class="no-suggestions">
                    No matching topics found
                  </div>
                </template>
              </div>
            </div>
            
            <!-- Selected topics display -->
            <div v-if="pendingTopics.length > 0" class="selected-topics">
              <div class="selected-topics-label">Selected:</div>
              <div class="selected-topics-list">
                <span 
                  v-for="topicName in pendingTopics" 
                  :key="topicName"
                  class="selected-topic-tag"
                >
                  {{ topicName }}
                  <button 
                    type="button" 
                    class="remove-topic-btn"
                    :title="`Remove ${topicName}`"
                    @click="removeTopic(topicName)"
                  >
                    <font-awesome-icon icon="times" />
                  </button>
                </span>
              </div>
            </div>
          </div>
          
          <div class="filter-buttons-container">
            <button class="btn-apply-filters" @click="applyFilters">
              <font-awesome-icon icon="filter" />
              Apply Filters
            </button>
            
            <button 
              v-show="hasActiveFilters" 
              class="btn-reset-filters" 
              @click="resetFilters"
            >
              <font-awesome-icon icon="times-circle" />
              Reset Filters
            </button>
            <div v-show="!hasActiveFilters" class="btn-reset-filters-placeholder"></div>
          </div>
        </div>
      </div>

      <div class="content-area">
        <!-- Search bar for homepage only -->
        <div class="home-search">
          <div class="search-input-container">
            <font-awesome-icon icon="search" class="search-icon" />
            <input
              id="room-search"
              v-model="searchInputQuery" 
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

          <!-- Reserve minimum height for content area to prevent CLS -->
          <div class="rooms-content" :style="{ minHeight: getMinContentHeight('rooms') }">
            <!-- Error state for rooms -->
            <div v-if="homepageErrors.generalErrors.length > 0" class="error-state">
              <font-awesome-icon icon="exclamation-triangle" size="2x" />
              <p>Failed to load rooms</p>
              <div class="error-details">
                <p v-for="(errMsg, index) in homepageErrors.generalErrors" :key="index">{{ errMsg }}</p>
              </div>
              <button class="btn-retry" @click="() => refetch()">Try Again</button>
            </div>

            <!-- Loading state -->
            <div v-else-if="loadingHomepage" class="rooms-loading">
              <div class="spinner"></div>
              <p>Loading rooms...</p>
              <!-- Skeleton placeholders to reserve space -->
              <div :class="['rooms-container', 'skeleton-container', isGridView ? 'grid-view' : 'list-view']">
                <div v-for="n in 6" :key="n" class="room-card-skeleton"></div>
              </div>
            </div>

            <!-- No results state -->
            <div v-else-if="rooms.length === 0" class="no-rooms">
              <font-awesome-icon icon="comment-slash" size="3x" />
              <p>No rooms found matching your criteria</p>
              <button class="btn-reset-filters" @click="resetFilters">Reset filters</button>
            </div>

            <!-- Rooms grid/list -->
            <div v-else :class="['rooms-container', isGridView ? 'grid-view' : 'list-view']">
              <button 
                v-for="room in rooms" 
                :key="room.id"
                class="room-card"
                @click="navigateToRoom(room)"
              >
                <div class="room-card-header">
                  <h3 class="room-name">{{ room.name }}</h3>
                  <div class="room-topics">
                    <span 
                      v-for="topic in room.topics" 
                      :key="topic.name" 
                      class="room-topic"
                    >
                      {{ topic.name }}
                    </span>
                  </div>
                </div>
                <div class="room-description">{{ room.description }}</div>
                <div class="room-meta">
                  <span class="room-date">
                    <font-awesome-icon icon="calendar-alt" />
                    {{ formatDate(room.created_at) }}
                  </span>
                  <span class="room-host">
                    <font-awesome-icon icon="user" />
                    {{ room.host.username }}
                  </span>
                </div>
              </button>
            </div>
          </div>
        </section>

        <!-- Your Rooms Section (if authenticated) - Always render container to prevent CLS -->
        <section v-if="isAuthenticated" class="rooms-section joined-rooms-section">
          <div class="section-header">
            <h2>
              <font-awesome-icon :icon="['fas', 'user-circle']" />
              Joined Rooms
            </h2>
          </div>

          <div class="rooms-content" :style="{ minHeight: getMinContentHeight('userRooms') }">
            <!-- Error state for user rooms -->
            <div v-if="userRoomsErrors.generalErrors.length > 0" class="error-state">
              <font-awesome-icon icon="exclamation-triangle" size="2x" />
              <p>Failed to load your rooms</p>
              <button class="btn-retry" @click="() => refetchUserRooms()">Try Again</button>
            </div>

            <!-- Loading state -->
            <div v-else-if="loadingUserRooms" class="rooms-loading">
              <div class="spinner"></div>
              <p>Loading your rooms...</p>
              <div class="rooms-container grid-view skeleton-container">
                <div v-for="n in 3" :key="n" class="room-card-skeleton"></div>
              </div>
            </div>

            <!-- No rooms state -->
            <div v-else-if="userRooms.length === 0" class="no-rooms">
              <font-awesome-icon icon="door-closed" size="2x" />
              <p>You haven't joined any rooms yet</p>
              <router-link to="/create-room" class="btn-create-room-small">Create your first room</router-link>
            </div>

            <!-- User rooms grid -->
            <div v-else class="rooms-container grid-view">
              <button 
                v-for="room in userRooms" 
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
                    {{ formatDate(room.created_at) }}
                  </span>
                  <span class="room-host">
                    <font-awesome-icon icon="user" />
                    {{ room.host.username }}
                  </span>
                </div>
              </button>
            </div>
          </div>
        </section>

        <!-- Recommendations Section - Always render container to prevent CLS -->
        <section v-if="isAuthenticated" class="rooms-section recommended-section">
          <div class="section-header">
            <h2>
              <font-awesome-icon :icon="['fas', 'star']" />
              Recommended For You
            </h2>
          </div>

          <div class="rooms-content" :style="{ minHeight: getMinContentHeight('recommendations') }">
            <!-- Error state for recommendations -->
            <div v-if="userRoomsErrors.generalErrors.length > 0" class="error-state">
              <font-awesome-icon icon="exclamation-triangle" size="2x" />
              <p>Failed to load recommendations</p>
              <button class="btn-retry" @click="() => refetchUserRooms()">Try Again</button>
            </div>

            <!-- Loading state -->
            <div v-else-if="loadingUserRooms" class="rooms-loading">
              <div class="spinner"></div>
              <p>Finding recommendations...</p>
              <div class="rooms-container grid-view skeleton-container">
                <div v-for="n in 3" :key="n" class="room-card-skeleton"></div>
              </div>
            </div>

            <!-- No recommendation state -->
            <div v-else-if="recommendedRooms.length === 0" class="no-rooms">
              <font-awesome-icon icon="compass" size="2x" />
              <p>No recommendations available right now</p>
            </div>

            <!-- Recommended rooms grid -->
            <div v-else class="rooms-container grid-view">
              <button 
                v-for="room in recommendedRooms" 
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
                    {{ formatDate(room.created_at) }}
                  </span>
                  <span class="room-host">
                    <font-awesome-icon icon="user" />
                    {{ room.host.username }}
                  </span>
                </div>
              </button>
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
import { useHomepageInitialQuery, useUserRoomsQuery } from '@/composables/useHomePage';
import { parseGraphQLError } from '@/utils/errorParser';

import type { Room, Topic } from '@/types';

const router = useRouter();
const authStore = useAuthStore();

// User state
const isAuthenticated = computed(() => authStore.isAuthenticated);

// UI state
const isGridView = ref<boolean>(true);
const showSidebar = ref<boolean>(window.innerWidth > 768);
const isMobileView = ref<boolean>(window.innerWidth <= 768);
const showTopicSuggestions = ref<boolean>(false);
const selectedTopicIndex = ref<number>(-1);

// Filter state
const searchInputQuery = ref<string>('');
const appliedSearchQuery = ref<string>('');
const topicSearchQuery = ref<string>('');
const selectedTopics = ref<string[]>([]);
const pendingTopics = ref<string[]>([]);

// Use composables for queries
const { 
  rooms, 
  topics, 
  loading: loadingHomepage, 
  error: homepageError,
  refetch 
} = useHomepageInitialQuery(
  computed(() => appliedSearchQuery.value),
  computed(() => selectedTopics.value)
);

const { 
  userRooms, 
  recommendedRooms: allRecommendedRooms, 
  loading: loadingUserRooms, 
  error: userRoomsError,
  refetch: refetchUserRooms 
} = useUserRoomsQuery(
  computed(() => authStore.user?.username || '')
);

// Show only first 3 recommendations
const recommendedRooms = computed(() => allRecommendedRooms.value.slice(0, 3));

// Error handling
const homepageErrors = computed(() => {
  if (!homepageError.value) return { fieldErrors: {}, generalErrors: [] };
  return parseGraphQLError(homepageError.value);
});

const userRoomsErrors = computed(() => {
  if (!userRoomsError.value) return { fieldErrors: {}, generalErrors: [] };
  return parseGraphQLError(userRoomsError.value);
});

// Get filtered topics based on search query
const filteredTopics = computed(() => {
  if (!topicSearchQuery.value) {
    return topics.value;
  }
  
  const query = topicSearchQuery.value.toLowerCase();
  return topics.value.filter((topic: Topic) => 
    topic.name.toLowerCase().includes(query)
  );
});

// Check if filters are active
const hasActiveFilters = computed(() => {
  return selectedTopics.value.length > 0 || appliedSearchQuery.value !== '';
});

// Function to calculate minimum height for content areas to prevent CLS
function getMinContentHeight(section: string): string {
  switch (section) {
    case 'rooms':
      return loadingHomepage.value ? '400px' : rooms.value.length === 0 ? '200px' : 'auto';
    case 'userRooms':
      return loadingUserRooms.value ? '300px' : userRooms.value.length === 0 ? '150px' : 'auto';
    case 'recommendations':
      return loadingUserRooms.value ? '300px' : recommendedRooms.value.length === 0 ? '150px' : 'auto';
    default:
      return 'auto';
  }
}

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

function selectTopic(topicName: string) {
  if (pendingTopics.value.includes(topicName)) {
    pendingTopics.value = pendingTopics.value.filter(t => t !== topicName);
  } else {
    pendingTopics.value.push(topicName);
  }
  topicSearchQuery.value = '';
  showTopicSuggestions.value = false;
  selectedTopicIndex.value = -1;
}

function scrollToSelectedTopic() {
  if (selectedTopicIndex.value >= 0) {
    const suggestionsList = document.querySelector('.suggestions-list');
    const selectedItem = suggestionsList?.children[selectedTopicIndex.value + (loadingHomepage.value ? 1 : 0)];
    
    if (suggestionsList && selectedItem) {
      const listRect = suggestionsList.getBoundingClientRect();
      const itemRect = selectedItem.getBoundingClientRect();
      
      if (itemRect.bottom > listRect.bottom) {
        suggestionsList.scrollTop += itemRect.bottom - listRect.bottom + 5;
      }

      else if (itemRect.top < listRect.top) {
        suggestionsList.scrollTop -= listRect.top - itemRect.top + 5;
      }
    }
  }
}

function removeTopic(topicName: string) {
  pendingTopics.value = pendingTopics.value.filter(t => t !== topicName);
}

function onTopicInput() {
  showTopicSuggestions.value = true;
  selectedTopicIndex.value = -1;
}

function onTopicFocus() {
  if (topics.value.length > 0) {
    showTopicSuggestions.value = true;
  }
}

function onArrowDown() {
  if (selectedTopicIndex.value < filteredTopics.value.length - 1) {
    selectedTopicIndex.value++;
    scrollToSelectedTopic();
  }
}

function onArrowUp() {
  if (selectedTopicIndex.value > -1) {
    selectedTopicIndex.value--;
    scrollToSelectedTopic();
  }
}

function onEnter(event: KeyboardEvent) {
  if (!showTopicSuggestions.value || filteredTopics.value.length === 0) {
    return;
  }

  event.preventDefault();

  if (selectedTopicIndex.value >= 0) {
    selectTopic(filteredTopics.value[selectedTopicIndex.value].name);
  } else if (filteredTopics.value.length === 1) {
    selectTopic(filteredTopics.value[0].name);
  }
}

function hideSuggestions() {
  setTimeout(() => {
    showTopicSuggestions.value = false;
    selectedTopicIndex.value = -1;
  }, 150);
}

function applyFilters() {
  selectedTopics.value = [...pendingTopics.value];
  appliedSearchQuery.value = searchInputQuery.value; // Apply the search term
}

function resetFilters() {
  searchInputQuery.value = '';
  appliedSearchQuery.value = '';
  selectedTopics.value = [];
  pendingTopics.value = [];
  topicSearchQuery.value = '';
}

function toggleView() {
  isGridView.value = !isGridView.value;
}

// Navigation functions
function navigateToRoom(room: Room) {
  router.push(`/r/${room.id}`);
}

watch(() => authStore.isAuthenticated, () => {
  if (isAuthenticated.value && authStore.user?.username) {
    refetchUserRooms();
  }
});

// Lifecycle hooks
onMounted(async () => {
  try {
    window.addEventListener('resize', handleResize);
    handleResize(); // Initialize the view state
    
    authStore.initialize();
    
    // Set initial pending topics to match selected topics
    pendingTopics.value = [...selectedTopics.value];
  } catch (error) {
    console.error('Error initializing home page:', error);
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

.autocomplete-wrapper {
  position: relative;
  margin-bottom: 1rem;
}

.topic-search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  box-sizing: border-box;
  border-radius: var(--radius);
  font-size: 0.9rem;
  color: var(--text-color);
  background-color: var(--white);
  transition: var(--transition);
}

.topic-search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.suggestions-list {
  position: absolute;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  z-index: 100;
  margin-top: 0.25rem;
  scroll-behavior: smooth;
}

.loading-suggestions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: var(--text-light);
  font-size: 0.875rem;
}

.loading-suggestions .spinner {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: var(--transition);
  color: var(--text-color);
  border-bottom: 1px solid var(--bg-color);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.active {
  background-color: var(--bg-color);
}

.suggestion-item.selected {
  background-color: rgba(79, 70, 229, 0.1);
  color: var(--primary-color);
}

.suggestion-item.selected.active {
  background-color: rgba(79, 70, 229, 0.2);
}

.selected-indicator {
  color: var(--primary-color);
  font-size: 0.8rem;
}

.no-suggestions {
  padding: 0.75rem 1rem;
  color: var(--text-light);
  font-size: 0.875rem;
  text-align: center;
}

.selected-topics {
  margin-top: 1rem;
}

.selected-topics-label {
  font-size: 0.875rem;
  color: var(--text-light);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.selected-topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-topic-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background-color: var(--primary-color);
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.remove-topic-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition);
  font-size: 0.75rem;
}

.remove-topic-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Filter buttons container to prevent CLS */
.filter-buttons-container {
  min-height: 90px; /* Reserve space for both buttons */
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

/* Placeholder for reset button to prevent CLS */
.btn-reset-filters-placeholder {
  height: 42px; /* Same height as btn-reset-filters */
  margin-bottom: 0.75rem;
}

/* Content area */
.content-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  margin-left: 260px;
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
  box-sizing: border-box;
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
  z-index: 10;
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

/* Rooms content container with min-height to prevent CLS */
.rooms-content {
  transition: min-height 0.3s ease;
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
  color: var(--text-color);
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
  /* Changed to column layout to accommodate multiple topics */
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.room-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

/* Updated styles for multiple topics */
.room-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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

/* Error states */
.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  border: 1px solid #f44336;
  color: #f44336;
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.sidebar-error {
  margin: 0 0 1rem 0;
}

.error-message svg {
  margin-top: 0.125rem;
  flex-shrink: 0;
}

.error-list p {
  margin: 0;
  font-size: 0.875rem;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  color: #f44336;
}

.error-state svg {
  margin-bottom: 1rem;
  opacity: 0.7;
}

.error-state p {
  margin-bottom: 1rem;
  font-weight: 500;
}

.error-details {
  margin-bottom: 1.5rem;
}

.error-details p {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #7f1d1d;
}

.btn-retry {
  padding: 0.5rem 1rem;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-retry:hover {
  background-color: #b91c1c;
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
    margin-left: 0;
  }
}
</style>