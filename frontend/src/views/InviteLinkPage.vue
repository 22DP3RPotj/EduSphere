<template>
  <div class="form-page">
    <div class="form-container">
      <div class="form-box">
        <div class="form-content">

          <!-- Loading -->
          <div v-if="loading" class="status-message">
            <font-awesome-icon icon="spinner" spin size="2x" />
            <p>{{ t('invite.loadingInvite') }}</p>
          </div>

          <!-- Not found / network error -->
          <div v-else-if="!invite" class="status-message error">
            <font-awesome-icon icon="exclamation-circle" size="2x" />
            <h2>{{ t('invite.inviteNotFound') }}</h2>
            <button class="submit-btn secondary" @click="router.push('/')">
              {{ t('auth.goToHome') }}
            </button>
          </div>

          <!-- Expired -->
          <div v-else-if="invite.status === 'EXPIRED'" class="status-message error">
            <font-awesome-icon icon="clock" size="2x" />
            <h2>{{ t('invite.inviteExpired') }}</h2>
            <button class="submit-btn secondary" @click="router.push('/')">
              {{ t('auth.goToHome') }}
            </button>
          </div>

          <!-- Already accepted / declined / revoked -->
          <div v-else-if="invite.status !== 'PENDING'" class="status-message">
            <font-awesome-icon icon="info-circle" size="2x" />
            <h2>{{ t('invite.inviteAlreadyUsed') }}</h2>
            <p class="status-badge" :class="invite.status.toLowerCase()">{{ formatStatus(invite.status) }}</p>
            <button class="submit-btn secondary" @click="router.push('/')">
              {{ t('auth.goToHome') }}
            </button>
          </div>

          <!-- Pending invite -->
          <div v-else class="invite-card">
            <div class="invite-icon">
              <font-awesome-icon icon="envelope" size="2x" />
            </div>

            <h2>{{ t('invite.inviteFor') }}</h2>
            <p class="room-name">{{ invite.room.name }}</p>

            <div class="invite-details">
              <div class="detail-row">
                <span class="label">{{ t('invite.invitedBy') }}</span>
                <span class="value">{{ invite.inviter.name || invite.inviter.username }}</span>
              </div>
              <div v-if="invite.role" class="detail-row">
                <span class="label">{{ t('invite.joinAs') }}</span>
                <span class="value">{{ invite.role.name }}</span>
              </div>
              <div v-if="invite.expiresAt" class="detail-row">
                <span class="label">{{ t('invite.inviteExpires') }}</span>
                <span class="value">{{ formatDate(invite.expiresAt) }}</span>
              </div>
            </div>

            <div class="action-buttons">
              <template v-if="isInvitee">
                <button class="submit-btn" :disabled="acceptLoading || declineLoading" @click="handleAccept">
                  <font-awesome-icon v-if="acceptLoading" icon="spinner" spin />
                  <span v-else>{{ t('invite.acceptInvite') }}</span>
                </button>
                <button class="submit-btn secondary" :disabled="acceptLoading || declineLoading" @click="handleDecline">
                  <font-awesome-icon v-if="declineLoading" icon="spinner" spin />
                  <span v-else>{{ t('invite.declineInvite') }}</span>
                </button>
              </template>
              <p v-else class="not-invitee-text">{{ t('invite.notYourInvite') }}</p>
            </div>

            <p v-if="actionError" class="error-text">{{ actionError }}</p>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useInviteByToken, useAcceptInvite, useDeclineInvite } from '@/composables/useInvites'
import { useAuthStore } from '@/stores/auth.store'
import type { UUID } from '@/types'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const token = route.params.token as string as UUID

const authStore = useAuthStore()
const currentUser = computed(() => authStore.currentUser)

const { invite, loading } = useInviteByToken(token)
const { acceptInvite, loading: acceptLoading } = useAcceptInvite()
const { declineInvite, loading: declineLoading } = useDeclineInvite()

const actionError = ref('')

const isInvitee = computed(() =>
  !!currentUser.value && !!invite.value && currentUser.value.id === invite.value.invitee.id
)

function formatStatus(status: string) {
  const map: Record<string, string> = {
    ACCEPTED: t('common.accepted'),
    DECLINED: t('common.declined'),
    REVOKED: t('common.revoked'),
    EXPIRED: t('common.expired'),
  }
  return map[status] ?? status
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function handleAccept() {
  actionError.value = ''
  const result = await acceptInvite(token)
  if (result.success) {
    router.push(`/r/${invite.value!.room.id}`)
  } else {
    actionError.value = t('invite.acceptFailed')
  }
}

async function handleDecline() {
  actionError.value = ''
  const result = await declineInvite(token)
  if (result.success) {
    router.push('/')
  } else {
    actionError.value = t('invite.declineFailed')
  }
}
</script>

<style scoped>
@import '@/assets/styles/form-layout.css';
@import '@/assets/styles/form-styles.css';
@import '@/assets/styles/form-errors.css';


.status-message {
  text-align: center;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.status-message h2 {
  margin: 0;
}

.status-message p {
  color: var(--text-light);
  margin: 0;
}

.status-message svg {
  color: var(--text-light);
}

.status-message.error svg {
  color: var(--error-color, #ef4444);
}

.invite-card {
  text-align: center;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.invite-icon svg {
  color: var(--primary-color);
}

.invite-card h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-light);
}

.room-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.invite-details {
  width: 100%;
  max-width: 320px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  background-color: var(--bg-secondary);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.detail-row .label {
  color: var(--text-light);
}

.detail-row .value {
  font-weight: 600;
  color: var(--text-color);
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  max-width: 320px;
}

.submit-btn.secondary {
  background-color: var(--bg-light);
  color: var(--text-color);
}

.status-badge {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background-color: var(--bg-light);
}

.status-badge.accepted { color: var(--success-color, #10b981); }
.status-badge.declined { color: var(--error-color, #ef4444); }
.status-badge.revoked  { color: var(--error-color, #ef4444); }

.error-text {
  color: var(--error-color, #ef4444);
  font-size: 0.875rem;
  margin: 0;
}

.not-invitee-text {
  font-size: 0.875rem;
  color: var(--text-light);
  margin: 0;
}
</style>
