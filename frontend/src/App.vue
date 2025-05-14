<template>
  <div>
    <app-header></app-header>
    <router-view v-if="isReady"></router-view>
    <div v-else class="loading-container">
      <p>Loading...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import authTokenService from '@/services/refresh-token';
import AppHeader from '@/components/AppHeader.vue';

export default {
  name: 'App',
  components: {
    AppHeader
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
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>