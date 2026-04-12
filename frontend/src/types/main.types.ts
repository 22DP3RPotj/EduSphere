export type UUID = string & { readonly __brand: unique symbol }
export type DateTime = string & { readonly __brand: unique symbol }

export interface User {
  id: UUID;
  username: string;
  name: string;
  bio: string | null;
  avatar: string | null;
  language: string;
  isStaff: boolean;
  isActive: boolean;
  isSuperuser: boolean;
  dateJoined: DateTime;
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
  joinedAt: DateTime;
}

export interface Topic {
  id: UUID;
  name: string;
}

export interface Room {
  id: UUID;
  name: string;
  host: User;
  topics: Topic[];
  description: string;
  participants: Participant[];
  updatedAt: DateTime;
  createdAt: DateTime;
}

export interface Message {
  id: UUID;
  author: User;
  room: Room;
  parent: Message | null;
  body: string;
  isEdited: boolean;
  createdAt: DateTime;
  updatedAt: DateTime;
}

export interface Report {
  id: UUID;
  description: string | null;
  reason: ReportReason;
  reporter: User;
  target: Room | User | Message;
  case: ModerationCase | null;
  createdAt: DateTime;
}

export interface ReportReason {
  id: UUID;
  slug: string;
  label: string;
  isActive: boolean;
}

export enum InviteStatus {
  PENDING = 'PENDING',
  ACCEPTED = 'ACCEPTED',
  DECLINED = 'DECLINED',
  EXPIRED = 'EXPIRED',
  REVOKED = 'REVOKED',
}

export interface Invite {
  id: UUID;
  token: UUID;
  room: { id: UUID; name: string };
  inviter: User;
  invitee: User;
  role: Role | null;
  status: InviteStatus;
  createdAt: DateTime;
  expiresAt: DateTime | null;
}

export enum CaseStatus {
  PENDING = 'PENDING',
  UNDER_REVIEW = 'UNDER_REVIEW',
  RESOLVED = 'RESOLVED',
  DISMISSED = 'DISMISSED',
}

export enum CasePriority {
  LOW = 0,
  MEDIUM = 1,
  HIGH = 2,
}

export enum ActionType {
  NO_VIOLATION = 'NO_VIOLATION',
  CONTENT_REMOVED = 'CONTENT_REMOVED',
  WARNING = 'WARNING',
  TEMP_BAN = 'TEMP_BAN',
  PERM_BAN = 'PERM_BAN',
}

export interface ModerationCase {
  id: UUID;
  status: CaseStatus;
  priority: number;
  reports: Report[];
  actions: ModerationAction[];
  target: Room | User | Message;
  createdAt: DateTime;
  updatedAt: DateTime;
}

export interface ModerationAction {
  id: UUID;
  action: ActionType;
  note: string | null;
  moderator: User;
  createdAt: DateTime;
}

export enum ReportTargetType {
  ROOM = 'ROOM',
  USER = 'USER',
  MESSAGE = 'MESSAGE',
}

export interface AuditEntry {
  pghId: string;
  pghCreatedAt: DateTime;
  pghLabel: string;
  pghObjId: UUID;
  actor: User | null;
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
  author?: string;
  search?: string;
}

export interface AuthStatus {
  isAuthenticated: boolean;
  user: User | null;
}