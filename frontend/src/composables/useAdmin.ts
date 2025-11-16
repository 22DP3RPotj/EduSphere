import { computed } from 'vue';
import { useQuery, useMutation } from '@vue/apollo-composable';
import type { Ref } from 'vue';
import { GET_ALL_USERS, GET_ALL_REPORTS, GET_REPORT_COUNT } from '@/api/graphql/admin.queries';
import {
  UPDATE_USER_STAFF_STATUS,
  UPDATE_USER_ACTIVE_STATUS,
  UPDATE_REPORT,
  DELETE_REPORT,
} from '@/api/graphql/admin.mutations';
import type { User, Report } from '@/types';

export function useAdminUsers(searchQuery: Ref<string>) {
  const { result, loading, error, refetch } = useQuery(
    GET_ALL_USERS,
    () => ({
      search: searchQuery.value || undefined,
    }),
    {
      fetchPolicy: 'cache-and-network',
    }
  );

  const users = computed<User[]>(() => result.value?.users || []);

  return {
    users,
    loading,
    error,
    refetch,
  };
}

export function useAdminReports(statusFilter: Ref<string>, reasonFilter: Ref<string>) {
  const { result, loading, error, refetch } = useQuery(
    GET_ALL_REPORTS,
    () => ({
      status: statusFilter.value || undefined,
      reason: reasonFilter.value || undefined,
    }),
    {
      fetchPolicy: 'cache-and-network',
    }
  );

  const reports = computed<Report[]>(() => result.value?.allReports || []);

  return {
    reports,
    loading,
    error,
    refetch,
  };
}

export function useReportCount(statusFilter: Ref<string>, reasonFilter: Ref<string>) {
  const { result, loading } = useQuery(
    GET_REPORT_COUNT,
    () => ({
      status: statusFilter.value || undefined,
      reason: reasonFilter.value || undefined,
    }),
    {
      fetchPolicy: 'cache-and-network',
    }
  );

  const count = computed<number>(() => result.value?.reportCount || 0);

  return {
    count,
    loading,
  };
}

export function useUpdateUserStaffStatus() {
  const { mutate, loading, error } = useMutation(UPDATE_USER_STAFF_STATUS);

  const updateStaffStatus = async (userIds: string[], isStaff: boolean) => {
    return await mutate({
      userIds,
      isStaff,
    });
  };

  return {
    updateStaffStatus,
    loading,
    error,
  };
}

export function useUpdateUserActiveStatus() {
  const { mutate, loading, error } = useMutation(UPDATE_USER_ACTIVE_STATUS);

  const updateActiveStatus = async (userIds: string[], isActive: boolean) => {
    return await mutate({
      userIds,
      isActive,
    });
  };

  return {
    updateActiveStatus,
    loading,
    error,
  };
}

// <CHANGE> Fixed mutation name from UPDATE_REPORT_STATUS to UPDATE_REPORT
export function useUpdateReport() {
  const { mutate, loading, error } = useMutation(UPDATE_REPORT);

  const updateReport = async (reportId: string, status?: string, moderatorNote?: string) => {
    return await mutate({
      reportId,
      status,
      moderatorNote,
    });
  };

  return {
    updateReport,
    loading,
    error,
  };
}

export function useDeleteReport() {
  const { mutate, loading, error } = useMutation(DELETE_REPORT);

  const deleteReport = async (reportId: string) => {
    return await mutate({
      reportId,
    });
  };

  return {
    deleteReport,
    loading,
    error,
  };
}
