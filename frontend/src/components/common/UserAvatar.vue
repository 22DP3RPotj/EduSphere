<template>
  <div :class="avatarClasses">
    <img 
      v-if="avatarSrc" 
      :src="avatarSrc" 
      :alt="`${username}'s avatar`" 
      class="avatar-image"
    />
    <div v-else class="avatar-fallback">
      {{ initials }}
    </div>
    <span v-if="showStatus" class="status-indicator"></span>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue';

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value: string) => ['small', 'medium', 'large'].includes(value)
  },
  showStatus: {
    type: Boolean,
    default: false
  }
});

const username = computed(() => {
  return props.user.username || props.user.name || '[Unknown]';
});

const avatarSrc = computed(() => {
  const avatar = props.user.avatar
  return avatar ? `/media/${avatar}` : '/default.svg';
});

const initials = computed(() => {
  if (!username.value || username.value === '[Unknown]') return '?';
  
  const parts = username.value.split(' ');
  if (parts.length === 1) {
    return username.value.charAt(0).toUpperCase();
  }
  
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
});

const avatarClasses = computed(() => {
  const classes = ['user-avatar'];
  classes.push(`size-${props.size}`);
  return classes;
});
</script>

<style scoped>
.user-avatar {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--bg-color);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-color);
  color: var(--white);
  font-weight: 600;
}

.size-small {
  width: 32px;
  height: 32px;
  font-size: 12px;
}

.size-medium {
  width: 40px;
  height: 40px;
  font-size: 16px;
}

.size-large {
  width: 64px;
  height: 64px;
  font-size: 24px;
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #10b981; /* Online status color (green) */
  border: 2px solid var(--white);
}

.size-small .status-indicator {
  width: 8px;
  height: 8px;
}

.size-large .status-indicator {
  width: 12px;
  height: 12px;
}
</style>
