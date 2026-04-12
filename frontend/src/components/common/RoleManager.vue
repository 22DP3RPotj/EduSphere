<template>
  <div class="role-manager">
    <div class="role-manager-header">
      <h3>{{ t('role.roles') }}</h3>
      <button class="btn-create" @click="showCreateForm = true">
        <font-awesome-icon icon="plus" />
        {{ t('role.createRole') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="rolesLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <!-- Empty state -->
    <div v-else-if="roles.length === 0" class="empty-state">
      <p>{{ t('role.noRoles') }}</p>
    </div>

    <!-- Roles list -->
    <div v-else class="roles-list">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="role-header">
          <div class="role-name-row">
            <span class="role-name">{{ role.name }}</span>
            <span class="role-priority">{{ t('role.priorityPrefix') }}{{ role.priority }}</span>
          </div>
          <div class="role-actions">
            <button class="btn-icon" @click="startEdit(role)">
              <font-awesome-icon icon="edit" />
            </button>
            <button class="btn-icon danger" @click="confirmDelete(role)">
              <font-awesome-icon icon="trash" />
            </button>
          </div>
        </div>
        <p v-if="role.description" class="role-description">{{ role.description }}</p>
        <div v-if="role.permissions?.length" class="role-permissions">
          <span v-for="perm in role.permissions" :key="perm.id" class="permission-tag">
            {{ perm.code }}
          </span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Form Modal -->
    <Teleport to="body">
    <div v-if="showCreateForm || editingRole" class="modal-overlay" @click="closeForm">
      <div class="modal-content" @click.stop>
        <h3>{{ editingRole ? t('role.editRole') : t('role.createRole') }}</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>{{ t('role.roleName') }}</label>
            <input v-model="formData.name" type="text" class="form-input" required />
          </div>
          <div class="form-group">
            <label>{{ t('role.roleDescription') }}</label>
            <input v-model="formData.description" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label>{{ t('role.rolePriority') }}</label>
            <input v-model.number="formData.priority" type="number" class="form-input" min="0" required />
          </div>
          <div class="form-group">
            <label>{{ t('role.permissions') }}</label>
            <div class="permissions-grid">
              <label
                v-for="perm in availablePermissions"
                :key="perm.id"
                class="permission-checkbox"
              >
                <input
                  type="checkbox"
                  :value="perm.id"
                  :checked="formData.permissionIds.includes(perm.id)"
                  @change="togglePermission(perm.id)"
                />
                <span class="perm-label">{{ perm.code }}</span>
                <span v-if="perm.description" class="perm-desc">{{ perm.description }}</span>
              </label>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeForm">{{ t('common.cancel') }}</button>
            <button type="submit" class="btn-confirm" :disabled="createLoading || updateLoading">
              <font-awesome-icon v-if="createLoading || updateLoading" icon="spinner" spin />
              {{ t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
    </Teleport>

    <!-- Delete confirmation -->
    <Teleport to="body">
    <div v-if="deletingRole" class="modal-overlay" @click="deletingRole = null">
      <div class="modal-content" @click.stop>
        <h3>{{ t('role.deleteRole') }}</h3>
        <p>{{ t('role.deleteConfirm') }}</p>
        <div v-if="roles.length > 1" class="form-group">
          <label>{{ t('role.substitutionRole') }}</label>
          <select v-model="substitutionRoleId" class="form-select">
            <option :value="null">{{ t('common.none') }}</option>
            <option
              v-for="r in roles.filter((r: Role) => r.id !== deletingRole!.id)"
              :key="r.id"
              :value="r.id"
            >
              {{ r.name }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="deletingRole = null">{{ t('common.cancel') }}</button>
          <button type="button" class="btn-confirm danger" :disabled="deleteLoading" @click="handleDelete">
            <font-awesome-icon v-if="deleteLoading" icon="spinner" spin />
            {{ t('common.delete') }}
          </button>
        </div>
      </div>
    </div>
    </Teleport>
  </div>
</template>

<script lang="ts" setup>
import { ref, type PropType } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  useRoomRoles,
  useAvailablePermissions,
  useCreateRole,
  useUpdateRole,
  useDeleteRole,
} from '@/composables/useRoles';
import type { Role, UUID } from '@/types';

const props = defineProps({
  roomId: {
    type: String as unknown as PropType<UUID>,
    required: true,
  },
});

const emit = defineEmits<{ (e: 'updated'): void }>();

const { t } = useI18n();

const roomIdRef = ref(props.roomId);
const { roles, loading: rolesLoading, refetch: refetchRoles } = useRoomRoles(roomIdRef);
const { permissions: availablePermissions } = useAvailablePermissions(roomIdRef);
const { createRole, loading: createLoading } = useCreateRole();
const { updateRole, loading: updateLoading } = useUpdateRole();
const { deleteRole, loading: deleteLoading } = useDeleteRole();

const showCreateForm = ref(false);
interface RoleData { id: UUID; name: string; description: string; priority: number; permissions: { id: UUID }[] }
const editingRole = ref<RoleData | null>(null);
const deletingRole = ref<{ id: UUID; name: string } | null>(null);
const substitutionRoleId = ref<string | null>(null);

const formData = ref({
  name: '',
  description: '',
  priority: 0,
  permissionIds: [] as string[],
});

function startEdit(role: RoleData) {
  editingRole.value = role;
  formData.value = {
    name: role.name,
    description: role.description || '',
    priority: role.priority,
    permissionIds: (role.permissions || []).map((p: { id: UUID }) => p.id),
  };
}

function closeForm() {
  showCreateForm.value = false;
  editingRole.value = null;
  formData.value = { name: '', description: '', priority: 0, permissionIds: [] };
}

function togglePermission(permId: string) {
  const idx = formData.value.permissionIds.indexOf(permId);
  if (idx >= 0) {
    formData.value.permissionIds.splice(idx, 1);
  } else {
    formData.value.permissionIds.push(permId);
  }
}

function confirmDelete(role: RoleData) {
  deletingRole.value = role;
  substitutionRoleId.value = null;
}

async function handleSubmit() {
  if (editingRole.value) {
    const result = await updateRole({
      roleId: editingRole.value.id,
      name: formData.value.name,
      description: formData.value.description,
      priority: formData.value.priority,
      permissionIds: formData.value.permissionIds as UUID[],
    });
    if (result.success) {
      closeForm();
      refetchRoles();
      emit('updated');
    }
  } else {
    const result = await createRole({
      roomId: props.roomId,
      name: formData.value.name,
      description: formData.value.description,
      priority: formData.value.priority,
      permissionIds: formData.value.permissionIds as UUID[],
    });
    if (result.success) {
      closeForm();
      refetchRoles();
      emit('updated');
    }
  }
}

async function handleDelete() {
  if (!deletingRole.value) return;

  const result = await deleteRole(
    deletingRole.value.id,
    substitutionRoleId.value as UUID | undefined,
  );
  if (result.success) {
    deletingRole.value = null;
    refetchRoles();
    emit('updated');
  }
}
</script>

<style scoped>
.role-manager {
  padding: 1rem 0;
}

.role-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.role-manager-header h3 {
  margin: 0;
  color: var(--text-color);
}

.btn-create {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  transition: var(--transition);
}

.btn-create:hover {
  background-color: var(--primary-hover);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}

.roles-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.role-card {
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 1rem;
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-name-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-name {
  font-weight: 600;
  color: var(--text-color);
}

.role-priority {
  font-size: 0.75rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius);
  background-color: var(--bg-light);
  color: var(--text-light);
}

.role-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 0.35rem;
  border-radius: var(--radius);
  transition: var(--transition);
}

.btn-icon:hover {
  background-color: var(--bg-light);
  color: var(--text-color);
}

.btn-icon.danger:hover {
  color: #ef4444;
  background-color: #fef2f2;
}

.role-description {
  margin: 0.5rem 0;
  font-size: 0.85rem;
  color: var(--text-light);
}

.role-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.permission-tag {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius);
  background-color: var(--bg-light);
  color: var(--text-light);
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.modal-content {
  background-color: var(--white);
  border-radius: var(--radius);
  padding: 1.5rem;
  max-width: 480px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 1rem;
  color: var(--text-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.85rem;
  color: var(--text-light);
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background-color: var(--white);
  color: var(--text-color);
  font-size: 0.9rem;
}

.permissions-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.perm-label {
  font-weight: 500;
  color: var(--text-color);
}

.perm-desc {
  color: var(--text-light);
  font-size: 0.8rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  background: none;
  color: var(--text-color);
  cursor: pointer;
  transition: var(--transition);
}

.btn-cancel:hover {
  background-color: var(--bg-light);
}

.btn-confirm {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius);
  background-color: var(--primary-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  transition: var(--transition);
}

.btn-confirm:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-confirm.danger {
  background-color: #ef4444;
}

.btn-confirm.danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
