<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <div class="tabs">
            <button 
              :class="['tab-btn', { active: activeTab === 'login' }]" 
              @click="activeTab = 'login'"
            >
              Login
            </button>
            <button 
              :class="['tab-btn', { active: activeTab === 'register' }]" 
              @click="activeTab = 'register'"
            >
              Register
            </button>
          </div>
        </div>
        
        <div class="form-content">
          <transition name="fade" mode="out-in">
            <login-component
              v-if="activeTab === 'login'"
              @login-success="handleLoginSuccess"
              @switch-to-register="activeTab = 'register'"
              key="login"
            />
            <register-component
              v-else
              @register-success="handleRegisterSuccess"
              @switch-to-login="activeTab = 'login'"
              key="register"
            />
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import LoginComponent from '@/components/LoginComponent.vue';
import RegisterComponent from '@/components/RegisterComponent.vue';

const router = useRouter();
const route = useRoute();

const activeTab = ref('login');

function handleLoginSuccess() {
  // Redirect to the homepage or intended destination
  const redirectPath = route.query.redirect || '/';
  router.push(redirectPath);
}

function handleRegisterSuccess() {
  // After successful registration, you might want to:
  // 1. Auto-login the user or
  // 2. Switch to login tab with a success message
  router.push('/');
}
</script>

<style scoped>
@import "@/assets/styles/form-layout.css";
</style>