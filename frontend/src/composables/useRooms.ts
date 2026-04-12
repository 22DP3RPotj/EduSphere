import { computed, type Ref } from "vue"
import type { Message, GqlMessage, UUID, DateTime } from "@/types"
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

export function useRoomQuery(roomId: Ref<UUID | null>) {
  const { result, loading, error, refetch } = useQuery(
    ROOM_QUERY,
    { roomId: roomId.value },
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

export function useRoomMessagesQuery(roomId: Ref<UUID>, options?: { enabled?: Ref<boolean> }) {
  const { result, loading, error, refetch } = useQuery(
    ROOM_MESSAGES_QUERY,
    { roomId: roomId.value },
    {
      enabled: options?.enabled?.value ?? true,
      fetchPolicy: "network-only",
    },
  )

  const normalizeMessages = (items?: GqlMessage[]): Message[] => {
    if (!items) return []
    return items.map((m): Message => ({
      id: m.id as UUID,
      author: m.author,
      room: m.room,
      parent: null,
      body: m.body,
      isEdited: m.isEdited,
      createdAt: m.createdAt as DateTime,
      updatedAt: m.updatedAt as DateTime,
    }))
  }

  return {
    messages: computed(() => normalizeMessages(result.value?.messages)),
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

  async function deleteRoom(roomId: UUID) {
    const result = await mutate({ roomId: roomId })

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

export function useJoinRoom(roomId?: Ref<UUID>) {
  const { mutate, loading, error } = useMutation(
    JOIN_ROOM_MUTATION,
    () => ({
      refetchQueries: roomId?.value
        ? [{ query: ROOM_QUERY, variables: { roomId: roomId.value } }]
        : [],
    })
  )

  async function joinRoom(roomId: UUID) {
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
