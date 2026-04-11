<template>
  <div class="invites-page">
    <div class="page-header">
      <button class="back-button" @click="$router.back()">
        <font-awesome-icon icon="arrow-left" />
      </button>
      <h1>{{ t('invite.invites') }}</h1>
    </div>

    <!-- Tabs -->
    <div class="invites-tabs">
      <div
        class="tab"
        :class="{ active: activeTab === 'received' }"
        @click="activeTab = 'received'"
      >
        {{ t('invite.receivedInvites') }}
        <span v-if="receivedInvites.length" class="badge">{{ receivedInvites.length }}</span>
      </div>
      <div
        class="tab"
        :class="{ active: activeTab === 'sent' }"
        @click="activeTab = 'sent'"
      >
        {{ t('invite.sentInvites') }}
      </div>
    </div>

    <!-- Received Invites -->
    <div v-if="activeTab === 'received'" class="tab-content">
      <div class="filters-row">
        <div class="filter-group">
          <label for="received-status-filter">Status</label>
          <select id="received-status-filter" v-model="receivedStatusFilter" class="filter-select">
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="DECLINED">Declined</option>
            <option value="EXPIRED">Expired</option>
            <option value="REVOKED">Revoked</option>
          </select>
        </div>
      </div>

      <div v-if="receivedLoading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ t('common.loading') }}</p>
      </div>

      <div v-else-if="filteredReceivedInvites.length === 0" class="empty-state">
        <font-awesome-icon icon="envelope-open" size="2x" />
        <p>{{ t('invite.noReceivedInvites') }}</p>
      </div>

      <div v-else class="invites-list">
        <div v-for="invite in filteredReceivedInvites" :key="invite.id" class="invite-card">
          <div class="invite-info">
            <div class="invite-room">
              <font-awesome-icon icon="door-open" class="icon" />
              <span class="room-name">{{ invite.room.name }}</span>
            </div>
            <div class="invite-meta">
              <span class="invited-by">{{ t('invite.invitedBy') }}: <strong>{{ invite.inviter.name || invite.inviter.username }}</strong></span>
              <span v-if="invite.role" class="invite-role">{{ invite.role.name }}</span>
              <span class="invite-status" :class="invite.status.toLowerCase()">{{ invite.status }}</span>
            </div>
            <div class="invite-dates">
              <span>{{ formatDate(invite.createdAt) }}</span>
              <span v-if="invite.expiresAt" class="expires">
                {{ t('invite.inviteExpires') }}: {{ formatDate(invite.expiresAt) }}
              </span>
            </div>
          </div>
          <div v-if="invite.status === 'PENDING'" class="invite-actions">
            <button
              class="btn btn-success"
              :disabled="acceptLoading"
              @click="handleAccept(invite.token)"
            >
              <font-awesome-icon v-if="acceptLoading" icon="spinner" spin />
              {{ t('invite.acceptInvite') }}
            </button>
            <button
              class="btn btn-danger"
              :disabled="declineLoading"
              @click="handleDecline(invite.token)"
            >
              {{ t('invite.declineInvite') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Sent Invites -->
    <div v-if="activeTab === 'sent'" class="tab-content">
      <div class="filters-row">
        <div class="filter-group">
          <label for="sent-status-filter">Status</label>
          <select id="sent-status-filter" v-model="sentStatusFilter" class="filter-select">
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="DECLINED">Declined</option>
            <option value="EXPIRED">Expired</option>
            <option value="REVOKED">Revoked</option>
          </select>
        </div>
      </div>

      <div v-if="sentLoading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ t('common.loading') }}</p>
      </div>

      <div v-else-if="filteredSentInvites.length === 0" class="empty-state">
        <font-awesome-icon icon="paper-plane" size="2x" />
        <p>{{ t('invite.noSentInvites') }}</p>
      </div>

      <div v-else class="invites-list">
        <div v-for="invite in filteredSentInvites" :key="invite.id" class="invite-card">
          <div class="invite-info">
            <div class="invite-room">
              <font-awesome-icon icon="door-open" class="icon" />
              <span class="room-name">{{ invite.room.name }}</span>
            </div>
            <div class="invite-meta">
              <span class="invited-to">{{ t('invite.invitedTo') }}: <strong>{{ invite.invitee.name || invite.invitee.username }}</strong></span>
              <span v-if="invite.role" class="invite-role">{{ invite.role.name }}</span>
              <span class="invite-status" :class="invite.status.toLowerCase()">{{ invite.status }}</span>
            </div>
            <div class="invite-dates">
              <span>{{ formatDate(invite.createdAt) }}</span>
              <span v-if="invite.expiresAt" class="expires">
                {{ t('invite.inviteExpires') }}: {{ formatDate(invite.expiresAt) }}
              </span>
            </div>
          </div>
          <div v-if="invite.status === 'PENDING'" class="invite-actions">
            <button
              class="btn btn-secondary"
              :disabled="resendLoading"
              @click="handleResend(invite.token)"
            >
              <font-awesome-icon icon="redo" />
              {{ t('invite.resendInvite') }}
            </button>
            <button
              class="btn btn-danger"
              :disabled="cancelLoading"
              @click="handleCancel(invite.token)"
            >
              {{ t('invite.cancelInvite') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  useReceivedInvites,
  useSentInvites,
  useAcceptInvite,
  useDeclineInvite,
  useCancelInvite,
  useResendInvite,
} from '@/composables/useInvites';
import type { UUID } from '@/types';

const { t } = useI18n();

const activeTab = ref<'received' | 'sent'>('received');
const receivedStatusFilter = ref('');
const sentStatusFilter = ref('');

const { invites: receivedInvites, loading: receivedLoading, refetch: refetchReceived } = useReceivedInvites();
const { invites: sentInvites, loading: sentLoading, refetch: refetchSent } = useSentInvites();
const { acceptInvite, loading: acceptLoading } = useAcceptInvite();
const { declineInvite, loading: declineLoading } = useDeclineInvite();
const { cancelInvite, loading: cancelLoading } = useCancelInvite();
const { resendInvite, loading: resendLoading } = useResendInvite();

const filteredReceivedInvites = computed(() => {
  if (!receivedStatusFilter.value) return receivedInvites.value;
  return receivedInvites.value.filter(i => i.status === receivedStatusFilter.value);
});

const filteredSentInvites = computed(() => {
  if (!sentStatusFilter.value) return sentInvites.value;
  return sentInvites.value.filter(i => i.status === sentStatusFilter.value);
});

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

async function handleAccept(token: UUID) {
  const result = await acceptInvite(token);
  if (result.success) {
    refetchReceived();
  }
}

async function handleDecline(token: UUID) {
  const result = await declineInvite(token);
  if (result.success) {
    refetchReceived();
  }
}

async function handleCancel(token: UUID) {
  const result = await cancelInvite(token);
  if (result.success) {
    refetchSent();
  }
}

async function handleResend(token: UUID) {
  await resendInvite(token);
  refetchSent();
}
</script>

<style scoped>
.invites-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  color: var(--text-color);
}

.back-button {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius);
  transition: var(--transition);
}

.back-button:hover {
  background-color: var(--bg-light);
}

.filters-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: 500;
}

