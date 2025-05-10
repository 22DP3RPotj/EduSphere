<template>
  <div class="auth-form-container">
    <form @submit.prevent="handleRegister" class="auth-form">
      <h2 class="form-title">Register</h2>
      
      <div class="form-group">
        <label for="username">Username</label>
        <input 
          id="username"
          v-model="username" 
          type="text" 
          placeholder="Choose a username"
          autocomplete="username" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="name">Full Name</label>
        <input 
          id="name"
          v-model="name" 
          type="text" 
          placeholder="Enter your full name"
          autocomplete="name" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="reg-email">Email</label>
        <input 
          id="reg-email"
          v-model="email" 
          type="email" 
          placeholder="Enter your email"
          autocomplete="email" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="password1">Password</label>
        <input 
          id="password1"
          v-model="password1" 
          type="password" 
          placeholder="Create a password"
          autocomplete="new-password" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="password2">Confirm Password</label>
        <input 
          id="password2"
          v-model="password2" 
          type="password" 
          placeholder="Confirm your password"
          autocomplete="new-password" 
          required
        >
      </div>
      
      <p v-if="error" class="error-message">{{ error }}</p>
      
      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Registering...' : 'Register' }}
      </button>
      
      <div class="form-footer">
        <p>Already have an account? 
          <a href="#" @click.prevent="$emit('switchToLogin')">Login</a>
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';
import { useAuthApi } from "@/api/auth.api";

const emit = defineEmits(['registerSuccess', 'switchToLogin']);

const { registerUser } = useAuthApi();

const username = ref('');
const name = ref('');
const email = ref('');
const password1 = ref('');
const password2 = ref('');
const error = ref(null);
const isLoading = ref(false);

async function handleRegister() {
  error.value = null;

  if (!username.value || !name.value || !email.value || !password1.value || !password2.value) {
    error.value = "Please fill in all fields";
    return;
  }


  if (password1.value !== password2.value) {
    error.value = "Passwords do not match";
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
    emit('registerSuccess');
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
</style>
