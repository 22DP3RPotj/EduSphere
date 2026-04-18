import { z } from 'zod';
import { MESSAGE_LIMITS } from './field-limits';

export { MESSAGE_LIMITS } from './field-limits';

export const messageSchema = z.object({
  body: z.string().min(1).max(MESSAGE_LIMITS.body),
});

export type MessageForm = z.infer<typeof messageSchema>;
