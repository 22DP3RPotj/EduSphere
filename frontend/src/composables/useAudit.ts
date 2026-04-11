import { computed, ref, type Ref } from "vue"
import { useQuery } from "@vue/apollo-composable"
import type { DocumentNode } from "graphql"
import {
  USER_AUDITS_QUERY,
  USER_BAN_AUDITS_QUERY,
  ROOM_AUDITS_QUERY,
  INVITE_AUDITS_QUERY,
  REPORT_AUDITS_QUERY,
  MODERATION_CASE_AUDITS_QUERY,
  MODERATION_ACTION_AUDITS_QUERY,
} from "@/api/graphql"
import type { AuditEntry } from "@/types"

interface AuditFilters {
  dateFrom?: string;
  dateTo?: string;
  actorUsername?: string;
  name?: string;
}

const PAGE_SIZE = 20

function useAuditQuery(
  query: DocumentNode,
  dataKey: string,
  filters: Ref<AuditFilters>,
  enabled: Ref<boolean> = ref(true)
) {
  const after = ref<string | null>(null)

  const { result, loading, error, refetch, fetchMore } = useQuery(
    query,
    () => ({
      first: PAGE_SIZE,
      after: after.value,
      dateFrom: filters.value.dateFrom || undefined,
      dateTo: filters.value.dateTo || undefined,
      actorUsername: filters.value.actorUsername || undefined,
      name: filters.value.name || undefined,
    }),
    () => ({
      enabled: enabled.value,
      fetchPolicy: "cache-and-network",
    })
  )

  const entries = computed<AuditEntry[]>(() => {
    const connection = result.value?.[dataKey]
    if (!connection?.edges) return []
    return connection.edges.map((edge: { node: AuditEntry }) => edge.node)
  })

  const pageInfo = computed(() => result.value?.[dataKey]?.pageInfo || { hasNextPage: false, endCursor: null })

  async function loadMore() {
    if (!pageInfo.value.hasNextPage) return

    await fetchMore({
      variables: { after: pageInfo.value.endCursor },
      updateQuery: (prev: Record<string, unknown>, { fetchMoreResult }: { fetchMoreResult: Record<string, unknown> }) => {
        if (!fetchMoreResult) return prev

        const prevConnection = prev[dataKey]
        const newConnection = fetchMoreResult[dataKey]

        return {
          [dataKey]: {
            ...newConnection,
            edges: [...prevConnection.edges, ...newConnection.edges],
          },
        }
      },
    })
  }

  return {
    entries,
    loading,
    error,
    hasNextPage: computed(() => pageInfo.value.hasNextPage),
    loadMore,
    refetch,
  }
}

export function useUserAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(USER_AUDITS_QUERY, "userAudits", filters, enabled)
}

export function useUserBanAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(USER_BAN_AUDITS_QUERY, "userBanAudits", filters, enabled)
}

export function useRoomAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(ROOM_AUDITS_QUERY, "roomAudits", filters, enabled)
}

export function useInviteAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(INVITE_AUDITS_QUERY, "inviteAudits", filters, enabled)
}

export function useReportAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(REPORT_AUDITS_QUERY, "reportAudits", filters, enabled)
}

export function useModerationCaseAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(MODERATION_CASE_AUDITS_QUERY, "moderationCaseAudits", filters, enabled)
}

export function useModerationActionAudits(filters: Ref<AuditFilters>, enabled?: Ref<boolean>) {
  return useAuditQuery(MODERATION_ACTION_AUDITS_QUERY, "moderationActionAudits", filters, enabled)
}
