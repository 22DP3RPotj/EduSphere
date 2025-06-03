# Testing

> **Relevant source files**
> * [backend/core/apps.py](../backend/core/apps.py)
> * [backend/core/tests/test_mutations.py](../backend/core/tests/test_mutations.py)
> * [backend/core/tests/test_queries.py](../backend/core/tests/test_queries.py)
> * [backend/core/tests/utils.py](../backend/core/tests/utils.py)

This document covers the testing infrastructure and test suite for the EduSphere backend application. The testing system validates GraphQL API functionality, including mutations for data modification and queries for data retrieval, as well as authentication workflows and file upload operations.

For information about backend configuration and Django setup, see [Backend Configuration](./Configuration.md). For details about data models and relationships being tested, see [Data Models and Forms](./Data-Models-and-Forms.md).

## Testing Framework Overview

The EduSphere backend uses Django's testing framework extended with GraphQL-specific testing capabilities. The test suite is built around `JSONWebTokenTestCase` from the `graphql_jwt.testcases` module, which provides JWT authentication testing support for GraphQL operations.

### Test Architecture

```mermaid
flowchart TD

JSONWebTokenTestCase["JSONWebTokenTestCase<br>Base Test Class"]
ExecutionResult["ExecutionResult<br>GraphQL Response"]
TestClient["Test Client<br>GraphQL Executor"]
UserMutationsTests["UserMutationsTests<br>User Operations"]
RoomMutationsTests["RoomMutationsTests<br>Room Operations"]
MessageMutationsTests["MessageMutationsTests<br>Message Operations"]
QueryTests["QueryTests<br>Data Queries"]
TestUtils["utils.py<br>Test Helpers"]
TempMedia["TemporaryDirectory<br>File Upload Testing"]
TestData["Test Data Creation<br>Models & Fixtures"]
User["User Model<br>Authentication"]
Room["Room Model<br>Chat Rooms"]
Message["Message Model<br>Messages"]
Topic["Topic Model<br>Room Topics"]

    JSONWebTokenTestCase --> UserMutationsTests
    JSONWebTokenTestCase --> RoomMutationsTests
    JSONWebTokenTestCase --> MessageMutationsTests
    JSONWebTokenTestCase --> QueryTests
    UserMutationsTests --> TestClient
    RoomMutationsTests --> TestClient
    MessageMutationsTests --> TestClient
    QueryTests --> TestClient
    TestUtils --> UserMutationsTests
    TempMedia --> UserMutationsTests
    UserMutationsTests --> User
    RoomMutationsTests --> Room
    RoomMutationsTests --> Topic
    MessageMutationsTests --> Message
    QueryTests --> User
    QueryTests --> Room
    QueryTests --> Message
    QueryTests --> Topic
subgraph Django_Models_Under_Test ["Django Models Under Test"]
    User
    Room
    Message
    Topic
end

subgraph Test_Utilities ["Test Utilities"]
    TestUtils
    TempMedia
    TestData
end

subgraph Test_Categories ["Test Categories"]
    UserMutationsTests
    RoomMutationsTests
    MessageMutationsTests
    QueryTests
end

subgraph Test_Framework_Components ["Test Framework Components"]
    JSONWebTokenTestCase
    ExecutionResult
    TestClient
    TestClient --> ExecutionResult
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`test_mutations.py`](../backend/core/tests/test_mutations.py#L1-L222) | L1–L222 |
| [`test_queries.py`](../backend/core/tests/test_queries.py#L1-L80) | L1–L80 |
| [`utils.py`](../backend/core/tests/utils.py#L1-L11) | L1–L11 |

## Mutation Testing

The mutation testing suite validates all GraphQL mutations that modify data in the system. Tests cover user management, room operations, and message handling with proper authentication and error handling validation.

### User Mutation Tests

The `UserMutationsTests` class in [backend/core/tests/test_mutations.py L13-L133](../backend/core/tests/test_mutations.py#L13-L133)

 tests user-related operations including registration, profile updates, and avatar uploads.

| Test Method | Purpose | Key Validations |
| --- | --- | --- |
| `test_register_user_success` | User registration flow | Username creation, email validation, success response |
| `test_register_user_password_mismatch` | Password validation | Error handling for mismatched passwords |
| `test_update_user_success` | Profile updates | Username changes, authentication required |
| `test_update_user_avatar` | File upload handling | Image upload, file storage, content type validation |

```mermaid
sequenceDiagram
  participant UserMutationsTests
  participant Test Client
  participant GraphQL Schema
  participant Database
  participant Media Storage

  note over UserMutationsTests,Media Storage: User Registration Test Flow
  UserMutationsTests->>Test Client: "Execute registerUser mutation"
  Test Client->>GraphQL Schema: "registerUser(username, email, password1, password2)"
  GraphQL Schema->>Database: "Create User object"
  Database->>GraphQL Schema: "User created successfully"
  GraphQL Schema->>Test Client: "ExecutionResult with user data"
  Test Client->>UserMutationsTests: "Assertion: success = true"
  note over UserMutationsTests,Media Storage: Avatar Upload Test Flow
  UserMutationsTests->>UserMutationsTests: "authenticate(user)"
  UserMutationsTests->>UserMutationsTests: "create SimpleUploadedFile"
  UserMutationsTests->>Test Client: "Execute updateUser mutation with avatar"
  Test Client->>GraphQL Schema: "updateUser(avatar: Upload)"
  GraphQL Schema->>Media Storage: "Store uploaded file"
  GraphQL Schema->>Database: "Update user.avatar field"
  Database->>GraphQL Schema: "User updated"
  GraphQL Schema->>Test Client: "ExecutionResult with avatar path"
  Test Client->>UserMutationsTests: "Assertion: avatar.name.endswith('.jpg')"
