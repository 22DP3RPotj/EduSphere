import { gql } from "@apollo/client";

export const ROOM_ROLES_QUERY = gql`
    query RoomRoles($roomId: UUID!) {
        roomRoles(roomId: $roomId) {
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
`;

export const AVAILABLE_PERMISSIONS_QUERY = gql`
    query AvailablePermissions($roomId: UUID!) {
        availablePermissions(roomId: $roomId) {
            id
            code
            description
        }
    }
`;

export const ROLE_QUERY = gql`
    query Role($roleId: UUID!) {
        role(roleId: $roleId) {
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
`;
