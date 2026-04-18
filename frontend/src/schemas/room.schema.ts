import { z } from 'zod';

export const ROOM_LIMITS = {
  name: 64,
  description: 512,
  topicName: 32,
} as const;

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
