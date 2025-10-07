import type { User, Room, Message } from './main.types';

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  username: string;
  name: string;
  email: string;
  password1: string;
  password2: string;
}

export interface UpdateUserInput {
  name?: string;
  bio?: string;
  avatar?: File | null;
}

export interface CreateRoomInput {
  name: string;
  topicName: string;
  description: string;
}

export interface UpdateRoomInput {
  roomId: string;
  topicName?: string;
  description?: string;
}

export interface CreateMessageInput {
  roomId: string;
  body: string;
}

export interface UpdateMessageInput {
  messageId: string;
  body: string;
}

export interface DeleteMessageInput {
  messageId: string;
}

// Response types for mutations - these should match your GraphQL response structure
export interface AuthPayload {
  success: boolean;
  payload?: unknown;
  refreshExpiresIn?: number;
  user?: User;
  errors?: string[];
}

export interface RegisterPayload {
  success: boolean;
  user?: User;
  errors?: string[];
}

export interface UpdateUserPayload {
  updateUser: {
    user: User;
  }
}

export interface CreateRoomPayload {
  createRoom: {
    room: Room;
  };
}

export interface UpdateRoomPayload {
  updateRoom: {
    room: Room;
  };
}

export interface DeleteRoomPayload {
  deleteRoom: {
    success: boolean;
  };
}

export interface JoinRoomPayload {
  joinRoom: {
    success: boolean;
  };
}

export interface UpdateMessagePayload {
  updateMessage: {
    message: Message;
  };
}

export interface DeleteMessagePayload {
  deleteMessage: {
    success: boolean;
  };
}

export interface LogoutPayload {
  deleted: boolean;
}

export interface TokenPayload {
  exp: number;
  origIat: number;
}

export interface RefreshTokenPayload {
  payload?: unknown;
  refreshExpiresIn?: number;
}

export interface UpdateRoomForm {
  topicName?: string;
  description?: string;
}
