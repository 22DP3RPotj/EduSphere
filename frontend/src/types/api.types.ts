import type { User, Room, Message, UUID, DateTime, ReportTargetType } from './main.types';

export interface LoginInput {
  email: string;
  password: string;
}

export interface PasswordChangeInput {
  oldPassword: string;
  newPassword: string;
}

export interface PasswordResetInput {
  token: string;
  newPassword: string;
}

export interface SendInviteInput {
  roomId: UUID;
  inviteeEmail: string;
  expiresAt?: string;
  roleId?: UUID;
}

export interface CreateReportInput {
  targetType: ReportTargetType;
  targetId: UUID;
  reasonId: UUID;
  description?: string;
}

export interface CreateRoleInput {
  roomId: UUID;
  name: string;
  description: string;
  priority: number;
  permissionIds?: UUID[];
}

export interface UpdateRoleInput {
  roleId: UUID;
  name?: string;
  description?: string;
  priority?: number;
  permissionIds?: UUID[];
}


export type GqlMessage = {
  id: UUID | string
  author: User
  room: Room
  body: string
  isEdited: boolean
  createdAt: DateTime | string
  updatedAt: DateTime | string
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
  language?: string;
}

export interface CreateRoomInput {
  name: string;
  topicNames: string[];
  description: string;
}

export interface UpdateRoomInput {
  roomId: UUID;
  topicNames?: string[];
  description?: string;
}

export interface CreateMessageInput {
  roomId: UUID;
  body: string;
}

export interface UpdateMessageInput {
  messageId: UUID;
  body: string;
}

export interface DeleteMessageInput {
  messageId: UUID;
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
