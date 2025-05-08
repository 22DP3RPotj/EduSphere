<template>
  <div class="auth-form-container">
    <form @submit.prevent="submitRoom" class="auth-form">
      <h2 class="form-title">Create Room</h2>
      
      <div class="form-group">
        <label for="room-name">Room Name</label>
        <input
          id="room-name"
          v-model="name"
          type="text"
          placeholder="Enter room name"
          required
        >
      </div>

      <div class="form-group">
        <label for="topic-name">Topic</label>
        <input
          id="topic-name"
          v-model="topic_name"
          type="text"
          placeholder="Enter topic name"
          required
        >
      </div>

      <div class="form-group">
        <label for="description">Description <span>(optional)</span></label>
        <textarea
          id="description"
          v-model="description"
          placeholder="Add a description"
          rows="3"
        ></textarea>
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        <span v-if="isLoading" class="spinner"></span>
        {{ isLoading ? 'Creating...' : 'Create Room' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoomApi } from "@/api/room.api";

const { createRoom } = useRoomApi();

const name = ref('');
const topic_name = ref('');
const description = ref('');
const isLoading = ref(false);

async function submitRoom() {
  if (!name.value || !topic_name.value) return;

  isLoading.value = true;
  await createRoom(
    name.value, 
    topic_name.value, 
    description.value || null
  );
  isLoading.value = false;
}
</script>

<style scoped>
@import '@/assets/styles/form-styles.css';

.form-group textarea {
  width: 90%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--white);
  transition: var(--transition);
  resize: none; /* Changed from vertical to none */
}

.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-group span {
  color: var(--text-light);
  font-size: 0.875rem;
}
</style>