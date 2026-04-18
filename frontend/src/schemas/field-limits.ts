export const USER_LIMITS = {
  name: 32,
  bio: 4096,
} as const;

export const ROOM_LIMITS = {
  name: 64,
  description: 512,
  topicName: 32,
} as const;

export const MESSAGE_LIMITS = {
  body: 2048,
} as const;

export const REPORT_LIMITS = {
  description: 2048,
} as const;
