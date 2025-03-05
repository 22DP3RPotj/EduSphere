<template>
  <div>
    <h2>Create Room</h2>
    <input v-model="name" placeholder="Room Name">
    <input v-model="topic_name" placeholder="Topic Name">
    <input v-model="description" placeholder="Description">
    <button @click="submitRoom" :disabled="isLoading">
      {{ isLoading ? 'Creating...' : 'Create' }}
    </button>
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