```

**Sources:**

| File | Lines |
|------|-------|
| [`test_mutations.py`](../backend/core/tests/test_mutations.py#L23-L133) | L23–L133 |
| [`utils.py`](../backend/core/tests/utils.py#L5-L10) | L5–L10 |

### Room and Message Mutation Tests

The `RoomMutationsTests` and `MessageMutationsTests` classes validate room management and message operations respectively.

```mermaid
flowchart TD

CreateRoom["test_create_room_success<br>Room Creation"]
DeleteRoom["test_delete_room_success<br>Room Deletion"]
DeleteMessage["test_delete_message_success<br>Message Deletion"]
UpdateMessage["test_update_message_success<br>Message Updates"]
SetupAuth["setUp()<br>Create test user"]
ClientAuth["client.authenticate(user)<br>JWT Authentication"]
RoomExists["Room.objects.filter().exists()<br>Existence Checks"]
MessageRefresh["message.refresh_from_db()<br>State Validation"]

    SetupAuth --> CreateRoom
    SetupAuth --> DeleteRoom
    SetupAuth --> DeleteMessage
    SetupAuth --> UpdateMessage
    ClientAuth --> CreateRoom
    ClientAuth --> DeleteRoom
    ClientAuth --> DeleteMessage
    ClientAuth --> UpdateMessage
    CreateRoom --> RoomExists
    DeleteRoom --> RoomExists
    DeleteMessage --> RoomExists
    UpdateMessage --> MessageRefresh
subgraph Data_Validation ["Data Validation"]
    RoomExists
    MessageRefresh
end

subgraph Authentication_Flow ["Authentication Flow"]
    SetupAuth
    ClientAuth
end

subgraph Message_Operations ["Message Operations"]
    DeleteMessage
    UpdateMessage
end

