import { gql } from "@apollo/client";

export const GET_USER = gql`
    query GetUser {
        me {
            name
            username
            avatar
        }
    }
`;

export const GET_AUTH_STATUS = gql`
    query AuthStatus {
        authStatus {
            user {
                name
                username
                avatar
            }
            isAuthenticated
        }
    }
`;