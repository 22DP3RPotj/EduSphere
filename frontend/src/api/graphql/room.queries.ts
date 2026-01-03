import { gql } from "@apollo/client";

export const ROOM_QUERY = gql`
    query Room($roomId: UUID!) {
        room(roomId: $roomId) {
            id
            name
            slug
            description
            createdAt
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
                user {
                    id
                }
            }
            topics {
                name
            }
        }
    }
`;

export const ROOMS_QUERY = gql`
    query Rooms($hostSlug: String, $search: String, $topics: [String]) {
        rooms(hostSlug: $hostSlug, search: $search, topics: $topics) {
            id
            name
            slug
            description
            createdAt
            topics {
                name
            }
            host { username }
        }
    }
`;

export const USER_WITH_ROOMS_QUERY = gql`
    query UserWithRooms($userSlug: String!) {
        user(userSlug: $userSlug) {
            id
            username
            name
            avatar
            bio
        }
        roomsParticipatedByUser(userSlug: $userSlug) {
            id
            name
            slug
            description
            createdAt
            topics { name }
            host { username }
        }
        roomsNotParticipatedByUser(userSlug: $userSlug) {
            id
            name
            slug
            description
            createdAt
            topics { name }
            host { username }
        }
    }
`;

// Combined query for initial page load - gets rooms and topics together
export const HOMEPAGE_INITIAL_QUERY = gql`
    query HomepageInitial($search: String, $topics: [String]) {
        rooms(search: $search, topics: $topics) {
            id
            name
            slug
            description
            createdAt
            topics {
                name
            }
            host { username }
        }
        topics {
            name
        }
    }
`;

export const ROOMS_PARTICIPATED_BY_USER_QUERY = gql`
    query RoomsParticipatedByUser($userSlug: String!) {
        roomsParticipatedByUser(userSlug: $userSlug) {
            id
            name
            slug
            description
            createdAt
            topics { name }
            host { username }
        }
    }
`;

export const ROOMS_NOT_PARTICIPATED_BY_USER_QUERY = gql`
    query RoomsNotParticipatedByUser($userSlug: String!) {
        roomsNotParticipatedByUser(userSlug: $userSlug) {
            id
            name
            slug
            description
            createdAt
            topics { name }
            host { username }
        }
    }
`;

export const ROOM_MESSAGES_QUERY = gql`
    query RoomMessages($roomId: UUID!) {
        messages(roomId: $roomId) {
            id
            user {
                id
                username
                avatar
            }
            body
            isEdited
            createdAt
            updatedAt
        }
    }
`;

export const MESSAGES_BY_USER_QUERY = gql`
    query MessagesByUser($userSlug: String!) {
        messagesByUser(userSlug: $userSlug) {
            id
            body
            isEdited
            updatedAt
            createdAt
            room {
                id
                slug
                name
                host {
                    username
                }
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
            id
            username
            name
            avatar
            bio
        }
    }
`;