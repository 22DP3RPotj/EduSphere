<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-header">
          <h2>{{ t('room.createRoom') }}</h2>
        </div>
        
        <div class="form-content">
          <create-room-form />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useI18n } from 'vue-i18n';
import CreateRoomForm from '@/components/forms/CreateRoom.vue';

const { t } = useI18n();
</script>

<style scoped>
@import "@/assets/styles/form-layout.css";

.form-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
}
</style>
