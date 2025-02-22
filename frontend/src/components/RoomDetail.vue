<template>
  <div v-if="room">
    <h2>{{ room.name }}</h2>
    <p>Hosted by: {{ room.host.username }}</p>
    <button @click="deleteRoom" v-if="isHost">Delete Room</button>
    <button @click="joinRoom">Join Room</button>
  </div>
  <div v-else>
    Loading room...
  </div>
</template>

<script>
import { deleteRoom, joinRoom } from "@/api/user";
import { gql } from "@apollo/client/core";
import { apolloClient } from "@/api/apollo";
import { useAuthStore } from "@/stores/auth";

const ROOM_QUERY = gql`
  query GetRoom($hostSlug: String!, $roomSlug: String!) {
    room(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      id
      name
      slug
      description
      host {
        id
        username
        slug
      }
      participants {
        id
        username
      }
    }
  }
`;

export default {
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
  data() {
    return {
      room: null
    };
  },
  computed: {
    isHost() {
      return this.room?.host.id === this.authStore.user?.id;
    }
  },
  async mounted() {
    await this.fetchRoom();
  },
  methods: {
    async fetchRoom() {
      const { hostSlug, roomSlug } = this.$route.params;
      try {
        const { data } = await apolloClient.query({
          query: ROOM_QUERY,
          variables: { hostSlug, roomSlug }
        });
        this.room = data.room;
      } catch (error) {
        console.error("Failed to fetch room:", error);
      }
    },
    async deleteRoom() {
      await deleteRoom(this.room.host.slug, this.room.slug);
      this.$router.push('/');
    },
    async joinRoom() {
      await joinRoom(this.room.host.slug, this.room.slug);
      await this.fetchRoom();
    }
  }
};
</script>