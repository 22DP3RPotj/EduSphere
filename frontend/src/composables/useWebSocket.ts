import { ref, type Ref } from "vue"
import { useAuthStore } from "@/stores/auth.store"
import { ROOM_MESSAGES_QUERY } from "@/api/graphql";
import { apolloClient } from "@/api/apollo.client";
import type { Room, Message, DateTime, UUID, GqlMessage } from "@/types"
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

export function useWebSocket(
  roomId: string,
) {
  const socket: Ref<WebSocket | null> = ref(null)
  const messages: Ref<Message[]> = ref([])
  const connectionStatus: Ref<ConnectionStatus> = ref("disconnected")
  const connectionError: Ref<string | null> = ref(null)
  const advisoryMessage: Ref<string | null> = ref(null)
  const reconnectAttempts = ref<number>(0)
  const isConnected = ref<boolean>(false)
  // Track pending sends awaiting server ack
  type PendingSend = { body: string; resolve: (ok: boolean) => void; timer: number; createdAt: number }
  const pendingSends: Ref<PendingSend[]> = ref([])
  const SEND_ACK_TIMEOUT = 1500
  const MAX_PENDING = 50
  
  const authStore = useAuthStore()
  
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY = 3000

  // Type guards to avoid any casts
  type ServerErrorEnvelope = { error: string }
  function isServerErrorEnvelope(v: unknown): v is ServerErrorEnvelope {
    return (
      typeof v === "object" && v !== null &&
      "error" in (v as Record<string, unknown>) &&
      typeof (v as Record<string, unknown>).error === "string"
    )
  }

  function isWSNewMessage(msg: ReceivedWebSocketMessage): msg is WSNewMessage {
    return msg.action === "new"
  }
  function isWSUpdateMessage(msg: ReceivedWebSocketMessage): msg is WSUpdateMessage {
    return msg.action === "update"
  }
  function isWSDeleteMessage(msg: ReceivedWebSocketMessage): msg is WSDeleteMessage {
    return msg.action === "delete"
  }

  function asDateTime(value: string): DateTime {
    return value as unknown as DateTime
  }

  function asUUID(value: string): UUID {
    return value as unknown as UUID
  }

  async function fetchRoomMessages(): Promise<Message[]> {
    const response = await apolloClient.query({
      query: ROOM_MESSAGES_QUERY,
      variables: { roomId },
      fetchPolicy: 'network-only'
    });

    const items: GqlMessage[] = response.data?.messages || []
    const normalized: Message[] = items.map((m): Message => ({
      id: asUUID(m.id as string),
      author: m.author,
      room: m.room,
      parent: null,
      body: m.body,
      is_edited: m.isEdited,
      created_at: asDateTime(m.createdAt as string),
      updated_at: asDateTime(m.updatedAt as string),
    }))
    return normalized
  }

  async function fetchInitialMessages(): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await fetchRoomMessages();
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
    const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${__WS_URL__}/chat/${roomId}`
    
    // Close existing connection if any
    closeWebSocket()
    
    connectionStatus.value = "connecting"
    connectionError.value = null
    advisoryMessage.value = null

    try {
      const ws = new WebSocket(wsUrl)
      socket.value = ws

      ws.onopen = () => {
        if (socket.value !== ws) return
        connectionStatus.value = "connected"
        connectionError.value = null
        advisoryMessage.value = null
        reconnectAttempts.value = 0
        isConnected.value = true
      }

      ws.onmessage = (event: MessageEvent) => {
        if (socket.value !== ws) return
        try {
          const raw = JSON.parse(event.data)
          // Error envelope from server (advisory: do not mark connection error)
          if (isServerErrorEnvelope(raw)) {
            advisoryMessage.value = raw.error
            const pending = pendingSends.value.shift()
            if (pending) {
              clearTimeout(pending.timer)
              pending.resolve(false)
            }
            return
          }

          const data = raw as ReceivedWebSocketMessage
          switch (data.action) {
            case "new": {
              const newData = isWSNewMessage(data) ? data : undefined
              if (newData) {
                handleNewMessage(newData)
                // Resolve oldest pending if it matches our echo (by author and body)
                const firstPending = pendingSends.value[0]
                if (
                  authStore.user?.id &&
                  newData.author_id === authStore.user.id &&
                  firstPending &&
                  firstPending.body === String(newData.body ?? "").trim()
                ) {
                  const pending = pendingSends.value.shift()
                  if (pending) {
                    clearTimeout(pending.timer)
                    pending.resolve(true)
                  }
                }
              }
              break
            }
            case "update": {
              const upd = isWSUpdateMessage(data) ? data : undefined
              if (upd) handleUpdateMessage(upd)
              break
            }
            case "delete": {
              const del = isWSDeleteMessage(data) ? data : undefined
              if (del) handleDeleteMessage(del)
              break
            }
            default: {
              console.warn("[v0] Unknown WebSocket action:", data)
            }
          }
        } catch (err) {
          console.error("[v0] WebSocket message parse error:", err)
          advisoryMessage.value = "Failed to process incoming message"
        }
      }

      ws.onerror = (err) => {
        if (socket.value !== ws) return
        console.error("[v0] WebSocket error:", err)
        console.error("[v0] WebSocket URL attempted:", wsUrl)
        connectionStatus.value = "error"
        connectionError.value = "Connection error - check permissions and ensure you are a participant"
        advisoryMessage.value = null
        isConnected.value = false
        // Fail all pending sends
        pendingSends.value.splice(0).forEach(p => { clearTimeout(p.timer); p.resolve(false) })
        attemptReconnect()
      }

      ws.onclose = (event) => {
        if (socket.value !== ws) return
        connectionStatus.value = "disconnected"
        isConnected.value = false
        // Fail all pending sends
        pendingSends.value.splice(0).forEach(p => { clearTimeout(p.timer); p.resolve(false) })
        if (!event.wasClean) {
          connectionError.value = "Connection lost"
          advisoryMessage.value = null
          attemptReconnect()
        }
      }

      return { success: true }
    } catch (err) {
      connectionError.value = err instanceof Error ? err.message : "Failed to connect"
      advisoryMessage.value = null
      return { success: false, error: connectionError.value }
    }
  }

  // TODO: real values
  function handleNewMessage(data: WSNewMessage): void {
    const newMessage: Message = {
      id: asUUID(data.id),
      body: data.body,
      created_at: asDateTime(data.created_at),
      updated_at: asDateTime(data.updated_at),
      parent: null,
      is_edited: data.is_edited,
      author: {
        id: asUUID(data.author_id),
        username: data.author,
        avatar: data.author_avatar,
        name: data.author,
        bio: null,
        isStaff: false,
        isActive: false,
        isSuperuser: false,
        dateJoined: "",
      },
      room: {} as Room,
    }
    messages.value.push(newMessage)
  }

  function handleUpdateMessage(data: WSUpdateMessage): void {
    const messageId = asUUID(data.id)
    const index = messages.value.findIndex((m) => m.id === messageId)
    if (index !== -1) {
      messages.value[index] = {
        ...messages.value[index],
        body: data.body,
        is_edited: data.is_edited,
        updated_at: asDateTime(data.updated_at),
      } as Message
    }
  }

  function handleDeleteMessage(data: WSDeleteMessage): void {
    const messageId = asUUID(data.id)
    messages.value = messages.value.filter((m) => m.id !== messageId)
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

  function sendMessage(message: string): Promise<boolean> {
    const trimmed = String(message ?? "").trim()
    if (!trimmed) return Promise.resolve(false)
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
      connectionError.value = "Not connected to chat server"
      return Promise.resolve(false)
    }

    return new Promise<boolean>((resolve) => {
      // Cap queue
      if (pendingSends.value.length >= MAX_PENDING) {
        const dropped = pendingSends.value.shift()
        if (dropped) { clearTimeout(dropped.timer); dropped.resolve(false) }
      }
      try {
        const msg: OutgoingWebSocketMessage = {
          message: trimmed,
          type: "text",
          timestamp: new Date().toISOString(),
        }
        socket.value!.send(JSON.stringify(msg))
      } catch (err) {
        advisoryMessage.value = err instanceof Error ? err.message : "Failed to send message"
        resolve(false)
        return
      }

      const timer = window.setTimeout(() => {
        // Timeout: consider failed
        const idx = pendingSends.value.findIndex(p => p.resolve === resolve)
        if (idx !== -1) pendingSends.value.splice(idx, 1)
        resolve(false)
      }, SEND_ACK_TIMEOUT)
      pendingSends.value.push({ body: trimmed, resolve, timer, createdAt: Date.now() })
    })
  }

  function deleteMessage(messageId: UUID): boolean {
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
      advisoryMessage.value = err instanceof Error ? err.message : "Failed to delete message"
      return false
    }
  }

  function updateMessage(messageId: UUID, newBody: string): boolean {
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
      advisoryMessage.value = err instanceof Error ? err.message : "Failed to update message"
      return false
    }
  }

  function closeWebSocket(): void {
    if (socket.value) {
      socket.value.close()
      socket.value = null
      connectionStatus.value = "disconnected"
      connectionError.value = null
      advisoryMessage.value = null
      // Fail all pending sends on manual close
      pendingSends.value.splice(0).forEach(p => { clearTimeout(p.timer); p.resolve(false) })
    }
  }

  function clearError(): void {
    connectionError.value = null
  }

  function clearAdvisory(): void {
    advisoryMessage.value = null
  }

  return {
    socket,
    messages,
    connectionStatus,
    connectionError,
    advisoryMessage,
    isConnected,
    initializeWebSocket,
    sendMessage,
    deleteMessage,
    updateMessage,
    closeWebSocket,
    clearError,
    clearAdvisory,
  }
}