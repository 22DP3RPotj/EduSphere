import { ref, type Ref } from "vue"
import { useAuthStore } from "@/stores/auth.store"
import { useRoomApi } from '../api/room.api';
import type { Room, Message } from "@/types"
import type {
  ConnectionStatus,
  ReceivedWebSocketMessage,
  WSNewMessage,
  WSUpdateMessage,
  WSDeleteMessage,
  OutgoingWebSocketMessage,
  OutgoingUpdateMessage,
  OutgoingDeleteMessage,
} from "@/types"

export function useWebSocket(userSlug: string, roomSlug: string) {
  const { fetchRoomMessages } = useRoomApi();
  const socket: Ref<WebSocket | null> = ref(null)
  const messages: Ref<Message[]> = ref([])
  const connectionStatus: Ref<ConnectionStatus> = ref("disconnected")
  const connectionError: Ref<string | null> = ref(null)
  const authStore = useAuthStore()
  const reconnectAttempts = ref(0)
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY = 3000

  async function fetchInitialMessages(): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await fetchRoomMessages(userSlug, roomSlug);
      messages.value = [...response];

      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Failed to fetch messages",
      }
    }
  }

  async function initializeWebSocket(): Promise<{ success: boolean; error?: string }> {
    if (!authStore.isAuthenticated) {
      return { success: false, error: "Authentication required" }
    }

    // Fetch initial messages
    const fetchResult = await fetchInitialMessages()
    if (!fetchResult.success) {
      connectionError.value = fetchResult.error || "Failed to load messages"
      return fetchResult
    }

    // Initialize WebSocket connection
    const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${__WS_URL__}/chat/${userSlug}/${roomSlug}`
    connectionStatus.value = "connecting"
    connectionError.value = null

    try {
      socket.value = new WebSocket(wsUrl)

      socket.value.onopen = () => {
        connectionStatus.value = "connected"
        connectionError.value = null
        reconnectAttempts.value = 0
      }

      socket.value.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as ReceivedWebSocketMessage

          switch (data.action) {
            case "new":
              handleNewMessage(data)
              break
            case "update":
              handleUpdateMessage(data)
              break
            case "delete":
              handleDeleteMessage(data)
              break
            default:
              console.warn("[v0] Unknown WebSocket action:", data)
          }
        } catch (err) {
          console.error("[v0] WebSocket message parse error:", err)
          connectionError.value = "Failed to process incoming message"
        }
      }

      socket.value.onerror = (err) => {
        console.error("[v0] WebSocket error:", err)
        connectionStatus.value = "error"
        connectionError.value = "Connection error occurred"
        attemptReconnect()
      }

      socket.value.onclose = (event) => {
        connectionStatus.value = "disconnected"
        if (!event.wasClean) {
          connectionError.value = "Connection lost"
          attemptReconnect()
        }
      }

      return { success: true }
    } catch (err) {
      connectionError.value = err instanceof Error ? err.message : "Failed to connect"
      return { success: false, error: connectionError.value }
    }
  }

  function handleNewMessage(data: WSNewMessage): void {
    const newMessage: Message = {
      id: data.id,
      body: data.body,
      created: data.created,
      updated: data.updated,
      edited: data.edited,
      user: {
        id: data.user_id,
        username: data.user,
        avatar: data.userAvatar,
        name: data.user,
        bio: null,
      },
      room: {} as Room,
    }
    messages.value.push(newMessage)
  }

  function handleUpdateMessage(data: WSUpdateMessage): void {
    const index = messages.value.findIndex((m) => m.id === data.id)
    if (index !== -1) {
      messages.value[index] = {
        ...messages.value[index],
        body: data.body,
        edited: data.edited,
        updated: data.updated,
      } as Message
    }
  }

  function handleDeleteMessage(data: WSDeleteMessage): void {
    messages.value = messages.value.filter((m) => m.id !== data.id)
  }

  function attemptReconnect(): void {
    if (reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts.value++
      setTimeout(() => {
        initializeWebSocket()
      }, RECONNECT_DELAY * reconnectAttempts.value)
    } else {
      connectionError.value = "Failed to reconnect after multiple attempts"
    }
  }

  function sendMessage(message: string): boolean {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      connectionError.value = "Not connected to chat server"
      return false
    }

    try {
      const msg: OutgoingWebSocketMessage = {
        message,
        type: "text",
        timestamp: new Date().toISOString(),
      }
      socket.value.send(JSON.stringify(msg))
      return true
    } catch (err) {
      connectionError.value = err instanceof Error ? err.message : "Failed to send message"
      return false
    }
  }

  function deleteMessage(messageId: string): boolean {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      connectionError.value = "Not connected to chat server"
      return false
    }

    try {
      const msg: OutgoingDeleteMessage = {
        messageId,
        type: "delete",
        timestamp: new Date().toISOString(),
      }
      socket.value.send(JSON.stringify(msg))
      return true
    } catch (err) {
      connectionError.value = err instanceof Error ? err.message : "Failed to delete message"
      return false
    }
  }

  function updateMessage(messageId: string, newBody: string): boolean {
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      connectionError.value = "Not connected to chat server"
      return false
    }

    try {
      const msg: OutgoingUpdateMessage = {
        messageId,
        message: newBody,
        type: "update",
        timestamp: new Date().toISOString(),
      }
      socket.value.send(JSON.stringify(msg))
      return true
    } catch (err) {
      connectionError.value = err instanceof Error ? err.message : "Failed to update message"
      return false
    }
  }

  function closeWebSocket(): void {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      connectionStatus.value = "disconnected"
      connectionError.value = null
    }
  }

  function clearError(): void {
    connectionError.value = null
  }

  return {
    socket,
    messages,
    connectionStatus,
    connectionError,
    initializeWebSocket,
    sendMessage,
    deleteMessage,
    updateMessage,
    closeWebSocket,
    clearError,
  }
}
