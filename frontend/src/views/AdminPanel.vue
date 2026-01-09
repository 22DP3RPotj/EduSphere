<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>
        <font-awesome-icon icon="shield-alt" />
        Admin Panel
      </h1>
      <p class="admin-subtitle">Manage users and review reports</p>
    </div>

    <!-- Tab Navigation -->
    <div class="admin-tabs">
      <button
        :class="['tab-button', { active: activeTab === 'users' }]"
        @click="activeTab = 'users'"
      >
        <font-awesome-icon icon="users" />
        User Management
      </button>
      <button
        :class="['tab-button', { active: activeTab === 'reports' }]"
        @click="activeTab = 'reports'"
      >
        <font-awesome-icon icon="flag" />
        Reports
        <span v-if="pendingReportsCount > 0" class="badge-count">{{ pendingReportsCount }}</span>
      </button>
    </div>

    <!-- User Management Tab -->
    <div v-show="activeTab === 'users'" class="admin-section">
      <div class="section-controls">
        <div class="search-container">
          <font-awesome-icon icon="search" class="search-icon" />
          <input
            v-model="userSearch.query"
            type="text"
            placeholder="Search users by name or username..."
            class="search-input"
            @keyup.enter="onUserSearch"
          />
          <button class="search-button" @click="onUserSearch">
            Search
          </button>
        </div>
        
        <!-- Bulk Actions Dropdown -->
        <div v-if="selectedUsers.length > 0" class="bulk-actions">
          <span class="selected-count">{{ selectedUsers.length }} selected</span>
          <div class="bulk-action-controls">
            <select v-model="selectedBulkAction" class="action-select">
              <option :value="null">Select an action...</option>
              <option value="promote">Promote to Staff</option>
              <option value="demote">Remove Staff</option>
              <option value="terminate">Terminate</option>
              <option value="activate">Activate</option>
            </select>
            <button 
              class="btn-apply-action" 
              :disabled="!selectedBulkAction"
              @click="applyBulkAction"
            >
              Apply
            </button>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="usersError" class="error-banner">
        <font-awesome-icon icon="exclamation-triangle" />
        <div class="error-content">
          <p>Failed to load users: {{ usersError.message }}</p>
          <button class="btn-retry" @click="() => refetchUsersComposable()">Retry</button>
        </div>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th class="col-checkbox">
                <input
                  type="checkbox"
                  :checked="allUsersSelected"
                  @change="toggleAllUsers"
                />
              </th>
              <th class="col-user" @click="sortBy('username')">
                Username
                <font-awesome-icon
                  v-if="userSort.column === 'username'"
                  :icon="userSort.direction === 'asc' ? 'sort-up' : 'sort-down'"
                  class="sort-icon"
                />
              </th>
              <th class="col-name" @click="sortBy('name')">
                Name
                <font-awesome-icon
                  v-if="userSort.column === 'name'"
                  :icon="userSort.direction === 'asc' ? 'sort-up' : 'sort-down'"
                  class="sort-icon"
                />
              </th>
              <th class="col-date" @click="sortBy('dateJoined')">
                Joined
                <font-awesome-icon
                  v-if="userSort.column === 'dateJoined'"
                  :icon="userSort.direction === 'asc' ? 'sort-up' : 'sort-down'"
                  class="sort-icon"
                />
              </th>
              <th class="col-role" @click="sortBy('isStaff')">
                Role
                <font-awesome-icon
                  v-if="userSort.column === 'isStaff'"
                  :icon="userSort.direction === 'asc' ? 'sort-up' : 'sort-down'"
                  class="sort-icon"
                />
              </th>
              <th class="col-status" @click="sortBy('isActive')">
                Status
                <font-awesome-icon
                  v-if="userSort.column === 'isActive'"
                  :icon="userSort.direction === 'asc' ? 'sort-up' : 'sort-down'"
                  class="sort-icon"
                />
              </th>
              <th class="col-actions"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in sortedUsers" :key="user.id" :class="{ inactive: !user.isActive }">
              <td class="col-checkbox">
                <input
                  type="checkbox"
                  :checked="selectedUsers.includes(user.id)"
                  :disabled="user.isSuperuser"
                  @change="toggleUserSelection(user.id)"
                />
              </td>
              <td class="col-user">
                <div class="user-info">
                  <img
                    :src="buildAvatarUrl(user.avatar)"
                    :alt="user.username"
                    class="user-avatar"
                  />
                  <span class="username">{{ user.username }}</span>
                </div>
              </td>
              <td class="col-name">{{ user.name }}</td>
              <td class="col-date">{{ formatDate(user.dateJoined) }}</td>
              <td class="col-role">
                <span v-if="user.isSuperuser" class="badge badge-superuser">Superuser</span>
                <span v-else-if="user.isStaff" class="badge badge-staff">Staff</span>
                <span v-else class="badge badge-user">User</span>
              </td>
              <td class="col-status">
                <span :class="['status-badge', user.isActive ? 'active' : 'inactive']">
                  {{ user.isActive ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="col-actions">
                <div v-if="!user.isSuperuser" class="dropdown">
                  <button class="btn-icon-action" @click.stop="toggleUserActions(user.id)">
                    <font-awesome-icon icon="ellipsis-vertical" />
                  </button>
                  <div v-if="activeUserActions === user.id" class="dropdown-menu">
                    <button
                      v-if="!user.isStaff"
                      class="dropdown-item"
                      @click="promoteUser(user.id)"
                    >
                      <font-awesome-icon icon="user-shield" />
                      Promote to Staff
                    </button>
                    <button
                      v-if="user.isStaff"
                      class="dropdown-item"
                      @click="demoteUser(user.id)"
                    >
                      <font-awesome-icon icon="user-minus" />
                      Remove Staff
                    </button>
                    <button
                      v-if="user.isActive"
                      class="dropdown-item"
                      @click="terminateUser(user.id)"
                    >
                      <font-awesome-icon icon="ban" />
                      Terminate User
                    </button>
                    <button
                      v-if="!user.isActive"
                      class="dropdown-item"
                      @click="activateUser(user.id)"
                    >
                      <font-awesome-icon icon="check-circle" />
                      Activate User
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Loading State -->
        <div v-if="loadingUsers" class="loading-state">
          <div class="spinner"></div>
          <p>Loading users...</p>
        </div>

        <div v-else-if="sortedUsers.length === 0" class="no-results">
          <font-awesome-icon icon="users-slash" size="2x" />
          <p>No users found</p>
        </div>
      </div>
    </div>

    <!-- Reports Tab -->
    <div v-show="activeTab === 'reports'" class="admin-section">
      <div class="section-controls">
        <div class="filters-row">
          <div class="filter-group">
            <label for="status-filter">Status</label>
            <select id="status-filter" v-model="reportFiltersUI.status" class="filter-select">
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="reason-filter">Reason</label>
            <select id="reason-filter" v-model="reportFiltersUI.reason" class="filter-select">
              <option value="">All Reasons</option>
              <option value="SPAM">Spam</option>
              <option value="HARASSMENT">Harassment</option>
              <option value="INAPPROPRIATE_CONTENT">Inappropriate Content</option>
              <option value="HATE_SPEECH">Hate Speech</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="user-filter">Reporter</label>
            <input
              id="user-filter"
              v-model="reportFiltersUI.user"
              type="text"
              placeholder="Filter by reporter..."
              class="filter-input"
            />
          </div>
          <button class="apply-filters-btn" @click="applyReportFilters">
            Apply Filters
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="reportsError" class="error-banner">
        <font-awesome-icon icon="exclamation-triangle" />
        <div class="error-content">
          <p>Failed to load reports: {{ reportsError.message }}</p>
          <button class="btn-retry" @click="() => refetchReportsComposable()">Retry</button>
        </div>
      </div>

      <!-- Reports List -->
      <div class="reports-list">
        <!-- Loading State -->
        <div v-if="loadingReports" class="loading-state">
          <div class="spinner"></div>
          <p>Loading reports...</p>
        </div>

        <div v-else>
          <div v-for="report in sortedReports" :key="report.id" class="report-card">
            <div class="report-header">
              <div class="report-meta">
                <span class="report-id">Report #{{ report.id.slice(0, 8) }}</span>
                <span :class="['report-status-badge', `status-${report.status.toLowerCase()}`]">
                  {{ formatStatus(report.status) }}
                </span>
                <span class="report-reason-badge">{{ formatReason(report.reason) }}</span>
              </div>
              <div class="report-actions-header">
                <div class="report-date">{{ formatDate(report.created_at) }}</div>
                <div class="dropdown">
                  <button class="btn-icon-action" @click.stop="toggleReportActions(report.id)">
                    <font-awesome-icon icon="ellipsis-vertical" />
                  </button>
                  <div v-if="activeReportActions === report.id" class="dropdown-menu">
                    <button
                      v-if="report.status !== 'UNDER_REVIEW'"
                      class="dropdown-item"
                      @click="updateReportStatus(report.id, 'UNDER_REVIEW')"
                    >
                      <font-awesome-icon icon="eye" />
                      Mark Under Review
                    </button>
                    <button
                      v-if="report.status !== 'RESOLVED'"
                      class="dropdown-item"
                      @click="updateReportStatus(report.id, 'RESOLVED')"
                    >
                      <font-awesome-icon icon="check" />
                      Resolve
                    </button>
                    <button
                      v-if="report.status !== 'DISMISSED'"
                      class="dropdown-item"
                      @click="updateReportStatus(report.id, 'DISMISSED')"
                    >
                      <font-awesome-icon icon="times" />
                      Dismiss
                    </button>
                    <button class="dropdown-item" @click="showModeratorNoteModal(report)">
                      <font-awesome-icon icon="note-sticky" />
                      Add Moderator Note
                    </button>
                    <button class="dropdown-item delete-action" @click="confirmDeleteReport(report.id)">
                      <font-awesome-icon icon="trash" />
                      Delete Report
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="report-body">
              <div class="report-info">
                <div class="info-row">
                  <span class="info-label">Reporter:</span>
                  <span class="info-value">
                    {{ report.user ? report.user.username : 'Deleted User' }}
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-label">Room:</span>
                  <span class="info-value">
                    {{ report.room.name }} (by @{{ report.room.host.username }})
                  </span>
                </div>
              </div>
              <div class="report-description">
                <strong>Description:</strong>
                <p>{{ report.body }}</p>
              </div>
              <div v-if="report.moderatorNote" class="moderator-note">
                <strong>Moderator Note:</strong>
                <p>{{ report.moderatorNote }}</p>
                <span class="moderator-info">
                  - {{ report.moderator?.username }} on {{ formatDate(report.updated_at) }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="sortedReports.length === 0" class="no-results">
            <font-awesome-icon icon="inbox" size="2x" />
            <p>No reports found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Moderator Note Modal -->
    <div v-if="moderatorNoteModal.isOpen" class="modal-overlay" @click="closeModeratorNoteModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add Moderator Note</h3>
          <button class="modal-close" @click="closeModeratorNoteModal">
            <font-awesome-icon icon="times" />
          </button>
        </div>
        <div class="modal-body">
          <label for="moderator-note">Moderator Note</label>
          <textarea
            id="moderator-note"
            v-model="moderatorNoteModal.input"
            placeholder="Add a moderator note..."
            rows="4"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModeratorNoteModal">Cancel</button>
          <button class="btn-confirm" @click="confirmAddModeratorNote">Add Note</button>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      v-if="confirmationModal.isOpen"
      :is-visible="confirmationModal.isOpen"
      :title="confirmationModal.title"
      :message="confirmationModal.message"
      confirm-text="Confirm"
      cancel-text="Cancel"
      @confirm="executeConfirmedAction"
      @cancel="closeConfirmationModal"
      @close="closeConfirmationModal"
    />
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import {
  useAdminUsers,
  useAdminReports,
  useUpdateUserStaffStatus,
  useUpdateUserActiveStatus,
  useUpdateReport,
  useDeleteReport,
} from '@/composables/useAdmin';
import { buildAvatarUrl } from '@/utils/media';
import ConfirmationModal from '@/components/layout/ConfirmationModal.vue';
import type { Report, User } from '@/types';

// Role importance for sorting (higher = more important)
const ROLE_IMPORTANCE = {
  superuser: 3,
  staff: 2,
  user: 1,
} as const;

function getUserRoleImportance(user: User): number {
  if (user.isSuperuser) return ROLE_IMPORTANCE.superuser;
  if (user.isStaff) return ROLE_IMPORTANCE.staff;
  return ROLE_IMPORTANCE.user;
}

// Tab state
const activeTab = ref<'users' | 'reports'>('users');

// User Management State
const userSearch = ref({
  query: '',
  filter: '',
});
const userSort = ref<{
  column: 'username' | 'name' | 'dateJoined' | 'isStaff' | 'isActive';
  direction: 'asc' | 'desc';
}>({
  column: 'dateJoined',
  direction: 'desc',
});
const selectedUsers = ref<string[]>([]);
const activeUserActions = ref<string | null>(null);
const selectedBulkAction = ref<'promote' | 'demote' | 'terminate' | 'activate' | null>(null);

// Report Management State
const reportFiltersUI = ref({
  status: '',
  reason: '',
  user: '',
});
const reportFiltersApplied = ref({
  status: '',
  reason: '',
  user: '',
});
const moderatorNoteModal = ref({
  isOpen: false,
  report: null as Report | null,
  input: '',
});
const activeReportActions = ref<string | null>(null);

// Confirmation Modal State
const confirmationModal = ref({
  isOpen: false,
  title: '',
  message: '',
  action: null as (() => Promise<void>) | null,
});

// Composables
const { users, loading: loadingUsers, error: usersError, refetch: refetchUsersComposable } = useAdminUsers(computed(() => userSearch.value.filter));
const { reports, loading: loadingReports, error: reportsError, refetch: refetchReportsComposable } = useAdminReports(computed(() => reportFiltersApplied.value.status), computed(() => reportFiltersApplied.value.reason));

const { updateStaffStatus } = useUpdateUserStaffStatus();
const { updateActiveStatus } = useUpdateUserActiveStatus();
const { updateReport } = useUpdateReport();
const { deleteReport } = useDeleteReport();

// Computed
const pendingReportsCount = computed(() => {
  return reports.value.filter((r) => r.status === 'PENDING' || r.status === 'UNDER_REVIEW').length;
});

const allUsersSelected = computed(() => {
  const selectableUsers = users.value.filter((u) => !u.isSuperuser);
  return selectableUsers.length > 0 && selectedUsers.value.length === selectableUsers.length;
});

const sortedUsers = computed(() => {
  const sorted = [...users.value].sort((a, b) => {
    const aValue = a[userSort.value.column as keyof typeof a];
    const bValue = b[userSort.value.column as keyof typeof b];

    let aVal: number | string | boolean;
    let bVal: number | string | boolean;

    if (userSort.value.column === 'dateJoined') {
      aVal = new Date(String(aValue)).getTime();
      bVal = new Date(String(bValue)).getTime();
    } else if (userSort.value.column === 'isStaff') {
      // Sort by role importance using the mapping
      aVal = getUserRoleImportance(a);
      bVal = getUserRoleImportance(b);
    } else if (userSort.value.column === 'isActive') {
      aVal = Boolean(aValue);
      bVal = Boolean(bValue);
    } else {
      aVal = String(aValue).toLowerCase();
      bVal = String(bValue).toLowerCase();
    }

    if (userSort.value.direction === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  return sorted;
});

const sortedReports = computed(() => {
  return [...reports.value].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});

// Methods
function onUserSearch() {
  userSearch.value.filter = userSearch.value.query;
  refetchUsersComposable();
}

function applyReportFilters() {
  reportFiltersApplied.value = { ...reportFiltersUI.value };
  refetchReportsComposable();
}

function toggleUserSelection(userId: string) {
  const index = selectedUsers.value.indexOf(userId);
  if (index > -1) {
    selectedUsers.value.splice(index, 1);
  } else {
    selectedUsers.value.push(userId);
  }
  activeUserActions.value = null;
}

function toggleAllUsers() {
  if (allUsersSelected.value) {
    selectedUsers.value = [];
  } else {
    selectedUsers.value = users.value.filter((u) => !u.isSuperuser).map((u) => u.id);
  }
  activeUserActions.value = null;
}

function sortBy(column: 'username' | 'name' | 'dateJoined' | 'isStaff' | 'isActive') {
  if (userSort.value.column === column) {
    userSort.value.direction = userSort.value.direction === 'asc' ? 'desc' : 'asc';
  } else {
    userSort.value.column = column;
    userSort.value.direction = 'asc';
  }
}

function toggleUserActions(userId: string) {
  activeUserActions.value = activeUserActions.value === userId ? null : userId;
}

function toggleReportActions(reportId: string) {
  activeReportActions.value = activeReportActions.value === reportId ? null : reportId;
}

function showConfirmation(title: string, message: string, action: () => Promise<void>) {
  confirmationModal.value.title = title;
  confirmationModal.value.message = message;
  confirmationModal.value.action = action;
  confirmationModal.value.isOpen = true;
}

function closeConfirmationModal() {
  confirmationModal.value.isOpen = false;
  confirmationModal.value.action = null;
}

async function executeConfirmedAction() {
  if (confirmationModal.value.action) {
    try {
      await confirmationModal.value.action();
    } catch (error) {
      console.error('Action failed:', error);
    }
  }
  closeConfirmationModal();
}

// User Actions
async function promoteUser(userId: string) {
  activeUserActions.value = null;
  showConfirmation(
    'Promote User',
    'Are you sure you want to promote this user to staff?',
    async () => {
      try {
        await updateStaffStatus([userId], true);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to promote user:', error);
        throw error;
      }
    }
  );
}

async function demoteUser(userId: string) {
  activeUserActions.value = null;
  showConfirmation(
    'Remove Staff Role',
    'Are you sure you want to remove staff role from this user?',
    async () => {
      try {
        await updateStaffStatus([userId], false);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to demote user:', error);
        throw error;
      }
    }
  );
}

async function terminateUser(userId: string) {
  activeUserActions.value = null;
  showConfirmation(
    'Terminate User',
    'Are you sure you want to terminate this user? They will not be able to access the platform.',
    async () => {
      try {
        await updateActiveStatus([userId], false);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to terminate user:', error);
        throw error;
      }
    }
  );
}

async function activateUser(userId: string) {
  activeUserActions.value = null;
  try {
    await updateActiveStatus([userId], true);
    await refetchUsersComposable();
    selectedUsers.value = [];
  } catch (error) {
    console.error('Failed to activate user:', error);
  }
}

// Bulk Actions
function applyBulkAction() {
  switch (selectedBulkAction.value) {
    case 'promote':
      bulkPromoteUsers();
      break;
    case 'demote':
      bulkDemoteUsers();
      break;
    case 'terminate':
      bulkTerminateUsers();
      break;
    case 'activate':
      bulkActivateUsers();
      break;
  }
  selectedBulkAction.value = null;
}

async function bulkPromoteUsers() {
  showConfirmation(
    'Promote Users',
    `Are you sure you want to promote ${selectedUsers.value.length} users to staff?`,
    async () => {
      try {
        await updateStaffStatus(selectedUsers.value, true);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to promote users:', error);
        throw error;
      }
    }
  );
}

async function bulkDemoteUsers() {
  showConfirmation(
    'Remove Staff Role',
    `Are you sure you want to remove staff role from ${selectedUsers.value.length} users?`,
    async () => {
      try {
        await updateStaffStatus(selectedUsers.value, false);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to demote users:', error);
        throw error;
      }
    }
  );
}

async function bulkTerminateUsers() {
  showConfirmation(
    'Terminate Users',
    `Are you sure you want to terminate ${selectedUsers.value.length} users? They will not be able to access the platform.`,
    async () => {
      try {
        await updateActiveStatus(selectedUsers.value, false);
        await refetchUsersComposable();
        selectedUsers.value = [];
      } catch (error) {
        console.error('Failed to terminate users:', error);
        throw error;
      }
    }
  );
}

async function bulkActivateUsers() {
  try {
    await updateActiveStatus(selectedUsers.value, true);
    await refetchUsersComposable();
    selectedUsers.value = [];
  } catch (error) {
    console.error('Failed to activate users:', error);
  }
}

// Report Actions
async function updateReportStatus(reportId: string, status: string) {
  activeReportActions.value = null;
  try {
    await updateReport(reportId, status);
    await refetchReportsComposable();
  } catch (error) {
    console.error('Failed to update report status:', error);
  }
}

function showModeratorNoteModal(report: Report) {
  activeReportActions.value = null;
  moderatorNoteModal.value.report = report;
  moderatorNoteModal.value.input = report.moderatorNote || '';
  moderatorNoteModal.value.isOpen = true;
}

function closeModeratorNoteModal() {
  moderatorNoteModal.value.isOpen = false;
  moderatorNoteModal.value.report = null;
  moderatorNoteModal.value.input = '';
}

async function confirmAddModeratorNote() {
  if (!moderatorNoteModal.value.report) return;

  try {
    await updateReport(moderatorNoteModal.value.report.id, undefined, moderatorNoteModal.value.input);
    await refetchReportsComposable();
    closeModeratorNoteModal();
  } catch (error) {
    console.error('Failed to add moderator note:', error);
  }
}

async function confirmDeleteReport(reportId: string) {
  activeReportActions.value = null;
  showConfirmation(
    'Delete Report',
    'Are you sure you want to permanently delete this report?',
    async () => {
      try {
        await deleteReport(reportId);
        await refetchReportsComposable();
      } catch (error) {
        console.error('Failed to delete report:', error);
        throw error;
      }
    }
  );
}

function formatDate(dateString: string | undefined) {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatStatus(status: string) {
  return status
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
}

function formatReason(reason: string) {
  return reason
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
}

// Close dropdowns when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (!(event.target as Element).closest('.dropdown')) {
    activeUserActions.value = null;
    activeReportActions.value = null;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--bg-color);
  min-height: auto;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-header h1 {
  font-size: 2rem;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 0.5rem 0;
}

.admin-subtitle {
  color: var(--text-light);
  font-size: 1rem;
  margin: 0;
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border-color);
}

.tab-button {
  position: relative;
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  color: var(--text-light);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}

.tab-button:hover {
  color: var(--text-color);
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.badge-count {
  background-color: var(--error-color);
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Section */
.admin-section {
  background-color: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
}

/* Controls */
.section-controls {
  margin-bottom: 1.5rem;
}

.search-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
  z-index: 2;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 1rem;
  transition: var(--transition);
  color: var(--text-color);
  background-color: var(--bg-color);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.search-button:hover {
  background-color: var(--primary-hover);
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--bg-color);
  border-radius: var(--radius);
}

.selected-count {
  font-weight: 600;
  color: var(--primary-color);
}

.bulk-action-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-select {
  padding: 0.75rem 1rem;
  background-color: var(--white);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 0.9rem;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
}

.action-select:hover {
  border-color: var(--primary-color);
  background-color: var(--white);
}

.action-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.btn-apply-action {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-apply-action:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-apply-action:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Dropdown Styles */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: var(--text-color);
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.dropdown-toggle:hover {
  background-color: var(--bg-color);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  min-width: 200px;
  margin-top: 0.25rem;
  animation: fadeIn 0.15s ease-out;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  font-size: 0.9rem;
  text-align: left;
  transition: var(--transition);
}

.dropdown-item:hover {
  background-color: var(--bg-color);
}

.dropdown-item:first-child {
  border-radius: var(--radius) var(--radius) 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 var(--radius) var(--radius);
}

.dropdown-item.delete-action {
  color: var(--error-color);
}

.dropdown-item.delete-action:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Filters */
.filters-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
  height: 1.5rem;
}

.filter-select, .filter-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--white);
  transition: var(--transition);
  height: 2.5rem;
  box-sizing: border-box;
}

.filter-select:focus, .filter-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.apply-filters-btn {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  height: 2.5rem;
  display: flex;
  margin-top: auto;
  align-items: center;
  justify-content: center;
}

.apply-filters-btn:hover {
  background-color: var(--primary-hover);
}

/* Error Banner */
.error-banner {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: var(--radius);
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.error-banner svg {
  margin-top: 0.125rem;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
  display: flex;
  justify-content: between;
  align-items: center;
  gap: 1rem;
}

.error-content p {
  margin: 0;
  flex: 1;
}

.btn-retry {
  padding: 0.5rem 1rem;
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}

.btn-retry:hover {
  background-color: #b91c1c;
}

/* Table */
.table-container {
  position: relative;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table thead {
  background-color: var(--bg-color);
  border-bottom: 2px solid var(--border-color);
}

.admin-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.admin-table th:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.sort-icon {
  margin-left: 0.5rem;
  color: var(--primary-color);
}

.admin-table tbody tr {
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition);
}

.admin-table tbody tr:hover {
  background-color: var(--bg-color);
}

/* .admin-table tbody tr.inactive .user-info {
  opacity: 0.6;
} */

.admin-table td {
  padding: 1rem;
}

.col-checkbox {
  width: 50px;
  text-align: center !important;
}

.col-user {
  min-width: 200px;
}

.col-name {
  min-width: 150px;
}

.col-date {
  min-width: 120px;
}

.col-role, .col-status {
  min-width: 100px;
}

.col-actions {
  width: 60px;
  text-align: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  font-weight: 500;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-superuser {
  background-color: #8b5cf6;
  color: white;
}

.badge-staff {
  background-color: #10b981;
  color: white;
}

.badge-user {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background-color: #fef2f2;
  color: #dc2626;
}

.btn-icon-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  background-color: transparent;
  color: var(--text-light);
}

.btn-icon-action:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* Reports */
.reports-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  min-height: 200px;
}

.report-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1.5rem;
  transition: var(--transition);
}

.report-card:hover {
  box-shadow: var(--shadow);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.report-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.report-id {
  font-family: monospace;
  font-size: 0.875rem;
  color: var(--text-light);
}

.report-status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.status-under_review {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-resolved {
  background-color: #d1fae5;
  color: #065f46;
}

.status-dismissed {
  background-color: #f3f4f6;
  color: #6b7280;
}

.report-reason-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.report-actions-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.report-date {
  font-size: 0.875rem;
  color: var(--text-light);
  white-space: nowrap;
}

.report-body {
  margin-bottom: 1rem;
}

.report-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.info-row {
  display: flex;
  gap: 0.5rem;
}

.info-label {
  font-weight: 600;
  color: var(--text-light);
}

.info-value {
  color: var(--text-color);
}

.report-description {
  margin-bottom: 1rem;
}

.report-description p,
.moderator-note p {
  margin: 0.5rem 0;
  color: var(--text-color);
  line-height: 1.6;
}

.moderator-note {
  padding: 1rem;
  background-color: var(--bg-color);
  border-left: 3px solid var(--primary-color);
  border-radius: var(--radius);
}

.moderator-info {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-light);
  font-style: italic;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: var(--white);
  border-radius: var(--radius);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  color: var(--text-light);
  transition: var(--transition);
}

.modal-close:hover {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.modal-body label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.modal-body textarea {
  width: 100%;
  padding: 0.75rem;
  box-sizing: border-box;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: var(--transition);
  color: var(--text-color);
  background-color: var(--white);
  line-height: 1.5;
  min-height: 120px;
}

.modal-body textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
  background-color: var(--white);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background-color: var(--white);
  color: var(--text-color);
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-cancel:hover {
  background-color: var(--bg-color);
}

.btn-confirm {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #10b981;
  color: white;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-confirm:hover {
  background-color: #059669;
}

/* Loading & Error States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-light);
}

.no-results svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-container {
    padding: 1rem;
  }

  .admin-header h1 {
    font-size: 1.5rem;
  }

  .search-container {
    flex-direction: column;
  }

  .filters-row {
    flex-direction: column;
  }

  .filter-group {
    min-width: 100%;
  }

  .bulk-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-table {
    font-size: 0.875rem;
  }

  .admin-table th,
  .admin-table td {
    padding: 0.5rem;
  }

  .user-avatar {
    width: 28px;
    height: 28px;
  }

  .report-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .report-actions-header {
    width: 100%;
    justify-content: space-between;
  }
}
</style>