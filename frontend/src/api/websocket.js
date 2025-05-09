import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import { useRoomApi } from './room.api';
import { useNotifications } from '@/composables/useNotifications';

export function useWebSocket(username, roomSlug) {
  const { fetchRoomMessages } = useRoomApi();
  const socket = ref(null);
  const messages = ref([]);
  const connectionStatus = ref('disconnected');
  const authStore = useAuthStore();
  const notifications = useNotifications();
  const reconnectAttempts = ref(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000; // 3 seconds

  async function initializeWebSocket() {
    if (!authStore.isAuthenticated) {
      notifications.error({message: 'Authentication required'});
      return null;
    }

    const fetchedMessages = await fetchRoomMessages(username, roomSlug);
    messages.value = [...fetchedMessages];

    // const wsUrl = import.meta.env.VITE_WS_URL
    const wsUrl = `${window.location.protocol === 'https' ? 'wss' : 'ws'}://localhost/ws/chat/${username}/${roomSlug}`;
    
    function createWebSocket() {
      socket.value = new WebSocket(wsUrl);

      socket.value.onopen = () => {
        connectionStatus.value = 'connected';
        reconnectAttempts.value = 0;
      };

      socket.value.onmessage = (event) => {
        const receivedMessage = JSON.parse(event.data);

        if (receivedMessage.error) {
          notifications.error(receivedMessage);
          return;
        }
        
        // Handle different message actions
        const action = receivedMessage.action || 'new'; // Default to 'new' for backward compatibility
        
        switch (action) {
          case 'new':
            handleNewMessage(receivedMessage);
            break;
          case 'delete':
            handleDeleteMessage(receivedMessage);
            break;
          case 'update':
            handleUpdateMessage(receivedMessage);
            break;
          default:
            handleNewMessage(receivedMessage);
        }
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

    function handleNewMessage(receivedMessage) {
      messages.value.push({
        ...receivedMessage,
        created: receivedMessage.created,
        user: receivedMessage.user || { username: receivedMessage.username }
      });
    }

    function handleDeleteMessage(receivedMessage) {
      // Remove the message with the specified ID
      const messageId = receivedMessage.id;
      messages.value = messages.value.filter(msg => msg.id !== messageId);
    }

    function handleUpdateMessage(receivedMessage) {
      // Update the message with the new content
      const messageId = receivedMessage.id;
      const messageIndex = messages.value.findIndex(msg => msg.id === messageId);
      
      if (messageIndex !== -1) {
        messages.value[messageIndex] = {
          ...messages.value[messageIndex],
          body: receivedMessage.body,
          edited: receivedMessage.edited,
          updated: receivedMessage.updated
        };
      }
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

  function deleteMessage(messageId) {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({
        messageId,
        type: 'delete',
        timestamp: new Date().toISOString()
      }));
      return true;
    } else {
      notifications.warning('WebSocket is not connected. Cannot delete message.');
      return false;
    }
  }

  function updateMessage(messageId, newBody) {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify({
        messageId,
        message: newBody,
        type: 'update',
        timestamp: new Date().toISOString()
      }));
      return true;
    } else {
      notifications.warning('WebSocket is not connected. Cannot update message.');
      return false;
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
    closeWebSocket: () => {
      if (socket.value) {
        socket.value.close();
        socket.value = null;
      }
    }
  };
}