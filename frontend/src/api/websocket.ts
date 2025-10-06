import { ref, type Ref } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from './room.api';
import { useNotifications } from '@/composables/useNotifications';

import type { Room, Message } from '@/types';
import type {
  ConnectionStatus,
  ReceivedWebSocketMessage,
  WSNewMessage,
  WSUpdateMessage,
  WSDeleteMessage,
  MessageType,
  OutgoingWebSocketMessage,
  OutgoingUpdateMessage,
  OutgoingDeleteMessage
} from '@/types';


export function useWebSocket(userSlug: string, roomSlug: string) {
  const { fetchRoomMessages } = useRoomApi();
  const socket: Ref<WebSocket | null> = ref(null);
  const messages: Ref<Message[]> = ref([]);
  const connectionStatus: Ref<ConnectionStatus> = ref('disconnected');
  const authStore = useAuthStore();
  const notifications = useNotifications();
  const reconnectAttempts = ref(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000;

  async function initializeWebSocket(): Promise<WebSocket | null> {
    if (!authStore.isAuthenticated) {
      notifications.error({ message: 'Authentication required' });
      return null;
    }

    const fetchedMessages = await fetchRoomMessages(userSlug, roomSlug);
    messages.value = [...fetchedMessages];

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${__WS_URL__}/chat/${userSlug}/${roomSlug}`;
    connectionStatus.value = 'connecting';

    socket.value = new WebSocket(wsUrl);

    socket.value.onopen = () => {
      connectionStatus.value = 'connected';
      reconnectAttempts.value = 0;
    };

    socket.value.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as ReceivedWebSocketMessage;

        switch (data.action) {
          case 'new':
            handleNewMessage(data);
            break;
          case 'update':
            handleUpdateMessage(data);
            break;
          case 'delete':
            handleDeleteMessage(data);
            break;
          default:
            console.warn('Unknown action:', data);
        }
      } catch (err) {
        console.error('WebSocket message parse error:', err);
        notifications.error({ message: 'Failed to process incoming message.' });
      }
    };

    socket.value.onerror = (err) => {
      console.error('WebSocket error:', err);
      connectionStatus.value = 'error';
      notifications.error({ message: 'WebSocket connection error' });
      attemptReconnect();
    };

    socket.value.onclose = (event) => {
      connectionStatus.value = 'disconnected';
      if (!event.wasClean) attemptReconnect();
    };

    return socket.value;
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
        bio: null
      },
      room: {} as Room // TODO: refactor this to include room.
    };
    messages.value.push(newMessage);
  }

  function handleUpdateMessage(data: WSUpdateMessage): void {
    const index = messages.value.findIndex(m => m.id === data.id);
    if (index !== -1) {
      messages.value[index] = {
        ...messages.value[index],
        body: data.body,
        edited: data.edited,
        updated: data.updated
      } as Message;
    }
  }

  function handleDeleteMessage(data: WSDeleteMessage): void {
    messages.value = messages.value.filter(m => m.id !== data.id);
  }

  function attemptReconnect(): void {
    if (reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts.value++;
      setTimeout(() => {
        initializeWebSocket();
      }, RECONNECT_DELAY * reconnectAttempts.value);
    } else {
      notifications.error({ message: 'Failed to reconnect WebSocket after multiple attempts.' });
    }
  }

  function sendMessage(message: string, messageType: MessageType = 'text'): void {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      const timestamp = new Date().toISOString();
      let msg: OutgoingWebSocketMessage;

      if (messageType === 'text') {
        msg = {
          message,
          type: 'text',
          timestamp
        };
      } else if (messageType === 'update') {
        msg = {
          messageId: message,
          message,
          type: 'update',
          timestamp
        };
      } else {
        msg = {
          messageId: message,
          type: 'delete',
          timestamp
        };
      }

      socket.value.send(JSON.stringify(msg));
    } else {
      notifications.warning('WebSocket not connected. Message not sent.');
    }
  }


  function deleteMessage(messageId: string): boolean {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      const msg: OutgoingDeleteMessage = {
        messageId,
        type: 'delete',
        timestamp: new Date().toISOString()
      };
      socket.value.send(JSON.stringify(msg));
      return true;
    } else {
      notifications.warning('WebSocket not connected. Cannot delete message.');
      return false;
    }
  }

  function updateMessage(messageId: string, newBody: string): boolean {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      const msg: OutgoingUpdateMessage = {
        messageId,
        message: newBody,
        type: 'update',
        timestamp: new Date().toISOString()
      };
      socket.value.send(JSON.stringify(msg));
      return true;
    } else {
      notifications.warning('WebSocket not connected. Cannot update message.');
      return false;
    }
  }

  function closeWebSocket(): void {
    if (socket.value) {
      socket.value.close();
      socket.value = null;
      connectionStatus.value = 'disconnected';
    }
  }

  return {
    socket,
    messages,
    connectionStatus,
    initializeWebSocket,
    sendMessage,
    deleteMessage,
    updateMessage,
    closeWebSocket
  };
}
