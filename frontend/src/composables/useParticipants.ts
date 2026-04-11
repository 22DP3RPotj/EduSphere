import { useMutation } from "@vue/apollo-composable"
import type { Ref } from "vue"
import {
  LEAVE_ROOM_MUTATION,
  CHANGE_PARTICIPANT_ROLE_MUTATION,
  REMOVE_PARTICIPANT_MUTATION,
  ROOM_QUERY,
} from "@/api/graphql"
import type { UUID } from "@/types"

export function useLeaveRoom(roomId?: Ref<UUID>) {
  const { mutate, loading, error } = useMutation(
    LEAVE_ROOM_MUTATION,
    () => ({
      refetchQueries: roomId?.value
        ? [{ query: ROOM_QUERY, variables: { roomId: roomId.value } }]
        : [],
    })
  )

  async function leaveRoom(id: UUID) {
    const result = await mutate({ roomId: id })

    if (result?.data?.leaveRoom?.success) {
      return { success: true }
    }

    return { success: false, error: "Failed to leave room" }
  }

  return { leaveRoom, loading, error }
}

export function useChangeParticipantRole() {
  const { mutate, loading, error } = useMutation(CHANGE_PARTICIPANT_ROLE_MUTATION)

  async function changeParticipantRole(participantId: UUID, roleId: UUID) {
    const result = await mutate({ participantId, roleId })

    if (result?.data?.changeParticipantRole?.participant) {
      return { success: true, participant: result.data.changeParticipantRole.participant }
    }

    return { success: false, error: "Failed to change participant role" }
  }

  return { changeParticipantRole, loading, error }
}

export function useRemoveParticipant() {
  const { mutate, loading, error } = useMutation(REMOVE_PARTICIPANT_MUTATION)

  async function removeParticipant(participantId: UUID) {
    const result = await mutate({ participantId })

    if (result?.data?.removeParticipant?.success) {
      return { success: true }
    }

    return { success: false, error: "Failed to remove participant" }
  }

  return { removeParticipant, loading, error }
}
