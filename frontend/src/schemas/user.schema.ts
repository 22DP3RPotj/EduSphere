import { z } from 'zod';

export const USER_LIMITS = {
  name: 32,
  bio: 4096,
} as const;

export const profileEditSchema = z.object({
  name: z.string().max(USER_LIMITS.name),
  bio: z.string().max(USER_LIMITS.bio),
});

export type ProfileEditForm = z.infer<typeof profileEditSchema>;
