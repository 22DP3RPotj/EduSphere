import { computed, type Ref } from "vue"
import { useMutation, useQuery } from "@vue/apollo-composable"
import {
  CREATE_REPORT_MUTATION,
  REPORT_REASONS_QUERY,
  SUBMITTED_REPORTS_QUERY,
} from "@/api/graphql"
import type { CreateReportInput } from "@/types"

export function useReportReasons(targetType?: Ref<string | undefined>) {
  const { result, loading, error } = useQuery(
    REPORT_REASONS_QUERY,
    () => ({ targetType: targetType?.value }),
    { fetchPolicy: "cache-and-network" }
  )

  return {
    reasons: computed(() => result.value?.reportReasons || []),
    loading,
    error,
  }
}

export function useSubmittedReports() {
  const { result, loading, error, refetch } = useQuery(SUBMITTED_REPORTS_QUERY, null, {
    fetchPolicy: "cache-and-network",
  })

  return {
    reports: computed(() => result.value?.submittedReports || []),
    loading,
    error,
    refetch,
  }
}

export function useCreateReport() {
  const { mutate, loading, error } = useMutation(CREATE_REPORT_MUTATION)

  async function createReport(data: CreateReportInput) {
    try {
      const result = await mutate(data)

      if (result?.data?.createReport?.report) {
        return { success: true, report: result.data.createReport.report }
      }

      return { success: false, error: "Failed to create report" }
    } catch (e: unknown) {
      const gqlError = (e as { graphQLErrors?: { message: string }[] })?.graphQLErrors?.[0]
      return { success: false, error: gqlError?.message || "Failed to create report" }
    }
  }

  return { createReport, loading, error }
}
