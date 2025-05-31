<template>
  <div class="auth-form-container">
    <form class="auth-form" @submit.prevent="handleLogin">
      <h2 class="form-title">Login</h2>
      
      <div class="form-group">
        <label for="email">Email</label>
        <input 
          id="email"
          v-model="email" 
          type="email" 
          placeholder="Enter your email"
          autocomplete="email" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="password">Password</label>
        <input 
          id="password"
          v-model="password" 
          type="password" 
          placeholder="Enter your password"
          autocomplete="current-password" 
          required
        >
      </div>
      
      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
      
      <div class="form-footer">
        <p>Don't have an account? 
          <a href="#" @click.prevent="$emit('switchToRegister')">Register</a>
        </p>
      </div>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineEmits } from 'vue';
import { useAuthApi } from "@/api/auth.api";

const emit = defineEmits(['loginSuccess', 'switchToRegister']);

const { login } = useAuthApi();

const email = ref<string>('');
const password = ref<string>('');
const isLoading = ref<boolean>(false);

async function handleLogin() {
  if (!email.value || !password.value) return;

  isLoading.value = true;
  const success = await login(email.value, password.value);
  isLoading.value = false;

  if (success) {
    emit('loginSuccess');
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
</style>
