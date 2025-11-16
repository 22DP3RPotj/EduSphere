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
  query GetAllReports($status: ReportStatus, $reason: ReportReason, $user: String) {
    allReports(status: $status, reason: $reason, user: $user) {
      id
      body
      reason
      status
      moderatorNote
      created
      updated
      user {
        id
        username
        name
        avatar
      }
      room {
        id
        name
        slug
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
  query GetReportCount($status: ReportStatus, $reason: ReportReason, $user: String) {
    reportCount(status: $status, reason: $reason, user: $user)
  }
`;
