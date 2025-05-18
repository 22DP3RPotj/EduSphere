import { apolloClient } from "./apollo.client";
import { useRouter } from "vue-router";
import { useApiWrapper } from "@/composables/api.wrapper";

import {
  ROOM_QUERY,
  ROOM_MESSAGES_QUERY,
  TOPIC_QUERY
} from "./graphql/room.queries";

import {
  CREATE_ROOM_MUTATION,
  DELETE_ROOM_MUTATION,
  JOIN_ROOM_MUTATION,
  DELETE_MESSAGE_MUTATION,
  UPDATE_MESSAGE_MUTATION,
  UPDATE_ROOM_MUTATION
} from "./graphql/room.mutations";

export function useRoomApi() {
  const router = useRouter();
  const apiWrapper = useApiWrapper();

  async function fetchRoom(hostSlug, roomSlug) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.query({
          query: ROOM_QUERY,
          variables: { hostSlug, roomSlug },
          fetchPolicy: 'network-only'
        })
      );

      return response.data.room;
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  async function fetchRoomMessages(hostSlug, roomSlug) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.query({
          query: ROOM_MESSAGES_QUERY,
          variables: { hostSlug, roomSlug },
          fetchPolicy: 'network-only'
        })
      );

      return response.data.messages;
    } catch (error) {
      console.error("Error fetching room messages:", error);
      return [];
    }
  }

  async function createRoom(name, topic_name, description) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: CREATE_ROOM_MUTATION,
          variables: {
            name: name,
            topicName: topic_name,
            description: description
          },
        })
      );

      const room = response.data.createRoom.room;
      router.push(`/user/${room.host.username}/${room.slug}`);
      return room;
    } catch (error) {
      console.error("Error creating room:", error);
      return null;
    }
  }

  async function deleteRoom(hostSlug, roomSlug) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: DELETE_ROOM_MUTATION,
          variables: { hostSlug, roomSlug }
        })
      );

      router.push('/');
      return response.data.deleteRoom.success;
    } catch (error) {
      console.error("Error deleting room:", error);
      return false;
    }
  }

  async function updateRoom(data) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: UPDATE_ROOM_MUTATION,
          variables: data
        })
      );

      return response.data.updateRoom.room;
    } catch (error) {
      console.error("Error updating room:", error);
      return false;
    }
  }

  async function joinRoom(hostSlug, roomSlug) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: JOIN_ROOM_MUTATION,
          variables: { hostSlug, roomSlug }
        })
      );

      return response.data.joinRoom.room;
    } catch (error) {
      console.error("Error joining room:", error);
      return null;
    }
  }

  async function deleteMessage(messageId) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: DELETE_MESSAGE_MUTATION,
          variables: { messageId }
        })
      );

      return response.data.deleteMessage.success;
    } catch (error) {
      console.error("Error deleting message:", error);
      return false;
    }
  }

  async function updateMessage(messageId, body) {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.mutate({
          mutation: UPDATE_MESSAGE_MUTATION,
          variables: { messageId, body }
        })
      );

      return response.data.updateMessage.message;
    } catch (error) {
      console.error("Error updating message:", error);
      return false;
    }
  }

  async function fetchTopics() {
    try {
      const response = await apiWrapper.callApi(
        async () => apolloClient.query({
          query: TOPIC_QUERY,
        })
      );

      return response.data.topics;
    } catch (error) {
      console.error("Error fetching topics:", error);
      return [];
    }
  }

  return {
    fetchRoom,
    createRoom,
    deleteRoom,
    updateRoom,
    joinRoom,
    deleteMessage,
    updateMessage,
    fetchRoomMessages,
    fetchTopics,
  };
}