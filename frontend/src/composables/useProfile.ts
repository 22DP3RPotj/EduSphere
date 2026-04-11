import { computed, type Ref } from "vue"
import { useQuery } from "@vue/apollo-composable"
import {
  USER_QUERY,
  MESSAGES_BY_USER_QUERY,
  ROOMS_QUERY,
  ROOMS_PARTICIPATED_BY_USER_QUERY
} from "@/api/graphql"
import type { UUID } from "@/types"

export function useUserQuery(userId: Ref<UUID>) {
  const { result, loading, error, refetch } = useQuery(
    USER_QUERY,
    computed(() => ({ userId: userId.value })),
    { fetchPolicy: "network-only" }
  )

  return {
    user: computed(() => result.value?.user || null),
    loading,
    error,
    refetch,
  }
}

export function useUserMessagesQuery(userId: Ref<UUID>) {
  const { result, loading, error, refetch } = useQuery(
    MESSAGES_BY_USER_QUERY,
    computed(() => ({ userId: userId.value })),
    { fetchPolicy: "network-only" }
  )

  return {
    messages: computed(() => result.value?.messagesByUser || []),
    loading,
    error,
    refetch,
  }
}

export function useUserHostedRoomsQuery(userId: Ref<UUID>) {
  const { result, loading, error, refetch } = useQuery(
    ROOMS_QUERY,
    computed(() => ({ hostId: userId.value })),
    { fetchPolicy: "network-only" }
  )

  return {
    rooms: computed(() => result.value?.rooms || []),
    loading,
    error,
    refetch,
  }
}

export function useUserJoinedRoomsQuery(userId: Ref<UUID>) {
  const { result, loading, error, refetch } = useQuery(
    ROOMS_PARTICIPATED_BY_USER_QUERY,
    computed(() => ({ userId: userId.value })),
    { fetchPolicy: "network-only" }
  )

  return {
    rooms: computed(() => result.value?.roomsParticipatedByUser || []),
    loading,
    error,
    refetch,
  }
}
