import { gql } from "@apollo/client/core";
import { apolloClient } from "./apollo";

// GraphQL Mutation to Create Room
const CREATE_ROOM_MUTATION = gql`
  mutation CreateRoom($name: String!, $topicName: String!, $description: String) {
    createRoom(name: $name, topicName: $topicName, description: $description) {
      room {
        name
        description
        topic { name }
        host { username }
      }
    }
  }
`;

export async function createRoom(name, topic_name, description) {
  const { mutate } = apolloClient;
  const response = await mutate({
    mutation: CREATE_ROOM_MUTATION,
    variables: {
      name: name,
      topicName: topic_name,
      description: description
    },
  });

  return response.data.createRoom.room;
}

const DELETE_ROOM_MUTATION = gql`
  mutation DeleteRoom($hostSlug: String!, $roomSlug: String!) {
    deleteRoom(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      success
    }
  }
`;

export async function deleteRoom(hostSlug, roomSlug) {
  return apolloClient.mutate({
    mutation: DELETE_ROOM_MUTATION,
    variables: { hostSlug, roomSlug }
  });
}

const JOIN_ROOM_MUTATION = gql`
  mutation JoinRoom($hostSlug: String!, $roomSlug: String!) {
    joinRoom(hostSlug: $hostSlug, roomSlug: $roomSlug) {
      room {
        id
        participants {
          id
          username
        }
      }
    }
  }
`;

export async function joinRoom(hostSlug, roomSlug) {
  return apolloClient.mutate({
    mutation: JOIN_ROOM_MUTATION,
    variables: { hostSlug, roomSlug }
  });
}