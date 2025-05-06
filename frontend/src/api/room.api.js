import { gql } from "@apollo/client/core";
import { apolloClient } from "./apollo.client";
import { useNotifications } from "@/composables/useNotifications";
import { useRouter } from "vue-router";
import { useApiWrapper } from "@/composables/api.wrapper";

export function useRoomApi() {
  const notifications = useNotifications();
  const router = useRouter();
  const apiWrapper = useApiWrapper();

  const ROOM_MESSAGES_QUERY = gql`
  query RoomMessages($hostSlug: String!, $roomSlug: String!) {
    messages(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      id
      user {
        id
        username
        avatar
      }
      body
      created
    }
  }
`;

  async function fetchRoomMessages(hostSlug, roomSlug) {
    try {
      const result = await apiWrapper.callApi(
        async () => apolloClient.query({
          query: ROOM_MESSAGES_QUERY,
          variables: { hostSlug, roomSlug }
        })
      );

      return result.data.messages;
    } catch (error) {
      console.error("Error fetching room messages:", error);
      return [];
    }
  }

  const CREATE_ROOM_MUTATION = gql`
    mutation CreateRoom($name: String!, $topicName: String!, $description: String) {
      createRoom(name: $name, topicName: $topicName, description: $description) {
        room {
          name
          description
          topic { name }
          host {
            id
            username 
          }
        }
      }
    }
  `;

  const DELETE_ROOM_MUTATION = gql`
    mutation DeleteRoom($hostSlug: String!, $roomSlug: String!) {
      deleteRoom(hostSlug: $hostSlug, roomSlug: $roomSlug) {
        success
      }
    }
  `;

  const JOIN_ROOM_MUTATION = gql`
    mutation JoinRoom($hostSlug: String!, $roomSlug: String!) {
      joinRoom(hostSlug: $hostSlug, roomSlug: $roomSlug) {
        room {
          participants {
            id
            username
          }
        }
      }
    }
  `;

  const DELETE_MESSAGE_MUTATION = gql`
    mutation DeleteMessage($messageId: UUID!) {
      deleteMessage(messageId: $messageId) {
        success
      }
    }
  `;

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
      router.push(`/${room.host.username}/${room.name.toLowerCase().replace(/\s+/g, '-')}`);
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

  return {
    createRoom,
    deleteRoom,
    joinRoom,
    deleteMessage,
    fetchRoomMessages,
  };
}