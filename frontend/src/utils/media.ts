export function buildAvatarUrl(avatar: string | null): string {
  if (!avatar) return '/default.svg';

  const v = avatar.trim();

  // Absolute or special URLs
  if (
    v.startsWith('http://') ||
    v.startsWith('https://') ||
    v.startsWith('data:') ||
    v.startsWith('blob:')
  ) {
    return v;
  }

  // Ensure absolute path (prevents resolving under /u/..., /chat/..., etc.)
  const absolute = v.startsWith('/') ? v : `/${v}`;

  // Backend may send MEDIA_URL-based paths; nginx blocks /media/ externally.
  if (absolute.startsWith('/media/avatars/')) {
    return absolute.replace('/media/avatars/', '/avatars/');
  }

  // Already correct
  if (absolute.startsWith('/avatars/')) return absolute;

  // Fallback: treat as a filename/relative within avatars
  return `/avatars/${absolute.replace(/^\//, '')}`;
}