<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>Create New Room</h2>
        </div>
        
        <div class="form-content">
          <create-room-form />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import CreateRoomForm from '@/components/CreateRoomForm.vue';
</script>

<style scoped>
@import "@/assets/styles/form-layout.css";

.form-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
}
</style>
