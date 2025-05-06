<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <input 
        v-model="username" 
        type="text" 
        placeholder="Username" 
        autocomplete="username" 
        required
      >
      <input 
        v-model="name" 
        type="text" 
        placeholder="Name" 
        autocomplete="name" 
        required
      >
      <input 
        v-model="email" 
        type="email" 
        placeholder="Email" 
        autocomplete="email" 
        required
      >
      <input 
        v-model="password1" 
        type="password" 
        placeholder="Password" 
        autocomplete="new-password" 
        required
      >
      <input 
        v-model="password2" 
        type="password" 
        placeholder="Confirm Password" 
        autocomplete="new-password" 
        required
      >
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>


<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthApi } from "@/api/auth.api";

const router = useRouter();
const { registerUser } = useAuthApi();

const username = ref('');
const name = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const error = ref(null);
const isLoading = ref(false);

async function handleRegister() {
  // Reset error
  error.value = null;

  // Validate inputs
  if (!username.value || !name.value || !email.value || !password1.value || !password2.value) {
    error.value = "Please fill in all fields";
    return;
  }

  isLoading.value = true;
  const success = await registerUser(
    username.value, 
    name.value, 
    email.value, 
    password1.value, 
    password2.value
  );
  isLoading.value = false;

  if (success) {
    router.push("/");
  }
}
</script>