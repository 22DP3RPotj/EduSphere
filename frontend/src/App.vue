<template>
  <div class="app-container">
    <side-panel></side-panel>
    <main class="main-content">
      <router-view v-if="isReady"></router-view>
      <div v-else class="loading-container">
        <p>Loading...</p>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import authTokenService from '@/services/refresh-token';
import SidePanel from '@/components/SidePanel.vue';

export default {
  name: 'App',
  components: {
    SidePanel
  },
  setup() {
    const authStore = useAuthStore();
    const isReady = ref(false);

    onMounted(() => {
      authStore.initialize();
      
      authTokenService.init();
      
      // Watcher for auth state changes
      const unwatchAuth = watch(
        () => authStore.isAuthenticated,
        (isAuthenticated) => {
          authTokenService.handleAuthChange(isAuthenticated);
        },
        { immediate: true }
      );
      
      isReady.value = true;
      
      onUnmounted(() => {
        unwatchAuth();
        authTokenService.cleanup();
      });
    });

    return {
      isReady
    };
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex-grow: 1;
  width: 100%;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>