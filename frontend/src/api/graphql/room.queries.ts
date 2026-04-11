import { gql } from "@apollo/client";

export const ROOM_QUERY = gql`
    query Room($roomId: UUID!) {
        room(roomId: $roomId) {
            id
            name
            description
            createdAt
            host {
                id
                name
                username
                avatar
            }
            participants {
                id
                role
                joinedAt
                user {
                    id
                    name
                    username
                    avatar
                }
            }
            topics {
                name
            }
        }
    }
`;

export const ROOMS_QUERY = gql`
    query Rooms($hostId: UUID!, $search: String, $topics: [String]) {
        rooms(hostId: $hostId, search: $search, topics: $topics) {
            id
            name
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
    query UserWithRooms($userId: UUID!) {
        user(userId: $userId) {
            id
            username
            name
            avatar
            bio
            language
        }
        roomsParticipatedByUser(userId: $userId) {
            id
            name
            description
            createdAt
            topics { name }
            host { username }
        }
        roomsNotParticipatedByUser(userId: $userId) {
            id
            name
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
    query RoomsParticipatedByUser($userId: UUID!) {
        roomsParticipatedByUser(userId: $userId) {
            id
            name
            description
            createdAt
            topics { name }
            host { username }
        }
    }
`;

export const ROOMS_NOT_PARTICIPATED_BY_USER_QUERY = gql`
    query RoomsNotParticipatedByUser($userId: UUID!) {
        roomsNotParticipatedByUser(userId: $userId) {
            id
            name
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
            author {
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
    query MessagesByUser($userId: UUID!) {
        messagesByUser(userId: $userId) {
            id
            body
            isEdited
            updatedAt
            createdAt
            room {
                id
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
    query User($userId: UUID!) {
        user(userId: $userId) {
            id
            username
            name
            avatar
            bio
            language
        }
    }
`;