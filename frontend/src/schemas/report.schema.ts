import { z } from 'zod';

export const REPORT_LIMITS = {
  description: 2048,
} as const;

export const reportSchema = z.object({
  description: z.string().max(REPORT_LIMITS.description),
});

export type ReportForm = z.infer<typeof reportSchema>;
