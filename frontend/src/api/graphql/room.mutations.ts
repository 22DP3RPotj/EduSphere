import { gql } from "@apollo/client";

export const CREATE_ROOM_MUTATION = gql`
    mutation CreateRoom($name: String!, $topicNames: [String!]!, $description: String!) {
        createRoom(name: $name, topicNames: $topicNames, description: $description) {
            room {
                id
                name
                slug
                description
                topics { name }
                host {
                    id
                    username 
                }
            }
        }
    }
`;

export const DELETE_ROOM_MUTATION = gql`
    mutation DeleteRoom($roomId: UUID!) {
        deleteRoom(roomId: $roomId) {
            success
        }
    }
`;

export const UPDATE_ROOM_MUTATION = gql`
    mutation UpdateRoom(
        $roomId: UUID!,
        $topicNames: [String!],
        $description: String
    ) {
        updateRoom(
            roomId: $roomId,
            topicNames: $topicNames,
            description: $description
        ) {
            room {
                id
                name
                topics { name }
                description
                participants {
                    id
                    avatar
                    username
                }
                host {
                    id
                    username
                    avatar
                }
            }    
        }
    }
`;

export const JOIN_ROOM_MUTATION = gql`
    mutation JoinRoom($roomId: UUID!) {
        joinRoom(roomId: $roomId) {
            room {
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
                }
                topics {
                    name
                }
            }
        }
    }
`;

export const DELETE_MESSAGE_MUTATION = gql`
    mutation DeleteMessage($messageId: UUID!) {
        deleteMessage(messageId: $messageId) {
            success
        }
    }
`;

export const UPDATE_MESSAGE_MUTATION = gql`
    mutation UpdateMessage($messageId: UUID!, $body: String!) {
        updateMessage(messageId: $messageId, body: $body) {
            message {
                body
                isEdited
                updatedAt
            }
        }
    }
`;
