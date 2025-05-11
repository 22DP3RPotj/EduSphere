<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>Create New Room</h2>
        </div>
        
        <div class="form-content">
          <create-room-form @room-created="handleRoomCreated" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import CreateRoomForm from '@/components/CreateRoomForm.vue';

const router = useRouter();

function handleRoomCreated() {
  router.push('/');
}
</script>

<style scoped>
@import "@/assets/styles/form-layout.css";

.form-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
}
</style>
