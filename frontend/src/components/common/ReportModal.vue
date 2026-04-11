<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Report {{ targetLabel }}</h3>
        <button class="modal-close" @click="close">
          <font-awesome-icon icon="times" />
        </button>
      </div>

      <div v-if="submitted" class="modal-body">
        <div class="success-message">
          <font-awesome-icon icon="check-circle" class="success-icon" />
          <p>Report submitted successfully. Our team will review it shortly.</p>
        </div>
      </div>

      <template v-else>
        <div class="modal-body">
          <div class="form-group">
            <label for="report-reason">Reason</label>
            <select id="report-reason" v-model="selectedReason" class="report-select" :disabled="reasonsLoading">
              <option value="">Select a reason...</option>
              <option v-for="reason in reasons" :key="reason.id" :value="reason.id">
                {{ reason.label }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="report-description">Description (optional)</label>
            <textarea
              id="report-description"
              v-model="description"
              placeholder="Provide additional details..."
              rows="4"
              maxlength="2000"
            ></textarea>
          </div>
          <div v-if="submitError" class="error-text">{{ submitError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="close">Cancel</button>
          <button
            class="btn-confirm danger"
            :disabled="!selectedReason || submitLoading"
            @click="submitReport"
          >
            {{ submitLoading ? 'Submitting...' : 'Submit Report' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import { useReportReasons, useCreateReport } from '@/composables/useReports';
import type { ReportTargetType, UUID } from '@/types';

const props = defineProps<{
  isOpen: boolean;
  targetType: ReportTargetType;
  targetId: UUID;
  targetLabel?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'submitted'): void;
}>();

const targetTypeRef = computed(() => props.targetType);
const { reasons, loading: reasonsLoading } = useReportReasons(targetTypeRef);
const { createReport, loading: submitLoading } = useCreateReport();

const selectedReason = ref('');
const description = ref('');
const submitError = ref('');
const submitted = ref(false);

watch(() => props.isOpen, (open) => {
  if (open) {
    selectedReason.value = '';
    description.value = '';
    submitError.value = '';
    submitted.value = false;
  }
});

function close() {
  emit('close');
}

async function submitReport() {
  if (!selectedReason.value) return;

  submitError.value = '';
  const result = await createReport({
    targetType: props.targetType,
    targetId: props.targetId,
    reasonId: selectedReason.value as UUID,
    description: description.value || undefined,
  });

  if (result.success) {
    submitted.value = true;
    emit('submitted');
  } else {
    submitError.value = result.error || 'Failed to submit report';
  }
}
</script>

<style scoped>
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
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.report-select,
.modal-body textarea {
  width: 100%;
  padding: 0.75rem;
  box-sizing: border-box;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-family: inherit;
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--white);
  transition: var(--transition);
}

.report-select:focus,
.modal-body textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.modal-body textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.error-text {
  color: var(--error-color);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}

.success-icon {
  font-size: 2rem;
  color: #10b981;
  margin-bottom: 1rem;
}

.success-message p {
  color: var(--text-color);
  line-height: 1.5;
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
  border-radius: var(--radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-confirm.danger {
  background-color: var(--error-color);
  color: white;
}

.btn-confirm.danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
