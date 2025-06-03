# Overview

> **Relevant source files**
> * [README.md](../README.md)
> * [backend/README.md](../backend/README.md)
> * [frontend/README.md](../frontend/README.md)
> * [requirements.txt](../requirements.txt)

## Purpose and Scope

This document provides a comprehensive overview of EduSphere, a full-stack real-time messaging platform designed for educational collaboration. EduSphere combines course management capabilities with real-time chat functionality, built using Django for the backend and Vue.js for the frontend.

This overview covers the system's high-level architecture, core technologies, and primary features. For detailed implementation information, see [System Architecture](./System-Architecture.md#overall-system-architecture) for technical design patterns, [Core Features](./Core-Features.md) for functionality specifics, and [Deployment and Infrastructure](./Deployment-and-Infrastructure.md) for containerization and production setup.

*Sources: [README.md L1-L25](../README.md#L1-L25)*

## System Architecture Overview

EduSphere follows a decoupled architecture pattern with distinct frontend and backend services communicating through GraphQL APIs and WebSocket connections for real-time features.

### High-Level Component Architecture

```mermaid
flowchart TD

Browser["Web Browser"]
VueApp["Vue.js Application<br>frontend/src/"]
Frontend["Vue Frontend Server<br>Port 5173"]
Backend["Django Backend<br>Port 8000"]
NginxProxy["Nginx Reverse Proxy<br>docker/nginx/"]
GraphQLEndpoint["GraphQL API<br>/graphql/"]
WebSocketEndpoint["WebSocket API<br>/ws/"]
AdminInterface["Django Admin<br>/admin/"]
PostgreSQLDB["PostgreSQL Database<br>coredb"]
RedisCache["Redis Cache<br>Channel Layer"]
MediaStorage["Static/Media Files"]
DockerCompose["Docker Compose<br>docker-compose.yml"]
ConfigFiles["Configuration<br>backend/config/"]

    Browser --> NginxProxy
    NginxProxy --> MediaStorage
    Frontend --> GraphQLEndpoint
    Frontend --> WebSocketEndpoint
    Backend --> GraphQLEndpoint
    Backend --> WebSocketEndpoint
    Backend --> AdminInterface
    Backend --> PostgreSQLDB
    Backend --> RedisCache
    WebSocketEndpoint --> RedisCache
    DockerCompose --> Frontend
    DockerCompose --> Backend
    DockerCompose --> PostgreSQLDB
    DockerCompose --> RedisCache
    DockerCompose --> NginxProxy
    ConfigFiles --> Backend
subgraph Infrastructure ["Infrastructure"]
    DockerCompose
    ConfigFiles
end

subgraph Data_Layer ["Data Layer"]
    PostgreSQLDB
    RedisCache
    MediaStorage
end

subgraph API_Layer ["API Layer"]
    GraphQLEndpoint
    WebSocketEndpoint
    AdminInterface
end

subgraph Application_Services ["Application Services"]
    Frontend
    Backend
    NginxProxy
    NginxProxy --> Frontend
    NginxProxy --> Backend
end

subgraph Client_Layer ["Client Layer"]
    Browser
    VueApp
    VueApp --> Browser
end
```

*Sources: [README.md L25-L44](../README.md#L25-L44)

 [README.md L188-L211](../README.md#L188-L211)*

### Technology Stack Overview

```mermaid
flowchart TD

Vue3["Vue 3<br>vue@^3.0.0"]
VueRouter["Vue Router<br>Client-side routing"]
Pinia["Pinia<br>State management"]
TailwindCSS["Tailwind CSS<br>Styling framework"]
ViteBuild["Vite<br>Build tool"]
Django521["Django 5.2.1<br>Web framework"]
DjangoChannels["channels 4.2.0<br>WebSocket support"]
GrapheneDjango["graphene-django 3.2.3<br>GraphQL server"]
DjangoGraphQLJWT["django-graphql-jwt 0.4.0<br>Authentication"]
DjangoREST["djangorestframework 3.16.0<br>REST API"]
Uvicorn["uvicorn 0.34.0<br>ASGI server"]
PostgreSQL["PostgreSQL<br>psycopg2 2.9.10"]
Redis["Redis 6.0.0<br>Cache & channels"]
Pillow["Pillow 11.1.0<br>Image processing"]
DockerCompose["Docker Compose<br>Container orchestration"]
NginxServer["Nginx<br>Reverse proxy"]
PythonDotenv["python-dotenv 1.1.0<br>Environment config"]

    DjangoChannels --> Redis
    Django521 --> PostgreSQL
    Django521 --> Pillow
    DockerCompose --> PostgreSQL
    DockerCompose --> Redis
    PythonDotenv --> Django521
    Vue3 --> VueRouter
    Vue3 --> Pinia
    Vue3 --> TailwindCSS
subgraph Infrastructure ["Infrastructure"]
    Vue3
    ViteBuild
    DockerCompose
    NginxServer
    PythonDotenv
    DockerCompose --> NginxServer
    ViteBuild --> Vue3
end

subgraph Data_Technologies ["Data Technologies"]
    PostgreSQL
    Redis
    Pillow
end

subgraph Backend_Technologies ["Backend Technologies"]
    Django521
    DjangoChannels
    GrapheneDjango
    DjangoGraphQLJWT
    DjangoREST
    Uvicorn
    Django521 --> DjangoChannels
    Django521 --> GrapheneDjango
    Django521 --> DjangoGraphQLJWT
    Django521 --> DjangoREST
    Uvicorn --> Django521
end

subgraph Frontend_Technologies ["Frontend Technologies"]
    VueRouter
    Pinia
    TailwindCSS
end
```

*Sources: [requirements.txt L1-L42](../requirements.txt#L1-L42)

 [README.md L36-L43](../README.md#L36-L43)

 [README.md L27-L34](../README.md#L27-L34)*

## Core Features and Capabilities

EduSphere provides a comprehensive set of features organized around educational collaboration and real-time communication:

| Feature Category | Components | Description |
| --- | --- | --- |
| **User Management** | Multi-role system | Creators, Learners, and Admins with different permissions |
| **Course Management** | CRUD operations | Create, publish, and sell courses with content management |
| **Real-time Communication** | WebSocket chat | Live messaging system using `channels` and `redis` |
| **Payment Processing** | Stripe/PayPal integration | Monetization capabilities for course creators |
| **Search & Discovery** | Advanced filtering | Filter courses by price, rating, and category |
| **Administration** | Django Admin dashboard | Manage users, courses, and transactions |
| **Authentication** | JWT-based security | Secure login with `django-graphql-jwt` |

*Sources: [README.md L17-L24](../README.md#L17-L24)

 [README.md L32-L34](../README.md#L32-L34)

 [README.md L40-L43](../README.md#L40-L43)*

### System Data Flow

```mermaid
sequenceDiagram
  participant Vue.js Client
  participant frontend/src/
  participant Nginx Proxy
  participant docker/nginx/
  participant Django Backend
  participant backend/
  participant GraphQL API
  participant /graphql/
  participant WebSocket API
  participant /ws/
  participant PostgreSQL
  participant coredb
  participant Redis
  participant Channel Layer

  note over Vue.js Client,Channel Layer: Initial Page Load
  Vue.js Client->>Nginx Proxy: "HTTP Request"
  Nginx Proxy->>Django Backend: "Route to backend"
  Django Backend->>GraphQL API: "Query courses/users"
  GraphQL API->>PostgreSQL: "Database query"
  PostgreSQL->>GraphQL API: "Return data"
  GraphQL API->>Vue.js Client: "JSON response"
  note over Vue.js Client,Channel Layer: Real-time Chat
  Vue.js Client->>WebSocket API: "Connect to room"
  WebSocket API->>Redis: "Join channel group"
  Redis->>WebSocket API: "Connection confirmed"
  Vue.js Client->>WebSocket API: "Send message"
  WebSocket API->>PostgreSQL: "Store message"
  WebSocket API->>Redis: "Broadcast to group"
  Redis->>WebSocket API: "Distribute to clients"
  WebSocket API->>Vue.js Client: "Real-time updates"
```

*Sources: [README.md L20](../README.md#L20-L20)

 [README.md L28-L30](../README.md#L28-L30)

 [README.md L33](../README.md#L33-L33)*

## Development Environment Structure

The project follows a monorepo structure with clear separation between frontend, backend, and infrastructure components:

```go
EduSphere/
├── backend/                    # Django application
│   ├── config/                # Django settings and URL routing
│   ├── core/                  # Main application logic and models
│   ├── requirements.txt       # Python dependencies
│   └── manage.py             # Django management commands
├── frontend/                  # Vue.js application  
│   ├── src/                  # Vue components and stores
│   ├── public/               # Static assets
│   ├── package.json          # Node.ts dependencies
│   └── vite.config.ts        # Build configuration
├── docker/                   # Containerization
│   ├── backend/              # Django Docker setup
│   ├── frontend/             # Vue.js Docker setup
│   └── nginx/                # Nginx configuration
├── scripts/                  # Automation scripts
│   ├── run.sh               # Development server startup
│   └── test.sh              # Test execution
├── docker-compose.yml        # Multi-container orchestration
└── .env.docker              # Environment configuration
```

*Sources: [README.md L188-L211](../README.md#L188-L211)*

## Deployment and Infrastructure

EduSphere supports both manual development setup and containerized deployment through Docker Compose. The system uses environment-based configuration to support different deployment scenarios.

### Environment Configuration

| Environment Variable | Purpose | Example |
| --- | --- | --- |
| `SECRET_KEY` | Django security | Generated secret key |
| `DB_NAME` | PostgreSQL database | `coredb` |
| `DB_HOST` | Database hostname | `postgres` (Docker) or `localhost` |
| `REDIS_HOST` | Redis hostname | `redis` (Docker) or `localhost` |
| `DEBUG` | Development mode | `True` or `False` |

### Service Ports

| Service | Development Port | Docker Port | Purpose |
| --- | --- | --- | --- |
| Frontend | 5173 | 80 (via Nginx) | Vue.js development server |
| Backend | 8000 | 8000 | Django application server |
| PostgreSQL | 5432 | 5432 | Database connections |
| Redis | 6379 | 6379 | Cache and WebSocket channels |

*Sources: [README.md L61-L72](../README.md#L61-L72)

 [README.md L127-L140](../README.md#L127-L140)

 [README.md L159-L162](../README.md#L159-L162)*

This architecture provides a scalable foundation for educational platforms requiring real-time collaboration features while maintaining clear separation of concerns between presentation, business logic, and data layers.