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
  roomId: string;
  inviteeId: string;
  expiresAt?: string;
  roleId?: string;
}

export interface CreateReportInput {
  targetType: ReportTargetType;
  targetId: string;
  reasonId: string;
  description?: string;
}

export interface CreateRoleInput {
  roomId: string;
  name: string;
  description: string;
  priority: number;
  permissionIds?: string[];
}

export interface UpdateRoleInput {
  roleId: string;
  name?: string;
  description?: string;
  priority?: number;
  permissionIds?: string[];
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
  roomId: string;
  topicNames?: string[];
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
