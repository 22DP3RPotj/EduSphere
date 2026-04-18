import { z } from 'zod';

export const MESSAGE_LIMITS = {
  body: 2048,
} as const;

export const messageSchema = z.object({
  body: z.string().min(1).max(MESSAGE_LIMITS.body),
});

export type MessageForm = z.infer<typeof messageSchema>;
