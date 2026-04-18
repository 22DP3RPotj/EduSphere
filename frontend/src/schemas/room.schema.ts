import { z } from 'zod';
import { ROOM_LIMITS } from './field-limits';

export { ROOM_LIMITS } from './field-limits';

export const createRoomSchema = z.object({
  name: z.string().min(1).max(ROOM_LIMITS.name),
  description: z.string().max(ROOM_LIMITS.description),
  topicNames: z.array(z.string().max(ROOM_LIMITS.topicName)),
});

export const editRoomSchema = z.object({
  description: z.string().max(ROOM_LIMITS.description),
  topicNames: z.array(z.string().max(ROOM_LIMITS.topicName)),
});

export type CreateRoomForm = z.infer<typeof createRoomSchema>;
export type EditRoomForm = z.infer<typeof editRoomSchema>;
