import { gql } from "@apollo/client";

export const TAKE_CASE_ACTION = gql`
  mutation TakeCaseAction($caseId: UUID!, $action: ActionEnum!, $note: String) {
    takeCaseAction(caseId: $caseId, action: $action, note: $note) {
      case {
        id
        status
        priority
        updatedAt
        actions {
          id
          action
          note
          createdAt
          moderator {
            id
            username
            name
          }
        }
      }
    }
  }
`;

export const SET_CASE_UNDER_REVIEW = gql`
  mutation SetCaseUnderReview($caseId: UUID!) {
    setCaseUnderReview(caseId: $caseId) {
      case {
        id
        status
        updatedAt
      }
    }
  }
`;

export const SET_CASE_PRIORITY = gql`
  mutation SetCasePriority($caseId: UUID!, $priority: ActionPriorityEnum!) {
    setCasePriority(caseId: $caseId, priority: $priority) {
      case {
        id
        priority
        updatedAt
      }
    }
  }
`;

export const REOPEN_CASE = gql`
  mutation ReopenCase($caseId: UUID!) {
    reopenCase(caseId: $caseId) {
      case {
        id
        status
        updatedAt
      }
    }
  }
`;

export const BAN_USER = gql`
  mutation BanUser($userId: UUID!, $reason: String, $expiresAt: DateTime) {
    banUser(userId: $userId, reason: $reason, expiresAt: $expiresAt) {
      success
    }
  }
`;

export const UNBAN_USER = gql`
  mutation UnbanUser($userId: UUID!) {
    unbanUser(userId: $userId) {
      success
    }
  }
`;

export const BAN_USERS = gql`
  mutation BanUsers($userIds: [UUID!]!, $reason: String, $expiresAt: DateTime) {
    banUsers(userIds: $userIds, reason: $reason, expiresAt: $expiresAt) {
      success
      bannedCount
      skippedCount
    }
  }
`;

export const UNBAN_USERS = gql`
  mutation UnbanUsers($userIds: [UUID!]!) {
    unbanUsers(userIds: $userIds) {
      success
      unbannedCount
      skippedCount
    }
  }
`;

export const PROMOTE_USERS = gql`
  mutation PromoteUsers($userIds: [UUID!]!) {
    promoteUsers(userIds: $userIds) {
      success
      updatedCount
    }
  }
`;

export const DEMOTE_USERS = gql`
  mutation DemoteUsers($userIds: [UUID!]!) {
    demoteUsers(userIds: $userIds) {
      success
      updatedCount
    }
  }
`;

export const PROMOTE_USER = gql`
  mutation PromoteUser($userId: UUID!) {
    promoteUser(userId: $userId) {
      success
    }
  }
`;

export const DEMOTE_USER = gql`
  mutation DemoteUser($userId: UUID!) {
    demoteUser(userId: $userId) {
      success
    }
  }
`;
