import { gql } from "@apollo/client";

export const GET_ALL_USERS = gql`
  query GetAllUsers($search: String) {
    users(search: $search) {
      id
      username
      name
      bio
      avatar
      isStaff
      isActive
      isSuperuser
      dateJoined
    }
  }
`;

export const GET_REPORTS = gql`
  query GetReports(
    $reason: UUID,
    $reporter: UUID,
    $case: UUID,
    $hasCase: Boolean,
    $targetType: ReportTargetTypeEnum,
    $createdAfter: DateTime,
    $createdBefore: DateTime
  ) {
    reports(
      reason: $reason,
      reporter: $reporter,
      case: $case,
      hasCase: $hasCase,
      targetType: $targetType,
      createdAfter: $createdAfter,
      createdBefore: $createdBefore
    ) {
      id
      description
      createdAt
      reason {
        id
        slug
        label
      }
      reporter {
        id
        username
        name
        avatar
      }
      case {
        id
        status
        priority
      }
    }
  }
`;

export const GET_REPORT_COUNT = gql`
  query GetReportCount(
    $reason: UUID,
    $reporter: UUID,
    $case: UUID,
    $hasCase: Boolean,
    $targetType: ReportTargetTypeEnum,
    $createdAfter: DateTime,
    $createdBefore: DateTime
  ) {
    reportCount(
      reason: $reason,
      reporter: $reporter,
      case: $case,
      hasCase: $hasCase,
      targetType: $targetType,
      createdAfter: $createdAfter,
      createdBefore: $createdBefore
    )
  }
`;

export const GET_CASES = gql`
  query GetCases(
    $status: CaseStatusEnum,
    $priority: Int,
    $hasActions: Boolean,
    $targetType: ReportTargetTypeEnum,
    $createdAfter: DateTime,
    $createdBefore: DateTime,
    $updatedAfter: DateTime,
    $updatedBefore: DateTime
  ) {
    cases(
      status: $status,
      priority: $priority,
      hasActions: $hasActions,
      targetType: $targetType,
      createdAfter: $createdAfter,
      createdBefore: $createdBefore,
      updatedAfter: $updatedAfter,
      updatedBefore: $updatedBefore
    ) {
      id
      status
      priority
      createdAt
      updatedAt
      reports {
        id
        description
        reason {
          id
          slug
          label
        }
        reporter {
          id
          username
          name
        }
      }
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
`;

export const GET_CASE = gql`
  query GetCase($caseId: UUID!) {
    case(caseId: $caseId) {
      id
      status
      priority
      createdAt
      updatedAt
      reports {
        id
        description
        createdAt
        reason {
          id
          slug
          label
        }
        reporter {
          id
          username
          name
          avatar
        }
      }
      actions {
        id
        action
        note
        createdAt
        moderator {
          id
          username
          name
          avatar
        }
      }
    }
  }
`;