.filter-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--bg-secondary);
  color: var(--text-color);
  font-size: 0.85rem;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.invites-tabs {
  display: flex;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  color: var(--text-light);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab:hover {
  color: var(--text-color);
}

.tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.badge {
  background-color: var(--primary-color);
  color: var(--white);
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-light);
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.invites-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.invite-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.invite-info {
  flex: 1;
  min-width: 0;
}

.invite-room {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.invite-room .icon {
  color: var(--primary-color);
}

.room-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 1.05rem;
}

.invite-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
  color: var(--text-light);
}

.invite-role {
  background-color: var(--bg-light);
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
}

.invite-status {
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.invite-status.pending { background-color: #fef3c7; color: #92400e; }
.invite-status.accepted { background-color: #d1fae5; color: #065f46; }
.invite-status.declined { background-color: #fde2e2; color: #991b1b; }
.invite-status.revoked { background-color: #e5e7eb; color: #4b5563; }
.invite-status.expired { background-color: #e5e7eb; color: #6b7280; }

.invite-dates {
  font-size: 0.8rem;
  color: var(--text-light);
  display: flex;
  gap: 1rem;
}

.expires {
  font-style: italic;
}

.invite-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-secondary {
  background-color: var(--bg-light);
  color: var(--text-color);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--border-color);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 640px) {
  .invite-card {
    flex-direction: column;
  }

  .invite-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
