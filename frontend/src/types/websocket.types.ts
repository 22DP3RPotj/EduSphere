// WebSocket connection status
export type ConnectionStatus = 'connected' | 'disconnected' | 'error' | 'connecting';

// WebSocket actions
export type MessageAction = 'new' | 'update' | 'delete';
export type MessageType = 'text' | 'update' | 'delete';

// WebSocket incoming message types
export interface WSBaseMessage {
  type: 'chat_message';
  action: MessageAction;
  id: string;
}

export interface WSNewMessage extends WSBaseMessage {
  action: 'new';
  body: string;
  created_at: string;
  updated_at: string;
  is_edited: boolean;
  author: string;
  author_id: string;
  author_avatar: string | null;
}

export interface WSUpdateMessage extends WSBaseMessage {
  action: 'update';
  body: string;
  is_edited: boolean;
  updated_at: string;
}

export interface WSDeleteMessage extends WSBaseMessage {
  action: 'delete';
}

export type ReceivedWebSocketMessage = WSNewMessage | WSUpdateMessage | WSDeleteMessage;

// Outgoing WebSocket message types
export interface OutgoingTextMessage {
  message: string;
  type: 'text';
  timestamp: string;
}

export interface OutgoingDeleteMessage {
  messageId: string;
  type: 'delete';
  timestamp: string;
}

export interface OutgoingUpdateMessage {
  messageId: string;
  message: string;
  type: 'update';
  timestamp: string;
}

export type OutgoingWebSocketMessage =
  | OutgoingTextMessage
  | OutgoingDeleteMessage
  | OutgoingUpdateMessage;