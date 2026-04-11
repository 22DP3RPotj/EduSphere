<template>
  <div class="reports-page">
    <div class="page-header">
      <button class="back-button" @click="$router.back()">
        <font-awesome-icon icon="arrow-left" />
      </button>
      <h1>My Reports</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading reports...</p>
    </div>

    <template v-else>
      <div v-if="reports.length > 0" class="filters-row">
        <div class="filter-group">
          <label for="status-filter">Case Status</label>
          <select id="status-filter" v-model="statusFilter" class="filter-select">
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="RESOLVED">Resolved</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="reason-filter">Reason</label>
          <select id="reason-filter" v-model="reasonFilter" class="filter-select">
            <option value="">All</option>
            <option v-for="reason in uniqueReasons" :key="reason.id" :value="reason.id">
              {{ reason.label }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="filteredReports.length === 0 && reports.length > 0" class="empty-state">
        <font-awesome-icon icon="filter" size="2x" />
        <p>No reports match the selected filters.</p>
      </div>

      <div v-else-if="reports.length === 0" class="empty-state">
        <font-awesome-icon icon="flag" size="2x" />
        <p>You haven't submitted any reports yet.</p>
      </div>

      <div v-else class="reports-list">
        <div v-for="report in filteredReports" :key="report.id" class="report-card">
        <div class="report-info">
          <div class="report-reason">
            <font-awesome-icon icon="exclamation-circle" class="icon" />
            <span class="reason-label">{{ report.reason.label }}</span>
          </div>
          <p v-if="report.description" class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <span class="report-date">{{ formatDate(report.createdAt) }}</span>
            <span v-if="report.case" class="case-status" :class="report.case.status.toLowerCase()">
              {{ formatStatus(report.case.status) }}
            </span>
            <span v-else class="case-status pending">Pending Review</span>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { useSubmittedReports } from '@/composables/useReports';
import type { Report } from '@/types';

const { reports, loading } = useSubmittedReports();

const statusFilter = ref('');
const reasonFilter = ref('');

const uniqueReasons = computed(() => {
  const seen = new Map<string, { id: string; label: string }>();
  for (const r of reports.value) {
    if (!seen.has(r.reason.id)) {
      seen.set(r.reason.id, { id: r.reason.id, label: r.reason.label });
    }
  }
  return [...seen.values()];
});

const filteredReports = computed(() => {
  return reports.value.filter((r: Report) => {
    if (reasonFilter.value && r.reason.id !== reasonFilter.value) return false;
    if (statusFilter.value) {
      if (!r.case || r.case.status !== statusFilter.value) return false;
    }
    return true;
  });
});

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatStatus(status: string) {
  return status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
}
</script>

<style scoped>
.reports-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0;
}

.back-button {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: var(--radius);
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}

.back-button:hover {
  background-color: var(--hover-bg);
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
  color: var(--text-secondary);
  font-weight: 500;
}

.filter-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--white);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.report-card {
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.report-reason {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.report-reason .icon {
  color: var(--danger);
}

.report-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

.report-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.case-status {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.case-status.pending {
  background-color: var(--warning-bg, #fff3cd);
  color: var(--warning-text, #856404);
}

.case-status.under_review {
  background-color: var(--info-bg, #cce5ff);
  color: var(--info-text, #004085);
}

.case-status.resolved {
  background-color: var(--success-bg, #d4edda);
  color: var(--success-text, #155724);
}

.case-status.dismissed {
  background-color: var(--muted-bg, #e2e3e5);
  color: var(--muted-text, #383d41);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
