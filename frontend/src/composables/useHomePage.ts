import { computed, type Ref } from "vue"
import { useQuery } from "@vue/apollo-composable"
import {
  HOMEPAGE_INITIAL_QUERY,
  USER_WITH_ROOMS_QUERY
} from "@/api/graphql"

export function useHomepageInitialQuery(search: Ref<string | null>, topics: Ref<string[] | null>) {
  const variables = computed(() => ({
    search: search.value || null,
    topics: topics.value && topics.value.length > 0 ? topics.value : null
  }))

  const { result, loading, error, refetch } = useQuery(
    HOMEPAGE_INITIAL_QUERY,
    variables,
    {
      fetchPolicy: "network-only",
      errorPolicy: "all"
    }
  )

  const rooms = computed(() => result.value?.rooms || [])
  const allTopics = computed(() => result.value?.topics || [])

  return {
    rooms,
    topics: allTopics,
    loading,
    error,
    refetch
  }
}

export function useUserRoomsQuery(userSlug: Ref<string>) {
  const variables = computed(() => ({
    userSlug: userSlug.value
  }))

  const { result, loading, error, refetch } = useQuery(
    USER_WITH_ROOMS_QUERY,
    variables,
    {
      fetchPolicy: "network-only",
      enabled: computed(() => !!userSlug.value),
      errorPolicy: "all"
    }
  )

  const userRooms = computed(() => result.value?.roomsParticipatedByUser || [])
  const recommendedRooms = computed(() => result.value?.roomsNotParticipatedByUser || [])

  return {
    userRooms,
    recommendedRooms,
    loading,
    error,
    refetch
  }
}
