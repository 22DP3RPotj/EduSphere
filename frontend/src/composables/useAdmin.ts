import { computed } from 'vue';
import { useQuery, useMutation } from '@vue/apollo-composable';
import type { Ref } from 'vue';
import { GET_ALL_USERS, GET_REPORTS, GET_REPORT_COUNT, GET_CASES, GET_CASE } from '@/api/graphql/admin.queries';
import {
  TAKE_CASE_ACTION,
  SET_CASE_UNDER_REVIEW,
  SET_CASE_PRIORITY,
  REOPEN_CASE,
  BAN_USER,
  UNBAN_USER,
  BAN_USERS,
  UNBAN_USERS,
  PROMOTE_USERS,
  DEMOTE_USERS,
  PROMOTE_USER,
  DEMOTE_USER,
} from '@/api/graphql/admin.mutations';
import type { User, ModerationCase, Report, UUID } from '@/types';

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

export function useAdminReports(filters: Ref<{
  reason?: string;
  targetType?: string;
  hasCase?: boolean;
}>) {
  const { result, loading, error, refetch } = useQuery(
    GET_REPORTS,
    () => ({
      reason: filters.value.reason || undefined,
      targetType: filters.value.targetType || undefined,
      hasCase: filters.value.hasCase,
    }),
    {
      fetchPolicy: 'cache-and-network',
    }
  );

  const reports = computed<Report[]>(() => result.value?.reports || []);

  return {
    reports,
    loading,
    error,
    refetch,
  };
}

