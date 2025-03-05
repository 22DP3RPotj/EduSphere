<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <input 
        v-model="email" 
        type="email" 
        placeholder="Email" 
        autocomplete="email" 
        required
      >
      <input 
        v-model="password" 
        type="password" 
        placeholder="Password" 
        autocomplete="current-password" 
        required
      >
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
  </div>
</template>



<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthApi } from "@/api/auth.api";

const router = useRouter();
const { login } = useAuthApi();

const email = ref('');
const password = ref('');
const isLoading = ref(false);

async function handleLogin() {
  if (!email.value || !password.value) return;

  isLoading.value = true;
  const success = await login(email.value, password.value);
  isLoading.value = false;

  if (success) {
    router.push("/create-room");
  }
}
</script>