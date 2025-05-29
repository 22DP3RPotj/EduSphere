<template>
  <div>
    <!-- Collapsed Side Panel Button (Tab) -->
  <button 
    class="panel-tab" 
    :class="{ 'open': isPanelOpen }" 
    @click="togglePanel"
  >
    <font-awesome-icon :icon="isPanelOpen ? 'chevron-right' : 'chevron-left'" />
  </button>
    
    <!-- Backdrop (only visible when panel is open) -->
    <div 
      v-if="isPanelOpen" 
      class="panel-backdrop" 
      @click="closePanel"
    ></div>
    
    <!-- Side Panel -->
    <div class="side-panel" :class="{ 'open': isPanelOpen }">
      <div class="panel-inner">
        <!-- Logo/Home Link -->
        <div class="panel-section logo-section">
          <router-link to="/" class="logo-link" @click="closePanel">
            <span class="logo-text">Chat App</span>
          </router-link>
        </div>
        
        <!-- Main Navigation -->
        <div class="panel-section nav-section">
          <router-link to="/" class="nav-item" active-class="active" @click="closePanel">
            <font-awesome-icon icon="home" class="nav-icon" />
            <span class="nav-label">Home</span>
          </router-link>
          
          <router-link v-if="isAuthenticated" to="/create-room" class="nav-item" active-class="active" @click="closePanel">
            <font-awesome-icon icon="plus-circle" class="nav-icon" />
            <span class="nav-label">Create Room</span>
          </router-link>
        </div>
        
        <!-- User Section (bottom) -->
        <div class="panel-section user-section">
          <button @click="toggleTheme" class="theme-toggle-btn">
            <font-awesome-icon :icon="isDarkMode ? 'sun' : 'moon'" />
            <span>{{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}</span>
          </button>

          <template v-if="isAuthenticated">
            <router-link :to="`/user/${currentUser?.username}`" class="user-profile" @click="closePanel">
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
            <router-link to="/login" class="login-btn compact" @click="closePanel">
              <font-awesome-icon icon="sign-in-alt" />
              <span>Login</span>
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import { useAuthApi } from '@/api/auth.api';

const authStore = useAuthStore();
const { logout, fetchAuthStatus } = useAuthApi();

const currentUser = ref(null);
const isAuthenticated = computed(() => authStore.isAuthenticated);
const isPanelOpen = ref(false);
const isDarkMode = ref(false);

function togglePanel() {
  isPanelOpen.value = !isPanelOpen.value;
}

function closePanel() {
  isPanelOpen.value = false;
}

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark', isDarkMode.value)
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

async function handleLogout() {
  await logout();
  closePanel();
}

async function fetchCurrentUser() {
  const { isAuthenticated, user } = await fetchAuthStatus();
    
  if (isAuthenticated) {
    currentUser.value = user;
    authStore.setUser(user);
  }
}

watch(
  isAuthenticated,
  async (newVal) => {
    if (newVal) await fetchCurrentUser();
    else currentUser.value = null;
  },
  { immediate: true }
);

watch(
  () => authStore.user,
  (newUser) => {
    if (newUser && isAuthenticated.value) {
      currentUser.value = newUser;
    }
  },
  { deep: true }
);

onMounted(() => {
  isDarkMode.value = localStorage.getItem('theme') === 'dark'
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped>
.side-panel {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background-color: var(--white);
  border-left: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  z-index: 100;
  transition: width 0.3s ease;
  overflow: hidden;
}

.side-panel.open {
  width: 250px;
  max-width: 80vw;
}

.panel-inner {
  width: 250px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-tab {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 30px;
  height: 60px;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-right: none;
  border-radius: 8px 0 0 8px;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 101;
  color: var(--text-light);
  transition: var(--transition);
}

.panel-tab:hover {
  color: var(--text-color);
  background-color: var(--bg-color);
}

.panel-tab.open {
  right: 250px;
}

@media (max-width: 768px) {
  .panel-tab.open {
    right: 250px;
  }
}

.panel-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 99;
}

.panel-section {
  padding: 1rem;
  box-sizing: border-box;
  width: 100%;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  transition: var(--transition);
  margin-bottom: 0.5rem;
}

.theme-toggle-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

.logo-section {
  border-bottom: 1px solid var(--border-color);
  padding: 1.5rem 1rem;
}

.nav-section {
  flex-grow: 1;
}

.user-section {
  border-top: 1px solid var(--border-color);
}

.logo-link {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
  transition: var(--transition);
  display: block;
}

.logo-link:hover {
  color: var(--primary-hover);
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
  transition: var(--transition);
}

.nav-item:hover, .nav-item.active {
  background-color: var(--bg-color);
}

.nav-icon {
  width: 20px;
  margin-right: 12px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  color: var(--text-color);
  margin-bottom: 0.5rem;
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
  width: 100%;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-color);
  text-decoration: none;
}

.login-btn.compact {
  width: auto;
  display: inline-flex;
  padding: 0.5rem 1rem;
}

.logout-btn:hover, .login-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .side-panel.open {
    width: 250px;
  }
}
</style>