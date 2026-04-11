import { gql } from "@apollo/client";

export const CREATE_REPORT_MUTATION = gql`
    mutation CreateReport($targetType: ReportTargetTypeEnum!, $targetId: UUID!, $reasonId: UUID!, $description: String) {
        createReport(targetType: $targetType, targetId: $targetId, reasonId: $reasonId, description: $description) {
            report {
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
                }
            }
        }
    }
`;

export const REPORT_REASONS_QUERY = gql`
    query ReportReasons($targetType: ReportTargetTypeEnum) {
        reportReasons(targetType: $targetType) {
            id
            slug
            label
            isActive
        }
    }
`;

export const SUBMITTED_REPORTS_QUERY = gql`
    query SubmittedReports {
        submittedReports {
            id
            description
            createdAt
            reason {
                id
                slug
                label
            }
            case {
                id
                status
            }
        }
    }
`;
