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

export const GET_ALL_REPORTS = gql`
  query GetReports($status: ReportStatus, $reason: ReportReason, $userId: UUID) {
    reports(status: $status, reason: $reason, userId: $userId) {
      id
      body
      reason
      status
      moderatorNote
      createdAt
      updatedAt
      user {
        id
        username
        name
        avatar
      }
      room {
        id
        name
        host {
          id
          username
        }
      }
      moderator {
        id
        username
        name
      }
    }
  }
`;

export const GET_REPORT_COUNT = gql`
  query GetReportCount($status: ReportStatus, $reason: ReportReason, $userId: UUID) {
    reportCount(status: $status, reason: $reason, userId: $userId)
  }
`;
