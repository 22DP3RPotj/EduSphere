# GraphQL Queries

> **Relevant source files**
> * [backend/core/graphql/queries.py](../backend/core/graphql/queries.py)
> * [frontend/src/App.vue](../frontend/src/App.vue)
> * [frontend/src/api/graphql/auth.queries.ts](../frontend/src/api/graphql/auth.queries.ts)
> * [frontend/src/api/graphql/room.queries.ts](../frontend/src/api/graphql/room.queries.ts)
> * [frontend/src/views/Home.vue](../frontend/src/views/HomePage.vue)
> * [frontend/src/views/RoomDetail.vue](../frontend/src/views/RoomDetail.vue)

This document covers the GraphQL query operations in the EduSphere platform, which provide read-only data fetching capabilities for rooms, users, messages, and topics. These queries form the primary data access layer between the Vue.js frontend and Django backend.

For information about data modification operations, see [GraphQL Mutations](./GraphQL-Mutations.md). For real-time communication capabilities, see [WebSocket API](./WebSocket-API.md).

## GraphQL Query Architecture

The GraphQL query system follows a client-server architecture where frontend queries are resolved by backend resolvers that interact with Django models.

```mermaid
flowchart TD

VueComponents["Vue Components"]
ApolloClient["Apollo Client"]
QueryFiles["Query Definition Files"]
GraphQLEndpoint["/graphql/ Endpoint"]
QueryParser["Query Parser"]
QueryClass["Query Class"]
Resolvers["Resolver Methods"]
DjangoModels["Django Models"]
PostgreSQL["PostgreSQL Database"]

    QueryFiles --> GraphQLEndpoint
    QueryParser --> QueryClass
    DjangoModels --> PostgreSQL
subgraph Data_Layer ["Data Layer"]
    PostgreSQL
end

subgraph Backend_Layer ["Backend Layer"]
    QueryClass
    Resolvers
    DjangoModels
    QueryClass --> Resolvers
    Resolvers --> DjangoModels
end

subgraph GraphQL_Interface ["GraphQL Interface"]
    GraphQLEndpoint
    QueryParser
    GraphQLEndpoint --> QueryParser
end

subgraph Frontend_Layer ["Frontend Layer"]
    VueComponents
    ApolloClient
    QueryFiles
    VueComponents --> ApolloClient
    ApolloClient --> QueryFiles
end
```

