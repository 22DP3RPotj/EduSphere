import { gql } from "@apollo/client";

export const LOGIN_MUTATION = gql`
    mutation TokenAuth($email: String!, $password: String!) {
        tokenAuth(email: $email, password: $password) {
            success
            payload
            refreshExpiresIn
            user {
                id
                username
                name
                avatar
                isSuperuser
            }
        }
    }
`;

export const REFRESH_TOKEN_MUTATION = gql`
    mutation RefreshToken {
        refreshToken {
            payload
            refreshExpiresIn
        }
    }
`;

export const REGISTER_MUTATION = gql`
    mutation RegisterUser(
        $username: String!
        $name: String!
        $email: String!
        $password1: String!
        $password2: String!
    ) {
        registerUser(
        username: $username
        name: $name
        email: $email
        password1: $password1
        password2: $password2
        ) {
            success
            user {
                id
                username
                name
                isStaff
                isSuperuser
            }
        }
    }
`;

export const LOGOUT_MUTATION = gql`
    mutation LogoutUser {
        deleteToken {
            deleted
        }
    }
`;

export const UPDATE_USER_MUTATION = gql`
    mutation UpdateUser(
        $name: String
        $bio: String
        $avatar: Upload
    ) {
        updateUser(
            name: $name
            bio: $bio
            avatar: $avatar
        ) {
            user {
                id
                username
                name
                bio
                avatar
                isStaff
                isSuperuser
            }
        }
    }
`;
