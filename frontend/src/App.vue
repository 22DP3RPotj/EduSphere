<template>
  <router-view v-if="isReady"></router-view>
  <div v-else class="loading-container">
    <p>Loading...</p>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import authTokenService from '@/services/refresh-token';

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore();
    const isReady = ref(false);

    onMounted(() => {
      // Initialize auth store
      authStore.initialize();
      
      // Initialize token service
      authTokenService.init();
      
      // Set up the watcher for auth state changes
      const unwatchAuth = watch(
        () => authStore.isAuthenticated,
        (isAuthenticated) => {
          authTokenService.handleAuthChange(isAuthenticated);
        },
        { immediate: true }
      );
      
      // App is ready to display
      isReady.value = true;
      
      // Clean up on unmount
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
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>