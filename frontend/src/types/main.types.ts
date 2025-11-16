export interface User {
  id: string;
  username: string;
  name: string;
  bio: string | null;
  avatar: string | null;
  isStaff: boolean;
  isActive: boolean;
  isSuperuser: boolean;
  dateJoined: string;
}

export interface Topic {
  name: string;
}

export interface Room {
  id: string;
  name: string;
  slug: string;
  host: User;
  topics: Topic[];
  description: string;
  participants: User[];
  updated: string;
  created: string;
}

export interface Message {
  id: string;
  user: User;
  room: Room;
  body: string;
  edited: boolean;
  created: string;
  updated: string;
}

export interface Report {
  id: string;
  body: string;
  reason: string;
  status: string;
  moderatorNote: string | null;
  created: string;
  updated: string;
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