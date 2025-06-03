# API Documentation

> **Relevant source files**
> * [backend/core/admin.py](../backend/core/admin.py)
> * [backend/core/graphql/mutations.py](../backend/core/graphql/mutations.py)
> * [backend/core/graphql/queries.py](../backend/core/graphql/queries.py)
> * [frontend/src/api/graphql/room.mutations.ts](../frontend/src/api/graphql/room.mutations.ts)
> * [frontend/src/api/graphql/room.queries.ts](../frontend/src/api/graphql/room.queries.ts)
> * [frontend/src/api/room.api.ts](../frontend/src/api/room.api.ts)
> * [frontend/src/views/Home.vue](../frontend/src/views/HomePage.vue)
> * [frontend/src/views/RoomDetail.vue](../frontend/src/views/RoomDetail.vue)
> * [scripts/setup.sh](../scripts/setup.sh)

This document provides comprehensive reference for all API interfaces available in the EduSphere system. It covers the GraphQL API for data operations, WebSocket API for real-time messaging, and authentication mechanisms. For detailed implementation guides, see [Frontend Development Guide](./Frontend-Development-Guide.md) and [Backend Development Guide](./Backend-Development-Guide.md). For real-time messaging specifics, see [Real-time Messaging](./Real-time-Messaging.md).

## API Architecture Overview

EduSphere exposes three primary API interfaces that work together to provide a complete chat platform experience.

```mermaid
flowchart TD

VueApp["Vue.js Frontend"]
ExternalClients["External Clients"]
ApolloClient["Apollo Client<br>GraphQL Transport"]
WebSocketClient["WebSocket Client<br>Real-time Transport"]
GraphQLEndpoint["/graphql/<br>GraphQL API"]
WebSocketEndpoint["/ws/chat/<br>WebSocket API"]
StaticEndpoint["/media/<br>Static Files"]
QueryClass["Query Class<br>Data Fetching"]
MutationClass["Mutation Class<br>Data Modification"]
TypeSystem["Type System<br>RoomType, UserType, MessageType"]
ChatConsumer["ChatConsumer<br>Real-time Messaging"]
JWTMiddleware["JWTMiddleware<br>WebSocket Authentication"]
DjangoModels["Django Models<br>Room, User, Message, Topic"]
PostgreSQL["PostgreSQL<br>Primary Database"]
Redis["Redis<br>Channel Layer"]

    VueApp --> ApolloClient
    VueApp --> WebSocketClient
    ExternalClients --> GraphQLEndpoint
    ExternalClients --> WebSocketEndpoint
    ApolloClient --> GraphQLEndpoint
    WebSocketClient --> WebSocketEndpoint
    GraphQLEndpoint --> QueryClass
    GraphQLEndpoint --> MutationClass
    WebSocketEndpoint --> ChatConsumer
    WebSocketEndpoint --> JWTMiddleware
    QueryClass --> DjangoModels
    MutationClass --> DjangoModels
    ChatConsumer --> DjangoModels
    ChatConsumer --> Redis
subgraph Data_Layer ["Data Layer"]
    DjangoModels
    PostgreSQL
    Redis
    DjangoModels --> PostgreSQL
end

subgraph WebSocket_Consumers ["WebSocket Consumers"]
    ChatConsumer
    JWTMiddleware
end

subgraph Core_GraphQL_Schema ["Core GraphQL Schema"]
    QueryClass
    MutationClass
    TypeSystem
    QueryClass --> TypeSystem
    MutationClass --> TypeSystem
end

subgraph Django_Backend_APIs ["Django Backend APIs"]
    GraphQLEndpoint
    WebSocketEndpoint
    StaticEndpoint
end

subgraph API_Gateway_Layer ["API Gateway Layer"]
    ApolloClient
    WebSocketClient
end

subgraph Client_Applications ["Client Applications"]
    VueApp
    ExternalClients
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`apollo.client.ts`](../frontend/src/api/apollo.client.ts) | — |
| [`queries.py`](../backend/core/graphql/queries.py#L1-L168) | L1–L168 |
| [`mutations.py`](../backend/core/graphql/mutations.py#L1-L244) | L1–L244 |

## GraphQL API Structure

The GraphQL API is implemented through Django Graphene and provides both query and mutation operations. The schema is organized around core entities: rooms, users, messages, and topics.

### Schema Organization

```mermaid
flowchart TD

