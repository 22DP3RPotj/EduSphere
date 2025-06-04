import { gql } from "@apollo/client";

export const CREATE_ROOM_MUTATION = gql`
    mutation CreateRoom($name: String!, $topicName: String!, $description: String!) {
        createRoom(name: $name, topicName: $topicName, description: $description) {
            room {
                name
                slug
                description
                topic { name }
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
        $topicName: String,
        $description: String
    ) {
        updateRoom(
            roomId: $roomId,
            topicName: $topicName,
            description: $description
        ) {
            room {
                id
                name
                topic { name }
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
                participants {
                    id
                    username
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
                edited
                updated
            }
        }
    }
`;
