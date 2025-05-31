import { apolloClient } from "./apollo.client";
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

import type {
  Room,
  Message,
  Topic,
  CreateRoomInput,
  UpdateRoomInput,
  UpdateMessageInput,
  DeleteMessageInput,
} from "@/types";


interface FetchRoomResponse {
  data?: {
    room?: Room;
  } | null;
}

interface FetchRoomMessagesResponse {
  data?: {
    messages?: Message[];
  } | null;
}

interface CreateRoomResponse {
  data?: {
    createRoom?: {
      room: Room;
    };
  } | null;
}

interface DeleteRoomResponse {
  data?: {
    deleteRoom?: {
      success: boolean;
    };
  } | null;
}

interface UpdateRoomResponse {
  data?: {
    updateRoom?: {
      room: Room;
    };
  } | null;
}

interface JoinRoomResponse {
  data?: {
    joinRoom?: {
      room: Room;
    };
  } | null;
}

interface DeleteMessageResponse {
  data?: {
    deleteMessage?: {
      success: boolean;
    };
  } | null;
}

interface UpdateMessageResponse {
  data?: {
    updateMessage?: {
      message: Message;
    };
  } | null;
}

interface FetchTopicsResponse {
  data?: {
    topics?: Topic[];
  } | null;
}

export function useRoomApi() {
  const apiWrapper = useApiWrapper();

  async function fetchRoom(hostSlug: string, roomSlug: string): Promise<Room | null> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<FetchRoomResponse> => apolloClient.query({
          query: ROOM_QUERY,
          variables: { hostSlug, roomSlug },
          fetchPolicy: 'network-only'
        })
      );

      return response.data?.room || null;
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  async function fetchRoomMessages(hostSlug: string, roomSlug: string): Promise<Message[]> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<FetchRoomMessagesResponse> => apolloClient.query({
          query: ROOM_MESSAGES_QUERY,
          variables: { hostSlug, roomSlug },
          fetchPolicy: 'network-only'
        })
      );

      return response.data?.messages || [];
    } catch (error) {
      console.error("Error fetching room messages:", error);
      return [];
    }
  }

  async function createRoom(name: string, topicName: string, description?: string): Promise<Room | null> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<CreateRoomResponse> => apolloClient.mutate({
          mutation: CREATE_ROOM_MUTATION,
          variables: {
            name,
            topicName,
            description
          } satisfies CreateRoomInput,
        })
      );

      return response.data?.createRoom?.room || null;
    } catch (error) {
      console.error("Error creating room:", error);
      return null;
    }
  }

  async function deleteRoom(hostSlug: string, roomSlug: string): Promise<boolean> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<DeleteRoomResponse> => apolloClient.mutate({
          mutation: DELETE_ROOM_MUTATION,
          variables: { hostSlug, roomSlug }
        })
      );

      return response.data?.deleteRoom?.success || false;
    } catch (error) {
      console.error("Error deleting room:", error);
      return false;
    }
  }

  async function updateRoom(data: UpdateRoomInput): Promise<Room | false> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<UpdateRoomResponse> => apolloClient.mutate({
          mutation: UPDATE_ROOM_MUTATION,
          variables: data
        })
      );

      return response.data?.updateRoom?.room || false;
    } catch (error) {
      console.error("Error updating room:", error);
      return false;
    }
  }

  async function joinRoom(hostSlug: string, roomSlug: string): Promise<Room | null> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<JoinRoomResponse> => apolloClient.mutate({
          mutation: JOIN_ROOM_MUTATION,
          variables: { hostSlug, roomSlug }
        })
      );

      return response.data?.joinRoom?.room || null;
    } catch (error) {
      console.error("Error joining room:", error);
      return null;
    }
  }

  async function deleteMessage(messageId: string): Promise<boolean> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<DeleteMessageResponse> => apolloClient.mutate({
          mutation: DELETE_MESSAGE_MUTATION,
          variables: { messageId } satisfies DeleteMessageInput
        })
      );

      return response.data?.deleteMessage?.success || false;
    } catch (error) {
      console.error("Error deleting message:", error);
      return false;
    }
  }

  async function updateMessage(messageId: string, body: string): Promise<Message | false> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<UpdateMessageResponse> => apolloClient.mutate({
          mutation: UPDATE_MESSAGE_MUTATION,
          variables: { messageId, body } satisfies UpdateMessageInput
        })
      );

      return response.data?.updateMessage?.message || false;
    } catch (error) {
      console.error("Error updating message:", error);
      return false;
    }
  }

  async function fetchTopics(): Promise<Topic[]> {
    try {
      const response = await apiWrapper.callApi(
        async (): Promise<FetchTopicsResponse> => apolloClient.query({
          query: TOPIC_QUERY,
        })
      );

      return response.data?.topics || [];
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
