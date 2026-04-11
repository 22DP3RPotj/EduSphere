import { gql } from "@apollo/client";

export const CREATE_ROLE_MUTATION = gql`
    mutation CreateRole($roomId: UUID!, $name: String!, $description: String!, $priority: Int!, $permissionIds: [UUID]) {
        createRole(roomId: $roomId, name: $name, description: $description, priority: $priority, permissionIds: $permissionIds) {
            role {
                id
                name
                description
                priority
                permissions {
                    id
                    code
                    description
                }
            }
        }
    }
`;

export const UPDATE_ROLE_MUTATION = gql`
    mutation UpdateRole($roleId: UUID!, $name: String, $description: String, $priority: Int, $permissionIds: [UUID]) {
        updateRole(roleId: $roleId, name: $name, description: $description, priority: $priority, permissionIds: $permissionIds) {
            role {
                id
                name
                description
                priority
                permissions {
                    id
                    code
                    description
                }
            }
        }
    }
`;

export const DELETE_ROLE_MUTATION = gql`
    mutation DeleteRole($roleId: UUID!, $substitutionRoleId: UUID) {
        deleteRole(roleId: $roleId, substitutionRoleId: $substitutionRoleId) {
            result {
                success
                deletedRoleId
                substitutionRoleId
                reassignedCount
            }
        }
    }
`;

export const ASSIGN_PERMISSIONS_MUTATION = gql`
    mutation AssignPermissionsToRole($roleId: UUID!, $permissionIds: [UUID!]!) {
        assignPermissionsToRole(roleId: $roleId, permissionIds: $permissionIds) {
            role {
                id
                permissions {
                    id
                    code
                    description
                }
            }
        }
    }
`;

export const REMOVE_PERMISSIONS_MUTATION = gql`
    mutation RemovePermissionsFromRole($roleId: UUID!, $permissionIds: [UUID!]!) {
        removePermissionsFromRole(roleId: $roleId, permissionIds: $permissionIds) {
            role {
                id
                permissions {
                    id
                    code
                    description
                }
            }
        }
    }
`;
