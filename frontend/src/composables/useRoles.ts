import { computed, type Ref } from "vue"
import { useMutation, useQuery } from "@vue/apollo-composable"
import {
  ROOM_ROLES_QUERY,
  AVAILABLE_PERMISSIONS_QUERY,
  CREATE_ROLE_MUTATION,
  UPDATE_ROLE_MUTATION,
  DELETE_ROLE_MUTATION,
  ASSIGN_PERMISSIONS_MUTATION,
  REMOVE_PERMISSIONS_MUTATION,
} from "@/api/graphql"
import type { UUID } from "@/types"
import type { CreateRoleInput, UpdateRoleInput } from "@/types"

export function useRoomRoles(roomId: Ref<UUID>) {
  const { result, loading, error, refetch } = useQuery(
    ROOM_ROLES_QUERY,
    () => ({ roomId: roomId.value }),
    { fetchPolicy: "cache-and-network" }
  )

  return {
    roles: computed(() => result.value?.roomRoles || []),
    loading,
    error,
    refetch,
  }
}

export function useAvailablePermissions(roomId: Ref<UUID>) {
  const { result, loading, error } = useQuery(
    AVAILABLE_PERMISSIONS_QUERY,
    () => ({ roomId: roomId.value }),
    { fetchPolicy: "cache-and-network" }
  )

  return {
    permissions: computed(() => result.value?.availablePermissions || []),
    loading,
    error,
  }
}

export function useCreateRole() {
  const { mutate, loading, error } = useMutation(CREATE_ROLE_MUTATION)

  async function createRole(data: CreateRoleInput) {
    const result = await mutate(data)

    if (result?.data?.createRole?.role) {
      return { success: true, role: result.data.createRole.role }
    }

    return { success: false, error: "Failed to create role" }
  }

  return { createRole, loading, error }
}

export function useUpdateRole() {
  const { mutate, loading, error } = useMutation(UPDATE_ROLE_MUTATION)

  async function updateRole(data: UpdateRoleInput) {
    const result = await mutate(data)

    if (result?.data?.updateRole?.role) {
      return { success: true, role: result.data.updateRole.role }
    }

    return { success: false, error: "Failed to update role" }
  }

  return { updateRole, loading, error }
}

export function useDeleteRole() {
  const { mutate, loading, error } = useMutation(DELETE_ROLE_MUTATION)

  async function deleteRole(roleId: UUID, substitutionRoleId?: UUID) {
    const result = await mutate({ roleId, substitutionRoleId })

    if (result?.data?.deleteRole?.result?.success) {
      return { success: true, result: result.data.deleteRole.result }
    }

    return { success: false, error: "Failed to delete role" }
  }

  return { deleteRole, loading, error }
}

export function useAssignPermissions() {
  const { mutate, loading, error } = useMutation(ASSIGN_PERMISSIONS_MUTATION)

  async function assignPermissions(roleId: UUID, permissionIds: UUID[]) {
    const result = await mutate({ roleId, permissionIds })

    if (result?.data?.assignPermissionsToRole?.role) {
      return { success: true, role: result.data.assignPermissionsToRole.role }
    }

    return { success: false, error: "Failed to assign permissions" }
  }

  return { assignPermissions, loading, error }
}

export function useRemovePermissions() {
  const { mutate, loading, error } = useMutation(REMOVE_PERMISSIONS_MUTATION)

  async function removePermissions(roleId: UUID, permissionIds: UUID[]) {
    const result = await mutate({ roleId, permissionIds })

    if (result?.data?.removePermissionsFromRole?.role) {
      return { success: true, role: result.data.removePermissionsFromRole.role }
    }

    return { success: false, error: "Failed to remove permissions" }
  }

  return { removePermissions, loading, error }
}
