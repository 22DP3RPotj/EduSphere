import type { DateTime, UUID } from "./main.types";

// WebSocket connection status
export type ConnectionStatus = 'connected' | 'disconnected' | 'error' | 'connecting';

// WebSocket actions
export type MessageAction = 'new' | 'update' | 'delete';
export type MessageType = 'text' | 'update' | 'delete';

// WebSocket incoming message types
export interface WSBaseMessage {
  type: 'chat_message';
  action: MessageAction;
  id: UUID;
}

export interface WSNewMessage extends WSBaseMessage {
  action: 'new';
  body: string;
  created_at: DateTime;
  updated_at: DateTime;
  is_edited: boolean;
  author: string;
  author_id: UUID;
  author_avatar: string | null;
}

export interface WSUpdateMessage extends WSBaseMessage {
  action: 'update';
  body: string;
  is_edited: boolean;
  updated_at: DateTime;
}

export interface WSDeleteMessage extends WSBaseMessage {
  action: 'delete';
}

export type ReceivedWebSocketMessage = WSNewMessage | WSUpdateMessage | WSDeleteMessage;

// Outgoing WebSocket message types
export interface OutgoingTextMessage {
  message: string;
  type: 'text';
  timestamp: DateTime;
}

export interface OutgoingDeleteMessage {
  messageId: UUID;
  type: 'delete';
  timestamp: DateTime;
}

export interface OutgoingUpdateMessage {
  messageId: UUID;
  message: string;
  type: 'update';
  timestamp: DateTime;
}

export type OutgoingWebSocketMessage =
  | OutgoingTextMessage
  | OutgoingDeleteMessage
  | OutgoingUpdateMessage;