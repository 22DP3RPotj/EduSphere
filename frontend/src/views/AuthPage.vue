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
            <login-form
              v-if="activeTab === 'login'"
              key="login"
              @login-success="handleLoginSuccess"
              @switch-to-register="activeTab = 'register'"
            />
            <register-form
              v-else
              key="register"
              @register-success="handleRegisterSuccess"
              @switch-to-login="activeTab = 'login'"
            />
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

import LoginForm from '@/components/LoginForm.vue';
import RegisterForm from '@/components/RegisterForm.vue';

const router = useRouter();
const route = useRoute();

const activeTab = ref('login');

function handleLoginSuccess() {
  let redirectPath = route.query.redirect || '/';
  if (Array.isArray(redirectPath)) {
    redirectPath = redirectPath[0] || '/';
  }
  router.push(redirectPath as string);
}

function handleRegisterSuccess() {
  router.push('/');
}
</script>

<style scoped>
@import "@/assets/styles/form-layout.css";
</style>
