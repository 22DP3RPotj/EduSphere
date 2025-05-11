<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apolloClient } from '@/api/apollo.client';
import { useNotifications } from '@/composables/useNotifications';

import {
    USER_QUERY
} from '@/api/graphql/room.queries';

import UserAvatar from '@/components/UserAvatar.vue';

const route = useRoute();
const router = useRouter();
const notifications = useNotifications();

const user = ref(null);
const loading = ref(true);
const error = ref(null);

// Fetch the user data
async function fetchUser() {
  loading.value = true;
  error.value = null;
  
  try {
    const { data } = await apolloClient.query({
      query: USER_QUERY,
      variables: { username: route.params.username },
      fetchPolicy: 'network-only'
    });
    
    user.value = data.user;
  } catch (err) {
    error.value = err;
    notifications.error('Error loading user profile');
  } finally {
    loading.value = false;
  }
}

// Navigate back
function goBack() {
  router.back();
}

onMounted(() => {
  fetchUser();
});
</script>

<template>
  <div class="profile-container">
    <!-- Header with back button -->
    <div class="profile-header">
      <button @click="goBack" class="back-button">
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
      
      <!-- Profile tabs - can be expanded later -->
      <div class="profile-tabs">
        <div class="tab active">Activity</div>
        <div class="tab">Rooms</div>
      </div>
      
      <!-- Placeholder for user activity feed -->
      <div class="profile-feed">
        <div class="empty-feed">
          <font-awesome-icon icon="comment-alt" size="2x" />
          <p>No recent activity to show</p>
        </div>
      </div>
    </div>
    
    <!-- User not found -->
    <div v-else class="profile-not-found">
      <font-awesome-icon icon="user-slash" size="3x" />
      <h2>User not found</h2>
      <p>The user you're looking for doesn't exist or is unavailable.</p>
      <button @click="goBack" class="back-link">
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

.retry-button {
  margin-top: 1rem;
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
}

.retry-button:hover {
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
  padding: 1rem 1.5rem;
  font-weight: 500;
  color: var(--text-light);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
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

.profile-feed {
  flex: 1;
  padding: 2rem 1rem;
}

.empty-feed {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: var(--text-light);
  text-align: center;
}

.empty-feed svg {
  margin-bottom: 1rem;
  opacity: 0.5;
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
  
  .tab {
    flex: 1;
    text-align: center;
    padding: 1rem 0;
  }
}
</style>