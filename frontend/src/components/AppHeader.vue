<template>
  <header class="app-header">
    <div class="header-logo">
      <router-link to="/" class="logo-link">Chat App</router-link>
    </div>
    
    <div class="header-user">
      <template v-if="isAuthenticated">
        <router-link :to="`/user/${currentUser?.username}`" class="user-profile">
          <img 
            :src="currentUser?.avatar ? `/media/${currentUser.avatar}` : '/default.svg'" 
            :alt="`${currentUser?.username}'s avatar`" 
            class="user-avatar"
          />
          <div class="user-info">
            <span class="user-name">{{ currentUser?.name || currentUser?.username }}</span>
            <span class="user-username">@{{ currentUser?.username }}</span>
          </div>
        </router-link>
        <button @click="handleLogout" class="logout-btn">
          <font-awesome-icon icon="sign-out-alt" />
          <span>Logout</span>
        </button>
      </template>
      <template v-else>
        <router-link to="/login" class="login-btn">
          <font-awesome-icon icon="sign-in-alt" />
          <span>Login</span>
        </router-link>
        <router-link to="/register" class="register-btn">Register</router-link>
      </template>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { useAuthApi } from '@/api/auth.api';
import { useNotifications } from '@/composables/useNotifications';
import { apolloClient } from '@/api/apollo.client';
import { USER_QUERY } from '@/api/graphql/room.queries';

const router = useRouter();
const authStore = useAuthStore();
const { logout } = useAuthApi();
const notifications = useNotifications();

// User state
const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = ref(null);

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

async function handleLogout() {
  try {
    await logout();
    router.push('/login');
  } catch (error) {
    notifications.error('Error logging out');
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await fetchCurrentUser();
  }
});
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background-color: var(--white);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-logo {
  flex-shrink: 0;
}

.logo-link {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
  transition: var(--transition);
}

.logo-link:hover {
  color: var(--primary-hover);
}

.header-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  color: var(--text-color);
}

.user-profile:hover {
  background-color: var(--bg-color);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  line-height: 1.2;
}

.user-username {
  font-size: 0.8rem;
  color: var(--text-light);
}

.logout-btn, .login-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  text-decoration: none;
}

.logout-btn:hover, .login-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

.register-btn {
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  background-color: var(--primary-color);
  color: white;
  font-weight: 500;
  text-decoration: none;
  transition: var(--transition);
}

.register-btn:hover {
  background-color: var(--primary-hover);
}
</style>