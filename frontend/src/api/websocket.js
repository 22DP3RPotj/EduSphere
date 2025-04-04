import { ref } from 'vue';
import { apolloClient } from '@/api/apollo.client';
import { gql } from '@apollo/client/core';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from './room.api';
import { useApi } from '@/composables/useApi';
import { useNotifications } from '@/composables/useNotifications';

export function useWebSocket(username, roomSlug) {
  const { fetchRoomMessages } = useRoomApi();
  const api = useApi();
  const socket = ref(null);
  const messages = ref([]);
  const connectionStatus = ref('disconnected');
  const authStore = useAuthStore();
  const notifications = useNotifications();
  const reconnectAttempts = ref(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000; // 3 seconds

  async function initializeWebSocket() {
    const token = authStore.token;
    if (!token) {
      notifications.error({message: 'Authentication required'});
      return null;
    }

    try {
      const room_messages = await api.call(
        () => fetchRoomMessages(username, roomSlug),
        'Messages fetched'
      )
      messages.value = [...room_messages];
    } catch (error) {
      notifications.error({message: 'Failed to load messages'});
    }

    const wsUrl = import.meta.env.VITE_WEBSOCKET_URL || `ws://localhost/ws/chat/${username}/${roomSlug}/?token=${token}`;
    
    function createWebSocket() {
      socket.value = new WebSocket(wsUrl);

      socket.value.onopen = () => {
        connectionStatus.value = 'connected';
        reconnectAttempts.value = 0;
      };

      socket.value.onmessage = (event) => {
        const receivedMessage = JSON.parse(event.data);
        
        // Use received timestamp or generate a new one
        const messageTimestamp = receivedMessage.timestamp 
          ? new Date(receivedMessage.timestamp).toISOString() 
          : new Date().toISOString();

        messages.value.push({
          ...receivedMessage,
          created: messageTimestamp,
          user: receivedMessage.user || { username: receivedMessage.username }
        });
      };

      socket.value.onerror = (error) => {
        connectionStatus.value = 'error';
        notifications.error({message: 'WebSocket connection error'});
        attemptReconnect();
      };

      socket.value.onclose = (event) => {
        connectionStatus.value = 'disconnected';
        if (!event.wasClean) {
          attemptReconnect();
        }
      };

      return socket.value;
    }

    function attemptReconnect() {
      if (reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.value++;
        setTimeout(() => {
          createWebSocket();
        }, RECONNECT_DELAY * reconnectAttempts.value);
      } else {
        notifications.error({message: 'WebSocket connection failed after multiple attempts'});
      }
    }

    return createWebSocket();
  }

  function sendMessage(message, messageType = 'text') {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({ 
        message, 
        type: messageType,
        timestamp: new Date().toISOString()
      }));
    } else {
      notifications.warning('WebSocket is not connected. Message not sent.');
    }
  }

  return {
    socket,
    messages,
    connectionStatus,
    initializeWebSocket,
    sendMessage,
    closeWebSocket: () => {
      if (socket.value) {
        socket.value.close();
        socket.value = null;
      }
    }
  };
}