export function useReportCount(filters: Ref<{
  reason?: string;
  targetType?: string;
  hasCase?: boolean;
}>) {
  const { result, loading } = useQuery(
    GET_REPORT_COUNT,
    () => ({
      reason: filters.value.reason || undefined,
      targetType: filters.value.targetType || undefined,
      hasCase: filters.value.hasCase,
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

export function useAdminCases(filters: Ref<{
  status?: string;
  priority?: number;
  targetType?: string;
}>) {
  const { result, loading, error, refetch } = useQuery(
    GET_CASES,
    () => ({
      status: filters.value.status || undefined,
      priority: filters.value.priority,
      targetType: filters.value.targetType || undefined,
    }),
    {
      fetchPolicy: 'cache-and-network',
    }
  );

  const cases = computed<ModerationCase[]>(() => result.value?.cases || []);

  return {
    cases,
    loading,
    error,
    refetch,
  };
}

export function useAdminCase(caseId: Ref<UUID | null>) {
  const { result, loading, error, refetch } = useQuery(
    GET_CASE,
    () => ({ caseId: caseId.value }),
    () => ({
      enabled: !!caseId.value,
      fetchPolicy: 'network-only',
    })
  );

  return {
    moderationCase: computed<ModerationCase | null>(() => result.value?.case || null),
    loading,
    error,
    refetch,
  };
}

export function useTakeCaseAction() {
  const { mutate, loading, error } = useMutation(TAKE_CASE_ACTION);

  const takeCaseAction = async (caseId: UUID, action: string, note?: string) => {
    const result = await mutate({ caseId, action, note });

    if (result?.data?.takeCaseAction?.case) {
      return { success: true, case: result.data.takeCaseAction.case };
    }

    return { success: false, error: 'Failed to take action' };
  };

  return { takeCaseAction, loading, error };
}

export function useSetCaseUnderReview() {
  const { mutate, loading, error } = useMutation(SET_CASE_UNDER_REVIEW);

  const setCaseUnderReview = async (caseId: UUID) => {
    const result = await mutate({ caseId });

    if (result?.data?.setCaseUnderReview?.case) {
      return { success: true };
    }

    return { success: false, error: 'Failed to set case under review' };
  };

  return { setCaseUnderReview, loading, error };
}

export function useSetCasePriority() {
  const { mutate, loading, error } = useMutation(SET_CASE_PRIORITY);

  const setCasePriority = async (caseId: UUID, priority: string) => {
    const result = await mutate({ caseId, priority });

    if (result?.data?.setCasePriority?.case) {
      return { success: true };
    }

    return { success: false, error: 'Failed to set priority' };
  };

  return { setCasePriority, loading, error };
}

export function useReopenCase() {
  const { mutate, loading, error } = useMutation(REOPEN_CASE);

  const reopenCase = async (caseId: UUID) => {
    const result = await mutate({ caseId });

    if (result?.data?.reopenCase?.case) {
      return { success: true };
    }

    return { success: false, error: 'Failed to reopen case' };
  };

  return { reopenCase, loading, error };
}

export function useBanUser() {
  const { mutate, loading, error } = useMutation(BAN_USER);

  const banUser = async (userId: UUID, reason?: string, expiresAt?: string) => {
    const result = await mutate({ userId, reason, expiresAt });

    if (result?.data?.banUser?.success) {
      return { success: true };
    }

    return { success: false, error: 'Failed to ban user' };
  };

  return { banUser, loading, error };
}

export function useUnbanUser() {
  const { mutate, loading, error } = useMutation(UNBAN_USER);

  const unbanUser = async (userId: UUID) => {
    const result = await mutate({ userId });

    if (result?.data?.unbanUser?.success) {
      return { success: true };
    }

    return { success: false, error: 'Failed to unban user' };
  };

  return { unbanUser, loading, error };
}

export function useBanUsers() {
  const { mutate, loading, error } = useMutation(BAN_USERS);

  const banUsers = async (userIds: UUID[], reason?: string, expiresAt?: string) => {
    const result = await mutate({ userIds, reason, expiresAt });
    if (result?.data?.banUsers?.success) {
      return { success: true, bannedCount: result.data.banUsers.bannedCount as number };
    }
    return { success: false, error: 'Failed to ban users' };
  };

  return { banUsers, loading, error };
}

export function useUnbanUsers() {
  const { mutate, loading, error } = useMutation(UNBAN_USERS);

  const unbanUsers = async (userIds: UUID[]) => {
    const result = await mutate({ userIds });
    if (result?.data?.unbanUsers?.success) {
      return { success: true, unbannedCount: result.data.unbanUsers.unbannedCount as number };
    }
    return { success: false, error: 'Failed to unban users' };
  };

  return { unbanUsers, loading, error };
}

export function usePromoteUsers() {
  const { mutate, loading, error } = useMutation(PROMOTE_USERS);

  const promoteUsers = async (userIds: UUID[]) => {
    const result = await mutate({ userIds });

    if (result?.data?.promoteUsers?.success) {
      return { success: true, updatedCount: result.data.promoteUsers.updatedCount };
    }

    return { success: false, error: 'Failed to promote users' };
  };

  return { promoteUsers, loading, error };
}

export function useDemoteUsers() {
  const { mutate, loading, error } = useMutation(DEMOTE_USERS);

  const demoteUsers = async (userIds: UUID[]) => {
    const result = await mutate({ userIds });

    if (result?.data?.demoteUsers?.success) {
      return { success: true, updatedCount: result.data.demoteUsers.updatedCount };
    }

    return { success: false, error: 'Failed to demote users' };
  };

  return { demoteUsers, loading, error };
}

export function usePromoteUser() {
  const { mutate, loading, error } = useMutation(PROMOTE_USER);

  const promoteUser = async (userId: UUID) => {
    const result = await mutate({ userId });
    if (result?.data?.promoteUser?.success) {
      return { success: true };
    }
    return { success: false, error: 'Failed to promote user' };
  };

  return { promoteUser, loading, error };
}

export function useDemoteUser() {
  const { mutate, loading, error } = useMutation(DEMOTE_USER);

  const demoteUser = async (userId: UUID) => {
    const result = await mutate({ userId });
    if (result?.data?.demoteUser?.success) {
      return { success: true };
    }
    return { success: false, error: 'Failed to demote user' };
  };

  return { demoteUser, loading, error };
}