QueryRoot["Query<br>backend.core.graphql.queries"]
MutationRoot["Mutation<br>backend.core.graphql.mutations"]
RoomQueries["Room Queries<br>rooms, room, rooms_participated_by_user"]
UserQueries["User Queries<br>users, user, me, auth_status"]
MessageQueries["Message Queries<br>messages, messages_by_user"]
TopicQueries["Topic Queries<br>topics"]
RoomMutations["Room Mutations<br>CreateRoom, UpdateRoom, DeleteRoom, JoinRoom"]
UserMutations["User Mutations<br>RegisterUser, UpdateUser"]
MessageMutations["Message Mutations<br>UpdateMessage, DeleteMessage"]
AuthMutations["Auth Mutations<br>ObtainJSONWebToken, RefreshToken"]
CoreTypes["Core Types<br>RoomType, UserType, MessageType, TopicType"]
ResponseTypes["Response Types<br>AuthStatusType"]

    QueryRoot --> RoomQueries
    QueryRoot --> UserQueries
    QueryRoot --> MessageQueries
    QueryRoot --> TopicQueries
    MutationRoot --> RoomMutations
    MutationRoot --> UserMutations
    MutationRoot --> MessageMutations
    MutationRoot --> AuthMutations
    RoomQueries --> CoreTypes
    UserQueries --> CoreTypes
    MessageQueries --> CoreTypes
    TopicQueries --> CoreTypes
    RoomMutations --> CoreTypes
    UserMutations --> CoreTypes
    MessageMutations --> CoreTypes
    AuthMutations --> ResponseTypes
subgraph Type_System ["Type System"]
    CoreTypes
    ResponseTypes
end

subgraph Mutation_Operations ["Mutation Operations"]
    RoomMutations
    UserMutations
    MessageMutations
    AuthMutations
end

subgraph Query_Operations ["Query Operations"]
    RoomQueries
    UserQueries
    MessageQueries
    TopicQueries
end

