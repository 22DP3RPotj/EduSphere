import { gql } from "@apollo/client";

export const ROOM_QUERY = gql`
    query Room($hostSlug: String!, $roomSlug: String!) {
        room(hostSlug: $hostSlug, roomSlug: $roomSlug) {
            name
            slug
            description
            created
            host {
                id
                username
                name
                avatar
            }
            participants {
                id
                username
                avatar
            }
            topic {
                name
            }
        }
    }
`;

export const ROOMS_QUERY = gql`
    query Rooms($hostSlug: String, $search: String, $topic: [String]) {
        rooms(hostSlug: $hostSlug, search: $search, topic: $topic) {
            name
            slug
            description
            created
            topic {
                name
            }
            host { username }
        }
    }
`;

export const ROOMS_PARTICIPATED_BY_USER_QUERY = gql`
    query RoomsParticipatedByUser($userSlug: String!) {
        roomsParticipatedByUser(userSlug: $userSlug) {
            name
            slug
            description
            created
            topic { name }
            host { username }
        }
    }
`;

export const ROOMS_NOT_PARTICIPATED_BY_USER_QUERY = gql`
    query RoomsNotParticipatedByUser($userSlug: String!) {
        roomsNotParticipatedByUser(userSlug: $userSlug) {
            name
            slug
            description
            created
            topic { name }
            host { username }
        }
    }
`;

export const ROOM_MESSAGES_QUERY = gql`
    query RoomMessages($hostSlug: String!, $roomSlug: String!) {
        messages(hostSlug: $hostSlug, roomSlug: $roomSlug) {
            id
            user {
                id
                username
                avatar
            }
            body
            edited
            created
            updated
        }
    }
`;

export const MESSAGES_BY_USER_QUERY = gql`
    query MessagesByUser($userSlug: String!) {
        messagesByUser(userSlug: $userSlug) {
            body
            edited
            updated
            created
            room {
                slug
                name
            }
        } 
    }
`;

export const TOPIC_QUERY = gql`
    query Topics {
        topics {
            name
        }
    }
`;

export const USER_QUERY = gql`
    query User($username: String!) {
        user(userSlug: $username) {
            username
            name
            avatar
            bio
        }
    }
`;
