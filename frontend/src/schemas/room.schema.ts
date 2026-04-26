import { z } from 'zod';
import { ROOM_LIMITS } from './field-limits';

export { ROOM_LIMITS } from './field-limits';

export const VISIBILITY_OPTIONS = ['PUBLIC', 'PRIVATE'] as const;
export type RoomVisibility = (typeof VISIBILITY_OPTIONS)[number];

export const createRoomSchema = z.object({
  name: z.string().min(1).max(ROOM_LIMITS.name),
  description: z.string().max(ROOM_LIMITS.description),
  topicNames: z.array(z.string().max(ROOM_LIMITS.topicName)),
  visibility: z.enum(VISIBILITY_OPTIONS).default('PUBLIC'),
});

export const editRoomSchema = z.object({
  description: z.string().max(ROOM_LIMITS.description),
  topicNames: z.array(z.string().max(ROOM_LIMITS.topicName)),
  visibility: z.enum(VISIBILITY_OPTIONS).optional(),
});

export type CreateRoomForm = z.infer<typeof createRoomSchema>;
export type EditRoomForm = z.infer<typeof editRoomSchema>;