subgraph GraphQL_Schema_Root ["GraphQL Schema Root"]
    QueryRoot
    MutationRoot
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`queries.py`](../backend/core/graphql/queries.py#L8-L168) | L8–L168 |
| [`mutations.py`](../backend/core/graphql/mutations.py#L225-L244) | L225–L244 |

### Key Query Operations

| Query | Purpose | Authentication | Parameters |
| --- | --- | --- | --- |
| `rooms` | Fetch filtered room list | Optional | `host_slug`, `search`, `topic` |
| `room` | Fetch single room details | Optional | `host_slug`, `room_slug` |
| `messages` | Fetch room messages | Optional | `host_slug`, `room_slug` |
| `topics` | Fetch available topics | None | `search`, `min_rooms` |
| `user` | Fetch user profile | Optional | `user_slug` |
| `me` | Fetch current user | Required | None |
| `auth_status` | Check authentication status | None | None |

### Key Mutation Operations

| Mutation | Purpose | Authentication | Parameters |
| --- | --- | --- | --- |
| `createRoom` | Create new room | Required | `name`, `topic_name`, `description` |
| `updateRoom` | Update room details | Required (host only) | `host_slug`, `room_slug`, fields |
| `deleteRoom` | Delete room | Required (host only) | `host_slug`, `room_slug` |
| `joinRoom` | Join as participant | Required | `host_slug`, `room_slug` |
| `updateMessage` | Edit message content | Required (author only) | `message_id`, `body` |
| `deleteMessage` | Delete message | Required (author only) | `message_id` |
| `registerUser` | Create user account | None | `username`, `name`, `email`, `password1`, `password2` |
| `updateUser` | Update user profile | Required | `username`, `name`, `bio`, `avatar` |

**Sources:**

| File | Lines |
|------|-------|
| [`queries.py`](../backend/core/graphql/queries.py#L9-L51) | L9–L51 |
| [`mutations.py`](../backend/core/graphql/mutations.py#L76-L233) | L76–L233 |

## Frontend API Integration

The Vue.js frontend implements a structured API layer that wraps GraphQL operations and WebSocket communication.

### API Client Architecture

```mermaid
flowchart TD

ApiWrapper["useApiWrapper<br>Error Handling"]
RoomApi["useRoomApi<br>Room Operations"]
AuthApi["useAuthApi<br>Authentication"]
WebSocketApi["useWebSocket<br>Real-time Communication"]
ApolloClient["apolloClient<br>GraphQL Transport"]
QueryDefinitions["GraphQL Queries<br>ROOM_QUERY, ROOMS_QUERY"]
MutationDefinitions["GraphQL Mutations<br>CREATE_ROOM_MUTATION"]
WebSocketConnection["WebSocket Connection<br>/ws/chat/"]
MessageHandlers["Message Handlers<br>sendMessage, deleteMessage"]
HomeView["Home.vue<br>Room Listings"]
RoomDetailView["RoomDetail.vue<br>Chat Interface"]

    HomeView --> RoomApi
    RoomDetailView --> RoomApi
    RoomDetailView --> WebSocketApi
    RoomApi --> ApolloClient
    AuthApi --> ApolloClient
    WebSocketApi --> WebSocketConnection
    WebSocketApi --> MessageHandlers
subgraph Vue_Components ["Vue Components"]
    HomeView
    RoomDetailView
end

subgraph WebSocket_Layer ["WebSocket Layer"]
    WebSocketConnection
    MessageHandlers
end

subgraph GraphQL_Client ["GraphQL Client"]
    ApolloClient
    QueryDefinitions
    MutationDefinitions
    ApolloClient --> QueryDefinitions
    ApolloClient --> MutationDefinitions
end

subgraph Frontend_API_Layer ["Frontend API Layer"]
    ApiWrapper
    RoomApi
    AuthApi
    WebSocketApi
    RoomApi --> ApiWrapper
    AuthApi --> ApiWrapper
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`room.api.ts`](../frontend/src/api/room.api.ts#L20-L187) | L20–L187 |
| [`room.queries.ts`](../frontend/src/api/graphql/room.queries.ts#L1-L122) | L1–L122 |
| [`room.mutations.ts`](../frontend/src/api/graphql/room.mutations.ts#L1-L93) | L1–L93 |

### Room API Functions

The `useRoomApi` composable provides methods for room management:

| Function | GraphQL Operation | Purpose |
| --- | --- | --- |
| `fetchRoom()` | `ROOM_QUERY` | Get room details and participants |
| `fetchRoomMessages()` | `ROOM_MESSAGES_QUERY` | Get room message history |
| `createRoom()` | `CREATE_ROOM_MUTATION` | Create new room |
| `updateRoom()` | `UPDATE_ROOM_MUTATION` | Update room properties |
| `deleteRoom()` | `DELETE_ROOM_MUTATION` | Delete room |
| `joinRoom()` | `JOIN_ROOM_MUTATION` | Join room as participant |
| `fetchTopics()` | `TOPIC_QUERY` | Get available topics |

**Sources:**

| File | Lines |
|------|-------|
| [`room.api.ts`](../frontend/src/api/room.api.ts#L24-L174) | L24–L174 |

## WebSocket API Protocol

Real-time messaging uses WebSocket connections with JSON message protocol. Messages are handled by Django Channels consumers.

### WebSocket Message Types

```mermaid
flowchart TD

SendMessage["Send Message<br>{type: 'send_message', body: string}"]
UpdateMessage["Update Message<br>{type: 'update_message', message_id: UUID, body: string}"]
DeleteMessage["Delete Message<br>{type: 'delete_message', message_id: UUID}"]
MessageReceived["Message Received<br>{type: 'message_received', message: object}"]
MessageUpdated["Message Updated<br>{type: 'message_updated', message: object}"]
MessageDeleted["Message Deleted<br>{type: 'message_deleted', message_id: UUID}"]
ErrorMessage["Error<br>{type: 'error', message: string}"]
ChatConsumer["ChatConsumer<br>backend.chat.consumers"]
MessageHandlers["receive_json()<br>handle_send_message()<br>handle_update_message()"]

    SendMessage --> ChatConsumer
    UpdateMessage --> ChatConsumer
    DeleteMessage --> ChatConsumer
    MessageHandlers --> MessageReceived
    MessageHandlers --> MessageUpdated
    MessageHandlers --> MessageDeleted
    MessageHandlers --> ErrorMessage
subgraph WebSocket_Consumer ["WebSocket Consumer"]
    ChatConsumer
    MessageHandlers
    ChatConsumer --> MessageHandlers
end

subgraph Server_to_Client_Messages ["Server to Client Messages"]
    MessageReceived
    MessageUpdated
    MessageDeleted
    ErrorMessage
end

subgraph Client_to_Server_Messages ["Client to Server Messages"]
    SendMessage
    UpdateMessage
    DeleteMessage
end
```

### WebSocket Connection Flow

1. **Connection**: Client connects to `/ws/chat/{host_slug}/{room_slug}/`
2. **Authentication**: JWT token validated via WebSocket middleware
3. **Room Validation**: User must be room participant
4. **Message Exchange**: JSON messages for real-time operations
5. **Broadcasting**: Messages broadcast to all room participants

**Sources:**

| File | Lines |
|------|-------|
| [`RoomDetail.vue`](../frontend/src/views/RoomDetail.vue#L29-L36) | L29–L36 |
| [`websocket.ts`](../frontend/src/api/websocket.ts) | — |

## Authentication System

Authentication uses JWT tokens for both HTTP and WebSocket connections.

### Authentication Flow

```mermaid
sequenceDiagram
  participant Frontend Client
  participant GraphQL API
  participant JWT Authentication
  participant WebSocket API
  participant Database

  note over Frontend Client,Database: Login Flow
  Frontend Client->>GraphQL API: tokenAuth mutation
  GraphQL API->>JWT Authentication: Validate credentials
  JWT Authentication->>Database: Check user
  Database-->>JWT Authentication: User data
  JWT Authentication-->>GraphQL API: JWT token + user
  GraphQL API-->>Frontend Client: Token response
  note over Frontend Client,Database: Protected GraphQL Request
  Frontend Client->>GraphQL API: Query with Authorization header
  GraphQL API->>JWT Authentication: Validate JWT token
  JWT Authentication-->>GraphQL API: User context
  GraphQL API->>Database: Execute query
  Database-->>GraphQL API: Data
  GraphQL API-->>Frontend Client: Query response
  note over Frontend Client,Database: WebSocket Connection
  Frontend Client->>WebSocket API: Connect with JWT token
  WebSocket API->>JWT Authentication: Validate JWT token
  JWT Authentication-->>WebSocket API: User context
  WebSocket API-->>Frontend Client: Connection accepted
```

### Authentication Mutations

| Mutation | Purpose | Response |
| --- | --- | --- |
| `tokenAuth` | Login and get JWT token | `{token, user, success}` |
| `verifyToken` | Validate existing token | `{payload}` |
| `refreshToken` | Refresh expired token | `{token, refreshToken}` |
| `deleteToken` | Logout (clear token) | `{deleted}` |

**Sources:**

| File | Lines |
|------|-------|
| [`mutations.py`](../backend/core/graphql/mutations.py#L15-L22) | L15–L22 |
| [`mutations.py`](../backend/core/graphql/mutations.py#L235-L241) | L235–L241 |

## Error Handling

The API implements consistent error handling across GraphQL and WebSocket interfaces.

### GraphQL Error Format

```json
{
  "errors": [
    {
      "message": "Room not found",
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

### Common Error Codes

| Code | Description | When Used |
| --- | --- | --- |
| `NOT_FOUND` | Resource doesn't exist | Room, user, or message not found |
| `PERMISSION_DENIED` | Access forbidden | User lacks permission for operation |
| `VALIDATION_ERROR` | Invalid input data | Form validation failures |
| `AUTHENTICATION_ERROR` | Invalid credentials | Login failures |

### Frontend Error Wrapper

The `useApiWrapper` composable provides consistent error handling:

```javascript
// Wraps API calls with error handling
const response = await apiWrapper.callApi(
  async () => apolloClient.query({
    query: ROOM_QUERY,
    variables: { hostSlug, roomSlug }
  })
);
```

**Sources:**

| File | Lines |
|------|-------|
| [`queries.py`](../backend/core/graphql/queries.py#L88-L88) | L88 |
| [`mutations.py`](../backend/core/graphql/mutations.py#L121-L121) | L121 |
| [`room.api.ts`](../frontend/src/api/room.api.ts#L26-L32) | L26–L32 |

## API Usage Examples

### Fetching Rooms with Filters

```javascript
// GraphQL query with search and topic filters
const { data } = await apolloClient.query({
  query: ROOMS_QUERY,
  variables: {
    search: "javascript",
    topic: ["Programming", "Web Development"]
  }
});
```

### Creating a Room

```javascript
// Create room mutation
const { data } = await apolloClient.mutate({
  mutation: CREATE_ROOM_MUTATION,
  variables: {
    name: "JavaScript Discussion",
    topicName: "Programming",
    description: "Talk about JavaScript frameworks"
  }
});
```

### Real-time Message Sending

```javascript
// WebSocket message
const message = {
  type: 'send_message',
  body: 'Hello everyone!'
};
websocket.send(JSON.stringify(message));
```

**Sources:**

| File | Lines |
|------|-------|
| [`Home.vue`](../frontend/src/views/HomePage.vue#L400-L404) | L400–L404 |
| [`room.api.ts`](../frontend/src/api/room.api.ts#L58-L78) | L58–L78 |
| [`RoomDetail.vue`](../frontend/src/views/RoomDetail.vue#L156-L165) | L156–L165 |
