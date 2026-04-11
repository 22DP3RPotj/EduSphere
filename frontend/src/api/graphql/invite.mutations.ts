import { gql } from "@apollo/client";

export const SEND_INVITE_MUTATION = gql`
    mutation SendInvite($roomId: UUID!, $inviteeEmail: String!, $expiresAt: DateTime, $roleId: UUID) {
        sendInvite(roomId: $roomId, inviteeEmail: $inviteeEmail, expiresAt: $expiresAt, roleId: $roleId) {
            invite {
                id
                token
                status
                createdAt
                expiresAt
                inviter {
                    id
                    username
                    name
                    avatar
                }
                invitee {
                    id
                    username
                    name
                    avatar
                }
                role {
                    id
                    name
                }
            }
        }
    }
`;

export const ACCEPT_INVITE_MUTATION = gql`
    mutation AcceptInvite($token: UUID!) {
        acceptInvite(token: $token) {
            participant {
                id
                user {
                    id
                    username
                    name
                    avatar
                }
                role {
                    id
                    name
                }
                joinedAt
            }
        }
    }
`;

export const DECLINE_INVITE_MUTATION = gql`
    mutation DeclineInvite($token: UUID!) {
        declineInvite(token: $token) {
            invite {
                id
                status
            }
        }
    }
`;

export const CANCEL_INVITE_MUTATION = gql`
    mutation CancelInvite($token: UUID!) {
        cancelInvite(token: $token) {
            invite {
                id
                status
            }
        }
    }
`;

export const RESEND_INVITE_MUTATION = gql`
    mutation ResendInvite($token: UUID!, $expiresAt: DateTime) {
        resendInvite(token: $token, expiresAt: $expiresAt) {
            invite {
                id
                token
                status
                expiresAt
            }
        }
    }
`;
