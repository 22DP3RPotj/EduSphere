import { gql } from "@apollo/client";

const AUDIT_FIELDS = `
    pghId
    pghCreatedAt
    pghLabel
    pghObjId
    actor {
        id
        username
        name
    }
`;

export const USER_AUDITS_QUERY = gql`
    query UserAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        userAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    isStaff
                    isActive
                    isSuperuser
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const USER_BAN_AUDITS_QUERY = gql`
    query UserBanAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        userBanAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    reason
                    expiresAt
                    isActive
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const ROOM_AUDITS_QUERY = gql`
    query RoomAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String, $name: String) {
        roomAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername, name: $name) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    name
                    description
                    visibility
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const INVITE_AUDITS_QUERY = gql`
    query InviteAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        inviteAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    status
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const REPORT_AUDITS_QUERY = gql`
    query ReportAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        reportAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    description
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const MODERATION_CASE_AUDITS_QUERY = gql`
    query ModerationCaseAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        moderationCaseAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    status
                    priority
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;

export const MODERATION_ACTION_AUDITS_QUERY = gql`
    query ModerationActionAudits($first: Int, $after: String, $dateFrom: Date, $dateTo: Date, $actorUsername: String) {
        moderationActionAudits(first: $first, after: $after, dateFrom: $dateFrom, dateTo: $dateTo, actorUsername: $actorUsername) {
            edges {
                node {
                    ${AUDIT_FIELDS}
                    action
                    note
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
`;
