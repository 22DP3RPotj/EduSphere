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
      this.response = await createRoom(this.name, this.topic_name, this.description);
    }
  }
};
</script>