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
