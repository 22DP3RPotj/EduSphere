import { z } from 'zod';
import { REPORT_LIMITS } from './field-limits';

export { REPORT_LIMITS } from './field-limits';

export const reportSchema = z.object({
  description: z.string().max(REPORT_LIMITS.description),
});

export type ReportForm = z.infer<typeof reportSchema>;
