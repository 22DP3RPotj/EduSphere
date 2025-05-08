<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>Create New Room</h2>
        </div>
        
        <div class="form-content">
          <create-room @room-created="handleRoomCreated" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import CreateRoom from '@/components/CreateRoom.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

function handleRoomCreated() {
  router.push('/'); // Or wherever you want to redirect after creation
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