subgraph Room_Operations ["Room Operations"]
    CreateRoom
    DeleteRoom
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`test_mutations.py`](../backend/core/tests/test_mutations.py#L134-L222) | L134–L222 |

## Query Testing

The `QueryTests` class in [backend/core/tests/test_queries.py L6-L80](../backend/core/tests/test_queries.py#L6-L80)

 validates GraphQL queries that retrieve data from the system. These tests ensure proper data filtering, authentication checks, and response formatting.

### Query Test Coverage

| Query | Test Method | Authentication Required | Key Assertions |
| --- | --- | --- | --- |
| `rooms` | `test_rooms_query` | No | Room count, name, description |
| `me` | `test_me_query` | Yes | Current user data |
| `authStatus` | `test_auth_status_authenticated` | Yes | Authentication state |
| `messages` | `test_messages_query` | No | Message content by room |

```mermaid
flowchart TD

QueryTests["QueryTests<br>Main Test Class"]
SetupData["setUp()<br>Test Data Creation"]
ExecuteQuery["client.execute(query)<br>GraphQL Execution"]
AssertResults["Assertion Methods<br>Response Validation"]
TestUser["self.user<br>get_user_model().objects.create_user()"]
TestTopic["self.topic<br>Topic.objects.create()"]
TestRoom["self.room<br>Room.objects.create()"]
TestMessage["self.message<br>Message.objects.create()"]
RoomsQuery["rooms { name description }<br>Public Room List"]
MeQuery["me { username }<br>Current User Info"]
AuthQuery["authStatus { isAuthenticated user }<br>Auth State"]
MessagesQuery["messages(hostSlug, roomSlug) { body }<br>Room Messages"]

    SetupData --> TestUser
    SetupData --> TestTopic
    SetupData --> TestRoom
    SetupData --> TestMessage
    ExecuteQuery --> RoomsQuery
    ExecuteQuery --> MeQuery
    ExecuteQuery --> AuthQuery
    ExecuteQuery --> MessagesQuery
subgraph GraphQL_Queries_Under_Test ["GraphQL Queries Under Test"]
    RoomsQuery
    MeQuery
    AuthQuery
    MessagesQuery
end

subgraph Test_Data_Objects ["Test Data Objects"]
    TestUser
    TestTopic
    TestRoom
    TestMessage
end

subgraph Query_Test_Structure ["Query Test Structure"]
    QueryTests
    SetupData
    ExecuteQuery
    AssertResults
    QueryTests --> SetupData
    QueryTests --> ExecuteQuery
    ExecuteQuery --> AssertResults
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`test_queries.py`](../backend/core/tests/test_queries.py#L6-L80) | L6–L80 |

## Test Utilities and Helpers

### Test Image Creation

The `create_test_image()` function in [backend/core/tests/utils.py L5-L10](../backend/core/tests/utils.py#L5-L10)

 generates test images for file upload testing using the PIL library.

```python
# Function signature and usage
def create_test_image():
    # Creates a 1x1 red JPEG image in memory
    # Returns bytes that can be used with SimpleUploadedFile
```

### Media File Testing

User mutation tests implement temporary media directory management for testing file uploads without affecting the production media storage:

```mermaid
flowchart TD

TempDir["tempfile.TemporaryDirectory()<br>Temporary Storage"]
MediaOverride["override_settings(MEDIA_ROOT)<br>Settings Override"]
SetupMethod["setUp()<br>Enable Override"]
TeardownMethod["tearDown()<br>Cleanup"]
CreateFile["SimpleUploadedFile<br>Test File Creation"]
ExecuteMutation["updateUser mutation<br>Avatar Upload"]
ValidateStorage["user.avatar.name<br>File Path Validation"]

    SetupMethod --> CreateFile
    ValidateStorage --> TeardownMethod
subgraph File_Upload_Test_Flow ["File Upload Test Flow"]
    CreateFile
    ExecuteMutation
    ValidateStorage
    CreateFile --> ExecuteMutation
    ExecuteMutation --> ValidateStorage
end

subgraph Media_Testing_Setup ["Media Testing Setup"]
    TempDir
    MediaOverride
    SetupMethod
    TeardownMethod
    TempDir --> MediaOverride
    MediaOverride --> SetupMethod
    TeardownMethod --> TempDir
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`test_mutations.py`](../backend/core/tests/test_mutations.py#L14-L21) | L14–L21 |
| [`utils.py`](../backend/core/tests/utils.py#L1-L11) | L1–L11 |

## Test Data Management

### Database Test Isolation

Each test class uses Django's transactional test case behavior to ensure test isolation. The `setUp()` method in each test class creates fresh test data:

```mermaid
flowchart TD

SetupMethod["setUp() Method<br>Data Initialization"]
UserCreation["User.objects.create_user()<br>Test User"]
ModelCreation["Topic/Room/Message Creation<br>Related Objects"]
AuthenticateClient["client.authenticate(user)<br>JWT Setup"]
ExecuteTest["Test Method Execution<br>GraphQL Operations"]
DatabaseAssertions["Database State Validation<br>Object Existence/Updates"]
TransactionRollback["Transaction Rollback<br>Automatic Cleanup"]
MediaCleanup["Temporary Directory Cleanup<br>File System"]

    ModelCreation --> AuthenticateClient
    DatabaseAssertions --> TransactionRollback
    DatabaseAssertions --> MediaCleanup
subgraph Test_Cleanup ["Test Cleanup"]
    TransactionRollback
    MediaCleanup
end

subgraph Test_Execution ["Test Execution"]
    AuthenticateClient
    ExecuteTest
    DatabaseAssertions
    AuthenticateClient --> ExecuteTest
    ExecuteTest --> DatabaseAssertions
end

subgraph Test_Data_Creation_Pattern ["Test Data Creation Pattern"]
    SetupMethod
    UserCreation
    ModelCreation
    SetupMethod --> UserCreation
    SetupMethod --> ModelCreation
end
```

### Authentication in Tests

The `JSONWebTokenTestCase` provides the `client.authenticate(user)` method for setting up JWT authentication in tests, simulating authenticated GraphQL requests.

**Sources:**

| File | Lines |
|------|-------|
| [`test_mutations.py`](../backend/core/tests/test_mutations.py#L97-L98) | L97–L98 |
| [`test_queries.py`](../backend/core/tests/test_queries.py#L7-L26) | L7–L26 |

## Running Tests

Tests can be executed using Django's standard test runner. The test suite is organized in the `backend/core/tests/` directory with the following structure:

* `test_mutations.py` - GraphQL mutation testing
* `test_queries.py` - GraphQL query testing
* `utils.py` - Test utility functions

The Django app configuration in [backend/core/apps.py L8-L9](../backend/core/apps.py#L8-L9)

 ensures that GraphQL signals are properly imported during testing, maintaining the same signal handling behavior as in production.

**Sources:**

| File | Lines |
|------|-------|
| [`apps.py`](../backend/core/apps.py#L1-L10) | L1–L10 |
