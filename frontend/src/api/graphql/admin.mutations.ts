import { gql } from "@apollo/client";

export const UPDATE_USER_STAFF_STATUS = gql`
  mutation UpdateUserStaffStatus($userIds: [UUID!]!, $isStaff: Boolean!) {
    updateUserStaffStatus(userIds: $userIds, isStaff: $isStaff) {
      success
      updatedCount
    }
  }
`;

export const UPDATE_USER_ACTIVE_STATUS = gql`
  mutation UpdateUserActiveStatus(
    $userIds: [UUID!]!
    $isActive: Boolean!
    $reason: String
    $expiresAt: DateTime
  ) {
    updateUserActiveStatus(
      userIds: $userIds
      isActive: $isActive
      reason: $reason
      expiresAt: $expiresAt
    ) {
      success
      updatedCount
    }
  }
`;

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
