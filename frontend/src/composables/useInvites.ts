import { computed } from "vue"
import { useMutation, useQuery } from "@vue/apollo-composable"
import {
  RECEIVED_INVITES_QUERY,
  SENT_INVITES_QUERY,
  SEND_INVITE_MUTATION,
  ACCEPT_INVITE_MUTATION,
  DECLINE_INVITE_MUTATION,
  CANCEL_INVITE_MUTATION,
  RESEND_INVITE_MUTATION,
} from "@/api/graphql"
import type { Invite, UUID } from "@/types"
import type { SendInviteInput } from "@/types"

export function useReceivedInvites() {
  const { result, loading, error, refetch } = useQuery(RECEIVED_INVITES_QUERY, null, {
    fetchPolicy: "cache-and-network",
  })

  return {
    invites: computed<Invite[]>(() => result.value?.receivedInvites || []),
    loading,
    error,
    refetch,
  }
}

export function useSentInvites() {
  const { result, loading, error, refetch } = useQuery(SENT_INVITES_QUERY, null, {
    fetchPolicy: "cache-and-network",
  })

  return {
    invites: computed<Invite[]>(() => result.value?.sentInvites || []),
    loading,
    error,
    refetch,
  }
}

export function useSendInvite() {
  const { mutate, loading, error } = useMutation(SEND_INVITE_MUTATION)

  async function sendInvite(data: SendInviteInput) {
    const result = await mutate(data)

    if (result?.data?.sendInvite?.invite) {
      return { success: true, invite: result.data.sendInvite.invite }
    }

    return { success: false, error: "Failed to send invite" }
  }

  return { sendInvite, loading, error }
}

export function useAcceptInvite() {
  const { mutate, loading, error } = useMutation(ACCEPT_INVITE_MUTATION)

  async function acceptInvite(token: UUID) {
    const result = await mutate({ token })

    if (result?.data?.acceptInvite?.participant) {
      return { success: true, participant: result.data.acceptInvite.participant }
    }

    return { success: false, error: "Failed to accept invite" }
  }

  return { acceptInvite, loading, error }
}

export function useDeclineInvite() {
  const { mutate, loading, error } = useMutation(DECLINE_INVITE_MUTATION)

  async function declineInvite(token: UUID) {
    const result = await mutate({ token })

    if (result?.data?.declineInvite?.invite) {
      return { success: true }
    }

    return { success: false, error: "Failed to decline invite" }
  }

  return { declineInvite, loading, error }
}

export function useCancelInvite() {
  const { mutate, loading, error } = useMutation(CANCEL_INVITE_MUTATION)

  async function cancelInvite(token: UUID) {
    const result = await mutate({ token })

    if (result?.data?.cancelInvite?.invite) {
      return { success: true }
    }

    return { success: false, error: "Failed to cancel invite" }
  }

  return { cancelInvite, loading, error }
}

export function useResendInvite() {
  const { mutate, loading, error } = useMutation(RESEND_INVITE_MUTATION)

  async function resendInvite(token: UUID, expiresAt?: string) {
    const result = await mutate({ token, expiresAt })

    if (result?.data?.resendInvite?.invite) {
      return { success: true, invite: result.data.resendInvite.invite }
    }

    return { success: false, error: "Failed to resend invite" }
  }

  return { resendInvite, loading, error }
}
