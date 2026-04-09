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
                language
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
    mutation Register(
        $username: String!
        $name: String!
        $email: String!
        $password1: String!
        $password2: String!
    ) {
        register(
        username: $username
        name: $name
        email: $email
        password1: $password1
        password2: $password2
        ) {
            success
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
        $language: LanguageChoices
    ) {
        updateUser(
            name: $name
            bio: $bio
            avatar: $avatar
            language: $language
        ) {
            user {
                id
                username
                name
                bio
                avatar
                language
                isStaff
                isSuperuser
            }
        }
    }
`;
