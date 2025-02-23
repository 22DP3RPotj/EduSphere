<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import { deleteRoom, joinRoom } from '@/api/room.api';
import { apolloClient } from '@/api/apollo.client';
import { gql } from '@apollo/client/core';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const room = ref(null);
const loading = ref(false);

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

const isHost = computed(() => {
  return room.value?.host?.id === authStore.user?.id;
});

async function fetchRoom() {
  try {
    loading.value = true;
    const { data } = await apolloClient.query({
      query: ROOM_QUERY,
      variables: route.params
    });
    room.value = data.room;
  } finally {
    loading.value = false;
  }
}

async function handleDelete() {
  await deleteRoom(room.value.host.slug, room.value.slug);
  router.push('/');
}

async function handleJoin() {
  await joinRoom(room.value.host.slug, room.value.slug);
  await fetchRoom();
}

onMounted(async () => {
  await authStore.initialize();
  await fetchRoom();
});
</script>

<template>
  <div v-if="loading || authStore.isLoadingUser">
    Loading room...
  </div>
  <div v-else-if="room">
    <h2>{{ room.name }}</h2>
    <p>Hosted by: {{ room.host.username }}</p>
    <button @click="handleDelete" v-if="isHost">Delete Room</button>
    <button @click="handleJoin">Join Room</button>
  </div>
</template>