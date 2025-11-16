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
  mutation UpdateUserActiveStatus($userIds: [UUID!]!, $isActive: Boolean!) {
    updateUserActiveStatus(userIds: $userIds, isActive: $isActive) {
      success
      updatedCount
    }
  }
`;

export const UPDATE_REPORT = gql`
  mutation UpdateReport($reportId: UUID!, $status: ReportStatus, $moderatorNote: String) {
    updateReport(reportId: $reportId, status: $status, moderatorNote: $moderatorNote) {
      report {
        id
        status
        moderatorNote
        updated
        moderator {
          id
          username
          name
        }
      }
    }
  }
`;

export const DELETE_REPORT = gql`
  mutation DeleteReport($reportId: UUID!) {
    deleteReport(reportId: $reportId) {
      success
    }
  }
`;
