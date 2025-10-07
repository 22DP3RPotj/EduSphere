import { useMutation } from "@vue/apollo-composable"
import { DELETE_MESSAGE_MUTATION, UPDATE_MESSAGE_MUTATION } from "@/api/graphql"

import type { UpdateMessageInput, DeleteMessageInput } from "@/types"

export function useDeleteMessage() {
  const { mutate, loading, error } = useMutation(DELETE_MESSAGE_MUTATION)

  async function deleteMessage(messageId: string) {
    const result = await mutate({ messageId } satisfies DeleteMessageInput)

    if (result?.data?.deleteMessage?.success) {
      return { success: true }
    }

    return { success: false, error: "Failed to delete message" }
  }

  return {
    deleteMessage,
    loading,
    error,
  }
}

export function useUpdateMessage() {
  const { mutate, loading, error } = useMutation(UPDATE_MESSAGE_MUTATION)

  async function updateMessage(messageId: string, body: string) {
    const result = await mutate({ messageId, body } satisfies UpdateMessageInput)

    if (result?.data?.updateMessage?.message) {
      return { success: true, message: result.data.updateMessage.message }
    }

    return { success: false, error: "Failed to update message" }
  }

  return {
    updateMessage,
    loading,
    error,
  }
}