Sources: [frontend/src/api/graphql/room.queries.ts L1-L122](../frontend/src/api/graphql/room.queries.ts#L1-L122)

 [backend/core/graphql/queries.py L1-L168](../backend/core/graphql/queries.py#L1-L168)

## Room Queries

The room query system provides comprehensive access to room data with filtering, search, and relationship capabilities.

### Core Room Queries

| Query Name | Purpose | Key Parameters | Return Type |
| --- | --- | --- | --- |
| `rooms` | List all rooms with filtering | `hostSlug`, `search`, `topic` | `List[RoomType]` |
| `room` | Get single room details | `hostSlug`, `roomSlug` | `RoomType` |
| `roomsParticipatedByUser` | User's joined rooms | `userSlug` | `List[RoomType]` |
| `roomsNotParticipatedByUser` | Recommended rooms | `userSlug` | `List[RoomType]` |

### Room Query Data Flow

```mermaid
flowchart TD

ROOM_QUERY["ROOM_QUERY"]
ROOMS_QUERY["ROOMS_QUERY"]
ROOMS_PARTICIPATED["ROOMS_PARTICIPATED_BY_USER_QUERY"]
ROOMS_NOT_PARTICIPATED["ROOMS_NOT_PARTICIPATED_BY_USER_QUERY"]
resolve_room["resolve_room"]
resolve_rooms["resolve_rooms"]
resolve_rooms_participated["resolve_rooms_participated_by_user"]
resolve_rooms_not_participated["resolve_rooms_not_participated_by_user"]
RoomModel["Room Model"]
UserModel["User Model"]
TopicModel["Topic Model"]

    ROOM_QUERY --> resolve_room
    ROOMS_QUERY --> resolve_rooms
    ROOMS_PARTICIPATED --> resolve_rooms_participated
    ROOMS_NOT_PARTICIPATED --> resolve_rooms_not_participated
    resolve_room --> RoomModel
    resolve_rooms --> RoomModel
    resolve_rooms_participated --> RoomModel
    resolve_rooms_not_participated --> RoomModel
subgraph Database_Models ["Database Models"]
    RoomModel
    UserModel
    TopicModel
    RoomModel --> UserModel
    RoomModel --> TopicModel
end

subgraph Backend_Resolvers ["Backend Resolvers"]
    resolve_room
    resolve_rooms
    resolve_rooms_participated
    resolve_rooms_not_participated
end

subgraph Frontend_Queries ["Frontend Queries"]
    ROOM_QUERY
    ROOMS_QUERY
    ROOMS_PARTICIPATED
    ROOMS_NOT_PARTICIPATED
end
```

Sources: [frontend/src/api/graphql/room.queries.ts L3-L67](../frontend/src/api/graphql/room.queries.ts#L3-L67)

 [backend/core/graphql/queries.py L65-L106](../backend/core/graphql/queries.py#L65-L106)

### Room Query Fields

The `ROOM_QUERY` provides detailed room information including relationships:

```
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
```

Sources: [frontend/src/api/graphql/room.queries.ts L3-L26](../frontend/src/api/graphql/room.queries.ts#L3-L26)

## User and Authentication Queries

The authentication system provides user data access and session management through dedicated queries.

### Authentication Query Types

| Query Name | Purpose | Authentication Required | Return Type |
| --- | --- | --- | --- |
| `me` | Get current user | Yes | `UserType` |
| `user` | Get user by slug | No | `UserType` |
| `users` | Search users | No | `List[UserType]` |
| `authStatus` | Get auth state | No | `AuthStatusType` |

### Authentication Query Flow

```mermaid
flowchart TD

GET_USER["GET_USER"]
GET_AUTH_STATUS["GET_AUTH_STATUS"]
USER_QUERY["USER_QUERY"]
resolve_me["resolve_me (@login_required)"]
resolve_auth_status["resolve_auth_status"]
resolve_user["resolve_user"]
JWTMiddleware["JWT Middleware"]
UserContext["info.context.user"]

    GET_USER --> resolve_me
    GET_AUTH_STATUS --> resolve_auth_status
    USER_QUERY --> resolve_user
    resolve_me --> JWTMiddleware
    resolve_auth_status --> UserContext
    resolve_user --> UserContext
subgraph Authentication_Context ["Authentication Context"]
    JWTMiddleware
    UserContext
end

subgraph Backend_Resolvers ["Backend Resolvers"]
    resolve_me
    resolve_auth_status
    resolve_user
end

subgraph Auth_Queries ["Auth Queries"]
    GET_USER
    GET_AUTH_STATUS
    USER_QUERY
end
```

Sources: [frontend/src/api/graphql/auth.queries.ts L1-L26](../frontend/src/api/graphql/auth.queries.ts#L1-L26)

 [backend/core/graphql/queries.py L54-L67](../backend/core/graphql/queries.py#L54-L67)

## Message Queries

Message queries provide access to chat messages with room-based and user-based filtering.

### Message Query Operations

The system supports two primary message query patterns:

1. **Room-based messages**: `ROOM_MESSAGES_QUERY` retrieves all messages for a specific room
2. **User-based messages**: `MESSAGES_BY_USER_QUERY` retrieves all messages by a specific user

```mermaid
flowchart TD

ROOM_MESSAGES["ROOM_MESSAGES_QUERY"]
MESSAGES_BY_USER["MESSAGES_BY_USER_QUERY"]
resolve_messages["resolve_messages"]
resolve_messages_by_user["resolve_messages_by_user"]
RoomLookup["Room.objects.get()"]
UserLookup["User.objects.get()"]
MessageFilter["message_set.all()"]

    ROOM_MESSAGES --> resolve_messages
    MESSAGES_BY_USER --> resolve_messages_by_user
    resolve_messages --> RoomLookup
    resolve_messages_by_user --> UserLookup
subgraph Query_Logic ["Query Logic"]
    RoomLookup
    UserLookup
    MessageFilter
    RoomLookup --> MessageFilter
    UserLookup --> MessageFilter
end

subgraph Resolvers ["Resolvers"]
    resolve_messages
    resolve_messages_by_user
end

subgraph Message_Queries ["Message Queries"]
    ROOM_MESSAGES
    MESSAGES_BY_USER
end
```

Sources: [frontend/src/api/graphql/room.queries.ts L69-L102](../frontend/src/api/graphql/room.queries.ts#L69-L102)

 [backend/core/graphql/queries.py L132-L149](../backend/core/graphql/queries.py#L132-L149)

### Message Query Implementation

The `ROOM_MESSAGES_QUERY` includes user relationship data for message display:

```
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
```

Sources: [frontend/src/api/graphql/room.queries.ts L69-L84](../frontend/src/api/graphql/room.queries.ts#L69-L84)

## Topic Queries

Topic queries provide access to room categorization data with usage statistics.

### Topic Query Structure

The `TOPIC_QUERY` retrieves all available topics for filtering and room creation:

```
query Topics {
    topics {
        name
    }
}
```

The backend resolver `resolve_topics` supports advanced filtering with room count annotations:

```python
def resolve_topics(self, info, search=None, min_rooms=None):
    queryset = Topic.objects.annotate(
        room_count=Count('room')
    )
    # Additional filtering logic
    return queryset.order_by('-room_count')
```

Sources: [frontend/src/api/graphql/room.queries.ts L104-L110](../frontend/src/api/graphql/room.queries.ts#L104-L110)

 [backend/core/graphql/queries.py L108-L119](../backend/core/graphql/queries.py#L108-L119)

## Query Usage Patterns

The application demonstrates several common query usage patterns that show how GraphQL queries integrate with Vue.js components.

### Component Query Integration

```mermaid
flowchart TD

ComponentMounted["onMounted()"]
FetchRooms["fetchRooms()"]
FetchTopics["fetchTopics()"]
FetchUserRooms["fetchUserRooms()"]
RoomsQuery["apolloClient.query(ROOMS_QUERY)"]
TopicsQuery["apolloClient.query(TOPIC_QUERY)"]
UserRoomsQuery["apolloClient.query(ROOMS_PARTICIPATED_BY_USER_QUERY)"]
QueryResolvers["GraphQL Resolvers"]
DatabaseQueries["Database Queries"]

    FetchRooms --> RoomsQuery
    FetchTopics --> TopicsQuery
    FetchUserRooms --> UserRoomsQuery
    RoomsQuery --> QueryResolvers
    TopicsQuery --> QueryResolvers
    UserRoomsQuery --> QueryResolvers
subgraph Backend_Processing ["Backend Processing"]
    QueryResolvers
    DatabaseQueries
    QueryResolvers --> DatabaseQueries
end

subgraph Apollo_Client_Calls ["Apollo Client Calls"]
    RoomsQuery
    TopicsQuery
    UserRoomsQuery
end

subgraph Homevue_Component ["Home.vue Component"]
    ComponentMounted
    FetchRooms
    FetchTopics
    FetchUserRooms
    ComponentMounted --> FetchRooms
    ComponentMounted --> FetchTopics
    ComponentMounted --> FetchUserRooms
end
```

Sources: [frontend/src/views/Home.vue L390-L470](../frontend/src/views/HomePage.vue#L390-L470)

 [frontend/src/views/RoomDetail.vue L172-L188](../frontend/src/views/RoomDetail.vue#L172-L188)

### Error Handling and Loading States

The query system implements consistent error handling patterns:

1. **Loading states**: Components track loading state during query execution
2. **Error handling**: GraphQL errors are caught and displayed via notifications
3. **Network policies**: Queries use `fetchPolicy: 'network-only'` for fresh data

Sources: [frontend/src/views/Home.vue L392-L414](../frontend/src/views/HomePage.vue#L392-L414)

 [backend/core/graphql/queries.py L88-L100](../backend/core/graphql/queries.py#L88-L100)