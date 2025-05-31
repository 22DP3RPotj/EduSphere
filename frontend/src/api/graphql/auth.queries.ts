import { gql } from "@apollo/client";

export const GET_USER = gql`
    query GetUser {
        me {
            id
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
                id
                name
                username
                avatar
            }
            isAuthenticated
        }
    }
`;