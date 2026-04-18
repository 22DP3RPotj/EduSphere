import { z } from 'zod';
import { USER_LIMITS } from './field-limits';

export { USER_LIMITS } from './field-limits';

export const profileEditSchema = z.object({
  name: z.string().max(USER_LIMITS.name),
  bio: z.string().max(USER_LIMITS.bio),
});

export type ProfileEditForm = z.infer<typeof profileEditSchema>;
