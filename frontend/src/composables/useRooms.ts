import { computed, type Ref } from "vue"
import { useMutation, useQuery } from "@vue/apollo-composable"
import {
  CREATE_ROOM_MUTATION,
  DELETE_ROOM_MUTATION,
  JOIN_ROOM_MUTATION,
  UPDATE_ROOM_MUTATION,
  ROOM_QUERY,
  ROOM_MESSAGES_QUERY,
  TOPIC_QUERY,
} from "@/api/graphql"

import type { CreateRoomInput, UpdateRoomInput } from "@/types"

export function useRoomQuery(hostSlug: string, roomSlug: string) {
  const { result, loading, error, refetch } = useQuery(
    ROOM_QUERY,
    { hostSlug, roomSlug },
    {
      fetchPolicy: "network-only",
    },
  )

  return {
    room: computed(() => result.value?.room || null),
    loading,
    error,
    refetch,
  }
}

export function useRoomMessagesQuery(hostSlug: string, roomSlug: string, options?: { enabled?: Ref<boolean> }) {
  const { result, loading, error, refetch } = useQuery(
    ROOM_MESSAGES_QUERY,
    { hostSlug, roomSlug },
    {
      enabled: options?.enabled?.value ?? true,
      fetchPolicy: "network-only",
    },
  )

  return {
    messages: computed(() => result.value?.messages || []),
    loading,
    error,
    refetch,
  }
}

export function useTopicsQuery() {
  const { result, loading, error } = useQuery(TOPIC_QUERY)

  return {
    topics: computed(() => result.value?.topics || []),
    loading,
    error,
  }
}

export function useCreateRoom() {
  const { mutate, loading, error, onDone, onError } = useMutation(CREATE_ROOM_MUTATION)

  async function createRoom(data: CreateRoomInput) {
    const result = await mutate(data)

    if (result?.data?.createRoom?.room) {
      return { success: true, room: result.data.createRoom.room }
    }

    return { success: false, error: "Failed to create room" }
  }

  return {
    createRoom,
    loading,
    error,
    onDone,
    onError,
  }
}

export function useUpdateRoom() {
  const { mutate, loading, error } = useMutation(UPDATE_ROOM_MUTATION)

  async function updateRoom(data: UpdateRoomInput) {
    const result = await mutate(data)

    if (result?.data?.updateRoom?.room) {
      return { success: true, room: result.data.updateRoom.room }
    }

    return { success: false, error: "Failed to update room" }
  }

  return {
    updateRoom,
    loading,
    error,
  }
}

export function useDeleteRoom() {
  const { mutate, loading, error } = useMutation(DELETE_ROOM_MUTATION)

  async function deleteRoom(roomId: string) {
    const result = await mutate({ roomId })

    if (result?.data?.deleteRoom?.success) {
      return { success: true }
    }

    return { success: false, error: "Failed to delete room" }
  }

  return {
    deleteRoom,
    loading,
    error,
  }
}

export function useJoinRoom(hostSlug?: string, roomSlug?: string) {
  const { mutate, loading, error } = useMutation(
    JOIN_ROOM_MUTATION,
    () => ({
      refetchQueries: hostSlug && roomSlug 
        ? [
            {
              query: ROOM_QUERY,
              variables: { hostSlug, roomSlug }
            }
          ]
        : [],
    })
  )

  async function joinRoom(roomId: string) {
    const result = await mutate({ roomId })

    if (result?.data?.joinRoom?.room) {
      return { success: true, room: result.data.joinRoom.room }
    }

    return { success: false, error: "Failed to join room" }
  }

  return {
    joinRoom,
    loading,
    error,
  }
}
