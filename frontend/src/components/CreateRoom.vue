<template>
  <div>
    <h2>Create Room</h2>
    <input v-model="name" placeholder="Room Name">
    <input v-model="topic_name" placeholder="Topic Name">
    <input v-model="description" placeholder="Description">
    <button @click="submitRoom">Create</button>
    <pre>{{ response }}</pre>
  </div>
</template>

<script>
import { createRoom } from "@/api/room.api";

export default {
  data() {
    return { name: "", topic_name: "", description: "", response: null };
  },
  methods: {
    async submitRoom() {
      const payload = {
        name: this.name || null,
        topic_name: this.topic_name || null,
        description: this.description || null
      };
      
      this.response = await createRoom(payload.name, payload.topic_name, payload.description);
    }
  }
};
</script>