<template>
  <div class="auth-form-container">
    <form class="auth-form" @submit.prevent="handleRegister">
      <h2 class="form-title">Register</h2>
      
      <div class="form-group">
        <label for="username">Username</label>
        <input 
          id="username"
          v-model="registerForm.username" 
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
          v-model="registerForm.name" 
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
          v-model="registerForm.email" 
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
          v-model="registerForm.password1" 
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
          v-model="registerForm.password2" 
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

<script lang="ts" setup>
import { ref, defineEmits } from 'vue';
import { useAuthApi } from "@/api/auth.api";

const emit = defineEmits(['registerSuccess', 'switchToLogin']);

const { registerUser } = useAuthApi();

const registerForm = ref({
  username: '',
  name: '',
  email: '',
  password1: '',
  password2: ''
});
const error = ref<string | null>(null);
const isLoading = ref<boolean>(false);

function validateRegisterForm(form: typeof registerForm.value): string | null {
  if (!form.username || !form.name || !form.email || !form.password1 || !form.password2) {
    return "Please fill in all fields";
  }
  if (form.password1 !== form.password2) {
    return "Passwords do not match";
  }
  return null;
}

async function handleRegister() {
  error.value = validateRegisterForm(registerForm.value);
  if (error.value) return;

  isLoading.value = true;
  const success = await registerUser({ ...registerForm.value });
  isLoading.value = false;

  if (success) {
    emit('registerSuccess');
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';
</style>
