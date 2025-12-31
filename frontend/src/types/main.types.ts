export type UUID = string & { readonly __brand: unique symbol }
export type DateTime = string & { readonly __brand: unique symbol }

export interface User {
  id: UUID;
  username: string;
  name: string;
  bio: string | null;
  avatar: string | null;
  isStaff: boolean;
  isActive: boolean;
  isSuperuser: boolean;
  dateJoined: string;
}

export interface Permission {
  id: UUID;
  code: string;
  description: string;
}

export interface Role {
  id: UUID;
  name: string;
  description: string;
  priority: number;
  permissions: Permission[];
}

export interface Participant {
  id: UUID;
  user: User;
  role: Role;
  joined_at: string;
}

export interface Topic {
  // id: UUID;
  name: string;
}

export interface Room {
  id: UUID;
  name: string;
  slug: string;
  host: User;
  topics: Topic[];
  description: string;
  participants: User[];
  updated_at: DateTime;
  created_at: DateTime;
}

export interface Message {
  id: UUID;
  user: User;
  room: Room;
  parent: Message | null;
  body: string;
  is_edited: boolean;
  created_at: DateTime;
  updated_at: DateTime;
}

export interface Report {
  id: UUID;
  body: string;
  reason: string;
  status: string;
  moderatorNote: string | null;
  created_at: DateTime;
  updated_at: DateTime;
  user: User;
  room: Room;
  moderator: User | null;
}

// Pagination types
export interface PageInfo {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor?: string;
  endCursor?: string;
}

export interface Connection<T> {
  edges: Array<{
    node: T;
    cursor: string;
  }>;
  pageInfo: PageInfo;
  totalCount?: number;
}

// Filter types
export interface RoomFilters {
  topic?: string;
  search?: string;
  host?: string;
}

export interface MessageFilters {
  room?: string;
  user?: string;
  search?: string;
}

export interface AuthStatus {
  isAuthenticated: boolean;
  user: User | null;
}