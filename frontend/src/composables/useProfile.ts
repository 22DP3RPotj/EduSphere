import { computed } from "vue"
import { useQuery } from "@vue/apollo-composable"
import {
  USER_QUERY,
  MESSAGES_BY_USER_QUERY,
  ROOMS_QUERY,
  ROOMS_PARTICIPATED_BY_USER_QUERY
} from "@/api/graphql"

export function useUserQuery(username: string) {
  const { result, loading, error, refetch } = useQuery(
    USER_QUERY,
    { username },
    { fetchPolicy: "network-only" }
  )

  return {
    user: computed(() => result.value?.user || null),
    loading,
    error,
    refetch,
  }
}

export function useUserMessagesQuery(username: string) {
  const { result, loading, error, refetch } = useQuery(
    MESSAGES_BY_USER_QUERY,
    { userSlug: username },
    { fetchPolicy: "network-only" }
  )

  return {
    messages: computed(() => result.value?.messagesByUser || []),
    loading,
    error,
    refetch,
  }
}

export function useUserHostedRoomsQuery(username: string) {
  const { result, loading, error, refetch } = useQuery(
    ROOMS_QUERY,
    { hostSlug: username },
    { fetchPolicy: "network-only" }
  )

  return {
    rooms: computed(() => result.value?.rooms || []),
    loading,
    error,
    refetch,
  }
}

export function useUserJoinedRoomsQuery(username: string) {
  const { result, loading, error, refetch } = useQuery(
    ROOMS_PARTICIPATED_BY_USER_QUERY,
    { userSlug: username },
    { fetchPolicy: "network-only" }
  )

  return {
    rooms: computed(() => result.value?.roomsParticipatedByUser || []),
    loading,
    error,
    refetch,
  }
}
