<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>
        <font-awesome-icon icon="shield-alt" />
        Admin Panel
      </h1>
      <p class="admin-subtitle">Manage users, moderate cases, and review audit logs</p>
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
        :class="['tab-button', { active: activeTab === 'cases' }]"
        @click="activeTab = 'cases'"
      >
        <font-awesome-icon icon="gavel" />
        Cases
        <span v-if="pendingCasesCount > 0" class="badge-count">{{ pendingCasesCount }}</span>
      </button>
      <button
        :class="['tab-button', { active: activeTab === 'audit' }]"
        @click="activeTab = 'audit'"
      >
        <font-awesome-icon icon="clipboard-list" />
        Audit Log
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

    <!-- Cases Tab -->
    <div v-show="activeTab === 'cases'" class="admin-section">
      <div class="section-controls">
        <div class="filters-row">
          <div class="filter-group">
            <label for="case-status-filter">Status</label>
            <select id="case-status-filter" v-model="caseFiltersUI.status" class="filter-select">
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="case-priority-filter">Priority</label>
            <select id="case-priority-filter" v-model="caseFiltersUI.priority" class="filter-select">
              <option value="">All Priorities</option>
              <option value="0">Low</option>
              <option value="1">Medium</option>
              <option value="2">High</option>
            </select>
          </div>
          <button class="apply-filters-btn" @click="applyCaseFilters">
            Apply Filters
          </button>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="casesError" class="error-banner">
        <font-awesome-icon icon="exclamation-triangle" />
        <div class="error-content">
          <p>Failed to load cases: {{ casesError.message }}</p>
          <button class="btn-retry" @click="() => refetchCasesComposable()">Retry</button>
        </div>
      </div>

      <!-- Cases List -->
      <div class="cases-list">
        <div v-if="loadingCases" class="loading-state">
          <div class="spinner"></div>
          <p>Loading cases...</p>
        </div>

        <div v-else>
          <div v-for="mc in sortedCases" :key="mc.id" class="case-card">
            <div class="case-header">
              <div class="case-meta">
                <span class="case-id">Case #{{ mc.id.slice(0, 8) }}</span>
                <span :class="['case-status-badge', `status-${mc.status.toLowerCase()}`]">
                  {{ formatStatus(mc.status) }}
                </span>
                <span :class="['case-priority-badge', `priority-${priorityLabel(mc.priority).toLowerCase()}`]">
                  {{ priorityLabel(mc.priority) }}
                </span>
              </div>
              <div class="case-actions-header">
                <div class="case-date">{{ formatDate(mc.createdAt) }}</div>
                <div class="dropdown">
                  <button class="btn-icon-action" @click.stop="toggleCaseActions(mc.id)">
                    <font-awesome-icon icon="ellipsis-vertical" />
                  </button>
                  <div v-if="activeCaseActions === mc.id" class="dropdown-menu">
                    <button
                      v-if="mc.status === 'PENDING'"
                      class="dropdown-item"
                      @click="startReviewCase(mc.id)"
                    >
                      <font-awesome-icon icon="eye" />
                      Start Review
                    </button>
                    <button class="dropdown-item" @click="openCaseActionModal(mc)">
                      <font-awesome-icon icon="gavel" />
                      Take Action
                    </button>
                    <button class="dropdown-item" @click="openPriorityModal(mc)">
                      <font-awesome-icon icon="flag" />
                      Set Priority
                    </button>
                    <button
                      v-if="mc.status === 'RESOLVED' || mc.status === 'DISMISSED'"
                      class="dropdown-item"
                      @click="handleReopenCase(mc.id)"
                    >
                      <font-awesome-icon icon="redo" />
                      Reopen
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="case-body">
              <!-- Linked Reports -->
              <div class="case-reports">
                <h4>Reports ({{ mc.reports.length }})</h4>
                <div v-for="report in mc.reports" :key="report.id" class="case-report-item">
                  <span class="report-reason-badge">{{ report.reason.label }}</span>
                  <span class="report-reporter">by {{ report.reporter?.username || 'Unknown' }}</span>
                  <p v-if="report.description" class="report-description-text">{{ report.description }}</p>
                </div>
              </div>

              <!-- Action History -->
              <div v-if="mc.actions.length > 0" class="case-action-history">
                <h4>Actions</h4>
                <div v-for="action in mc.actions" :key="action.id" class="case-action-item">
                  <span :class="['action-type-badge', `action-${action.action.toLowerCase()}`]">
                    {{ formatActionType(action.action) }}
                  </span>
                  <span class="action-moderator">{{ action.moderator?.username || 'System' }}</span>
                  <span class="action-date">{{ formatDate(action.createdAt) }}</span>
                  <p v-if="action.note" class="action-note">{{ action.note }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-if="sortedCases.length === 0" class="no-results">
            <font-awesome-icon icon="inbox" size="2x" />
            <p>No cases found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Audit Log Tab -->
    <div v-show="activeTab === 'audit'" class="admin-section">
      <div class="section-controls">
        <div class="filters-row">
          <div class="filter-group">
            <label for="audit-type-filter">Audit Type</label>
            <select id="audit-type-filter" v-model="auditType" class="filter-select">
              <option value="user">Users</option>
              <option value="userBan">User Bans</option>
              <option value="room">Rooms</option>
              <option value="invite">Invites</option>
              <option value="report">Reports</option>
              <option value="case">Moderation Cases</option>
              <option value="action">Moderation Actions</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="audit-date-from">From</label>
            <input id="audit-date-from" v-model="auditFilters.dateFrom" type="date" class="filter-input" />
          </div>
          <div class="filter-group">
            <label for="audit-date-to">To</label>
            <input id="audit-date-to" v-model="auditFilters.dateTo" type="date" class="filter-input" />
          </div>
          <div class="filter-group">
            <label for="audit-actor">Actor Username</label>
            <input id="audit-actor" v-model="auditFilters.actorUsername" type="text" class="filter-input" placeholder="Filter by actor..." />
          </div>
        </div>
      </div>

      <!-- Audit entries -->
      <div v-if="auditLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading audit log...</p>
      </div>
      <div v-else-if="auditError" class="error-banner">
        <font-awesome-icon icon="exclamation-triangle" />
        <div class="error-content">
          <p>Failed to load audit log: {{ auditError.message }}</p>
        </div>
      </div>
      <div v-else>
        <table class="admin-table audit-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Label</th>
              <th>Object ID</th>
              <th>Actor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in auditEntries" :key="entry.pghId">
              <td>{{ formatDate(entry.pghCreatedAt) }}</td>
              <td><span class="audit-label-badge">{{ entry.pghLabel }}</span></td>
              <td class="audit-obj-id">{{ entry.pghObjId?.slice(0, 8) || '—' }}</td>
              <td>{{ entry.actor?.username || 'System' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="auditEntries.length === 0" class="no-results">
          <font-awesome-icon icon="clipboard-list" size="2x" />
          <p>No audit entries found</p>
        </div>

        <div v-if="auditHasMore" class="load-more-container">
          <button class="btn-load-more" @click="auditLoadMore">
            Load More
          </button>
        </div>
      </div>
    </div>

    <!-- Case Action Modal -->
    <div v-if="caseActionModal.isOpen" class="modal-overlay" @click="closeCaseActionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Take Action on Case</h3>
          <button class="modal-close" @click="closeCaseActionModal">
            <font-awesome-icon icon="times" />
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="case-action-type">Action</label>
            <select id="case-action-type" v-model="caseActionModal.action" class="filter-select">
              <option value="">Select an action...</option>
              <option value="NO_VIOLATION">No Violation</option>
              <option value="CONTENT_REMOVED">Content Removed</option>
              <option value="WARNING">Warning</option>
              <option value="TEMP_BAN">Temporary Ban</option>
              <option value="PERM_BAN">Permanent Ban</option>
            </select>
          </div>
          <div class="form-group">
            <label for="case-action-note">Note (optional)</label>
            <textarea
              id="case-action-note"
              v-model="caseActionModal.note"
              placeholder="Add a note about this action..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCaseActionModal">Cancel</button>
          <button
            class="btn-confirm"
            :disabled="!caseActionModal.action"
            @click="confirmCaseAction"
          >
            Take Action
          </button>
        </div>
      </div>
    </div>

    <!-- Priority Modal -->
    <div v-if="priorityModal.isOpen" class="modal-overlay" @click="closePriorityModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Set Case Priority</h3>
          <button class="modal-close" @click="closePriorityModal">
            <font-awesome-icon icon="times" />
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="priority-select">Priority</label>
            <select id="priority-select" v-model="priorityModal.priority" class="filter-select">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closePriorityModal">Cancel</button>
          <button class="btn-confirm" @click="confirmSetPriority">Set Priority</button>
        </div>
      </div>
    </div>

    <!-- Termination Modal -->
    <div v-if="terminationModal.isOpen" class="modal-overlay" @click="closeTerminationModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Terminate User(s)</h3>
          <button class="modal-close" @click="closeTerminationModal">
            <font-awesome-icon icon="times" />
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="termination-reason">Reason for Termination</label>
            <textarea
              id="termination-reason"
              v-model="terminationModal.reason"
              placeholder="Explain why the user is being terminated..."
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="termination-duration">Duration</label>
             <select id="termination-duration" v-model="terminationModal.duration">
              <option value="permanent">Permanent</option>
              <option value="1h">1 Hour</option>
              <option value="24h">24 Hours</option>
              <option value="7d">7 Days</option>
              <option value="30d">30 Days</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeTerminationModal">Cancel</button>
          <button class="btn-confirm danger" @click="confirmTermination">Terminate</button>
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
  useAdminCases,
  useUpdateUserStaffStatus,
  useUpdateUserActiveStatus,
  useTakeCaseAction,
  useSetCaseUnderReview,
  useSetCasePriority,
  useReopenCase,
} from '@/composables/useAdmin';
import {
  useUserAudits,
  useUserBanAudits,
  useRoomAudits,
  useInviteAudits,
  useReportAudits,
  useModerationCaseAudits,
  useModerationActionAudits,
} from '@/composables/useAudit';
import { buildAvatarUrl } from '@/utils/media';
import ConfirmationModal from '@/components/layout/ConfirmationModal.vue';
import type { ModerationCase, User, UUID } from '@/types';

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
const activeTab = ref<'users' | 'cases' | 'audit'>('users');

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
const selectedBulkAction = ref<'promote' | 'demote' | 'activate' | null>(null);

// Case Management State
const caseFiltersUI = ref({ status: '', priority: '' });
const caseFiltersApplied = ref({ status: '', priority: '' });
const activeCaseActions = ref<string | null>(null);
const caseActionModal = ref({
  isOpen: false,
  caseId: '' as UUID,
  action: '',
  note: '',
});
const priorityModal = ref({
  isOpen: false,
  caseId: '' as UUID,
  priority: 'MEDIUM',
});

// Audit state
const auditType = ref<'user' | 'userBan' | 'room' | 'invite' | 'report' | 'case' | 'action'>('user');

// Termination Modal
const terminationModal = ref({
  isOpen: false,
  userId: '',
  reason: '',
  duration: 'permanent',
});

// Confirmation Modal State
const confirmationModal = ref({
  isOpen: false,
  title: '',
  message: '',
  action: null as (() => Promise<void>) | null,
});

// Composables - Users
const { users, loading: loadingUsers, error: usersError, refetch: refetchUsersComposable } = useAdminUsers(computed(() => userSearch.value.filter));
const { updateStaffStatus } = useUpdateUserStaffStatus();
const { updateActiveStatus } = useUpdateUserActiveStatus();

// Composables - Cases
const { cases, loading: loadingCases, error: casesError, refetch: refetchCasesComposable } = useAdminCases(
  computed(() => ({
    status: caseFiltersApplied.value.status || undefined,
    priority: caseFiltersApplied.value.priority ? Number(caseFiltersApplied.value.priority) : undefined,
    targetType: undefined,
  }))
);
const { takeCaseAction } = useTakeCaseAction();
const { setCaseUnderReview } = useSetCaseUnderReview();
const { setCasePriority } = useSetCasePriority();
const { reopenCase } = useReopenCase();

// Composables - Audit
const auditFilters = ref({ dateFrom: undefined, dateTo: undefined, actorUsername: undefined, name: undefined });
const userAudit = useUserAudits(auditFilters);
const userBanAudit = useUserBanAudits(auditFilters);
const roomAudit = useRoomAudits(auditFilters);
const inviteAudit = useInviteAudits(auditFilters);
const reportAudit = useReportAudits(auditFilters);
const caseAudit = useModerationCaseAudits(auditFilters);
const actionAudit = useModerationActionAudits(auditFilters);

const auditMap = {
  user: userAudit,
  userBan: userBanAudit,
  room: roomAudit,
  invite: inviteAudit,
  report: reportAudit,
  case: caseAudit,
  action: actionAudit,
} as const;

const auditEntries = computed(() => auditMap[auditType.value].entries.value);
const auditLoading = computed(() => auditMap[auditType.value].loading.value);
const auditError = computed(() => auditMap[auditType.value].error.value);
const auditHasMore = computed(() => auditMap[auditType.value].hasNextPage.value);

function auditLoadMore() {
  auditMap[auditType.value].loadMore();
}

// Computed
const pendingCasesCount = computed(() => {
  return cases.value.filter((c) => c.status === 'PENDING' || c.status === 'UNDER_REVIEW').length;
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

const sortedCases = computed(() => {
  return [...cases.value].sort((a, b) => {
    return new Date(b.updatedAt || b.createdAt).getTime() - new Date(a.updatedAt || a.createdAt).getTime();
  });
});

// Methods
function onUserSearch() {
  userSearch.value.filter = userSearch.value.query;
  refetchUsersComposable();
}

function closeTerminationModal() {
  terminationModal.value.isOpen = false;
  terminationModal.value.userId = '';
  terminationModal.value.reason = '';
  terminationModal.value.duration = 'permanent';
}

function calculateExpiresAt(duration: string): string | undefined {
  if (duration === 'permanent') return undefined;

  const now = new Date();
  switch (duration) {
    case '1h':
      now.setHours(now.getHours() + 1);
      break;
    case '24h':
      now.setHours(now.getHours() + 24);
      break;
    case '7d':
      now.setDate(now.getDate() + 7);
      break;
    case '30d':
      now.setDate(now.getDate() + 30);
      break;
  }
  return now.toISOString();
}

async function confirmTermination() {
  const reason = terminationModal.value.reason || 'Administratively banned';
  const expiresAt = calculateExpiresAt(terminationModal.value.duration);

  try {
    const result = await updateActiveStatus(
      terminationModal.value.userId,
      false,
      reason,
      expiresAt
    );

    if (result?.data?.updateUserActiveStatus?.success) {
      await refetchUsersComposable();
      selectedUsers.value = [];
      closeTerminationModal();
    }
  } catch (e: unknown) {
    console.error('Failed to terminate user:', e);
  }
}

function terminateUser(userId: string) {
  terminationModal.value.userId = userId;
  terminationModal.value.isOpen = true;
  activeUserActions.value = null;
}

function activateUser(userId: string) {
  confirmationModal.value = {
    isOpen: true,
    title: 'Confirm Activation',
    message: 'Are you sure you want to activate this user?',
    action: async () => {
      const result = await updateActiveStatus([userId], true);
      if (result?.data?.updateUserActiveStatus?.success) {
        await refetchUsersComposable();
        const idx = selectedUsers.value.indexOf(userId);
        if (idx > -1) selectedUsers.value.splice(idx, 1);
      }
    },
  };
  activeUserActions.value = null;
}

function applyCaseFilters() {
  caseFiltersApplied.value = { ...caseFiltersUI.value };
  refetchCasesComposable();
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

function toggleCaseActions(caseId: string) {
  activeCaseActions.value = activeCaseActions.value === caseId ? null : caseId;
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

// Bulk Actions
function applyBulkAction() {
  switch (selectedBulkAction.value) {
    case 'promote':
      bulkPromoteUsers();
      break;
    case 'demote':
      bulkDemoteUsers();
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

async function bulkActivateUsers() {
  try {
    await updateActiveStatus(selectedUsers.value, true);
    await refetchUsersComposable();
    selectedUsers.value = [];
  } catch (error) {
    console.error('Failed to activate users:', error);
  }
}

// Case Actions
async function startReviewCase(caseId: UUID) {
  activeCaseActions.value = null;
  try {
    await setCaseUnderReview(caseId);
    await refetchCasesComposable();
  } catch (error) {
    console.error('Failed to start review:', error);
  }
}

function openCaseActionModal(mc: ModerationCase) {
  activeCaseActions.value = null;
  caseActionModal.value = {
    isOpen: true,
    caseId: mc.id,
    action: '',
    note: '',
  };
}

function closeCaseActionModal() {
  caseActionModal.value.isOpen = false;
  caseActionModal.value.caseId = '' as UUID;
  caseActionModal.value.action = '';
  caseActionModal.value.note = '';
}

async function confirmCaseAction() {
  if (!caseActionModal.value.action) return;
  try {
    await takeCaseAction(
      caseActionModal.value.caseId,
      caseActionModal.value.action,
      caseActionModal.value.note || undefined
    );
    await refetchCasesComposable();
    closeCaseActionModal();
  } catch (error) {
    console.error('Failed to take case action:', error);
  }
}

function openPriorityModal(mc: ModerationCase) {
  activeCaseActions.value = null;
  priorityModal.value = {
    isOpen: true,
    caseId: mc.id,
    priority: mc.priority === 0 ? 'LOW' : mc.priority === 1 ? 'MEDIUM' : 'HIGH',
  };
}

function closePriorityModal() {
  priorityModal.value.isOpen = false;
  priorityModal.value.caseId = '' as UUID;
}

async function confirmSetPriority() {
  try {
    await setCasePriority(priorityModal.value.caseId, priorityModal.value.priority);
    await refetchCasesComposable();
    closePriorityModal();
  } catch (error) {
    console.error('Failed to set priority:', error);
  }
}

async function handleReopenCase(caseId: UUID) {
  activeCaseActions.value = null;
  showConfirmation(
    'Reopen Case',
    'Are you sure you want to reopen this case?',
    async () => {
      try {
        await reopenCase(caseId);
        await refetchCasesComposable();
      } catch (error) {
        console.error('Failed to reopen case:', error);
        throw error;
      }
    }
  );
}

function priorityLabel(priority: number): string {
  switch (priority) {
    case 0: return 'Low';
    case 1: return 'Medium';
    case 2: return 'High';
    default: return 'Unknown';
  }
}

function formatActionType(action: string): string {
  return action
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
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

// Close dropdowns when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (!(event.target as Element).closest('.dropdown')) {
    activeUserActions.value = null;
    activeCaseActions.value = null;
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

/* Cases */
.cases-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  min-height: 200px;
}

.case-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1.5rem;
  transition: var(--transition);
}

.case-card:hover {
  box-shadow: var(--shadow);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.case-id {
  font-family: monospace;
  font-size: 0.875rem;
  color: var(--text-light);
}

.case-status-badge {
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

.case-priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.priority-low {
  background-color: #d1fae5;
  color: #065f46;
}

.priority-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.priority-high {
  background-color: #fef2f2;
  color: #dc2626;
}

.case-actions-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.case-date {
  font-size: 0.875rem;
  color: var(--text-light);
  white-space: nowrap;
}

.case-body {
  margin-bottom: 1rem;
}

.case-reports h4,
.case-action-history h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.case-report-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.case-report-item:last-child {
  border-bottom: none;
}

.report-reporter {
  font-size: 0.875rem;
  color: var(--text-light);
}

.report-description-text {
  width: 100%;
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  color: var(--text-color);
  line-height: 1.5;
}

.report-reason-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.case-action-history {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.case-action-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.action-type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.action-no_violation {
  background-color: #d1fae5;
  color: #065f46;
}

.action-content_removed {
  background-color: #fef3c7;
  color: #92400e;
}

.action-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.action-temp_ban {
  background-color: #fef2f2;
  color: #dc2626;
}

.action-perm_ban {
  background-color: #fef2f2;
  color: #991b1b;
}

.action-moderator {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
}

.action-date {
  font-size: 0.8rem;
  color: var(--text-light);
}

.action-note {
  width: 100%;
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  color: var(--text-color);
  padding: 0.5rem;
  background-color: var(--bg-color);
  border-radius: var(--radius);
  border-left: 3px solid var(--primary-color);
}

/* Audit */
.audit-table th,
.audit-table td {
  padding: 0.75rem 1rem;
}

.audit-label-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.audit-obj-id {
  font-family: monospace;
  font-size: 0.875rem;
  color: var(--text-light);
}

.load-more-container {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0;
}

.btn-load-more {
  padding: 0.75rem 2rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-load-more:hover {
  background-color: var(--primary-hover);
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

  .case-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .case-actions-header {
    width: 100%;
    justify-content: space-between;
  }
}
</style>