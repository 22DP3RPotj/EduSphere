import { gql } from "@apollo/client";

export const ROOM_QUERY = gql`
    query GetRoom($hostSlug: String!, $roomSlug: String!) {
        room(hostSlug: $hostSlug, roomSlug: $roomSlug) {
            name
            slug
            description
            created
            host {
                id
                username
                slug
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
            created
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