import { gql } from "@apollo/client";

export const RECEIVED_INVITES_QUERY = gql`
    query ReceivedInvites {
        receivedInvites {
            id
            token
            status
            createdAt
            expiresAt
            room {
                id
                name
            }
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
`;

export const SENT_INVITES_QUERY = gql`
    query SentInvites {
        sentInvites {
            id
            token
            status
            createdAt
            expiresAt
            room {
                id
                name
            }
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
`;

export const INVITE_BY_TOKEN_QUERY = gql`
    query InviteByToken($token: UUID!) {
        invite(token: $token) {
            id
            token
            status
            createdAt
            expiresAt
            room {
                id
                name
            }
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
`;
