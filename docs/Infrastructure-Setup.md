# Infrastructure Setup

> **Relevant source files**
> * [README.md](../README.md)
> * [backend/README.md](../backend/README.md)
> * [backend/config/settings.py](../backend/config/settings.py)
> * [backend/config/urls.py](../backend/config/urls.py)
> * [docker-compose.yml](../docker-compose.yml)
> * [docker/nginx/nginx.conf](../docker/nginx/nginx.conf)
> * [frontend/README.md](../frontend/README.md)
> * [frontend/vite.config.ts](../frontend/vite.config.ts)
> * [requirements.txt](../requirements.txt)

This document covers the infrastructure configuration and setup for the EduSphere platform, including database setup, caching layer, reverse proxy configuration, and service networking. This page focuses on the underlying infrastructure components and their configuration. For container orchestration and Docker-specific setup, see [Docker Configuration](./Docker-Configuration.md).

## Service Architecture Overview

The EduSphere platform uses a multi-service architecture with distinct infrastructure components handling different aspects of the system.

### Infrastructure Service Topology

```mermaid
flowchart TD

Client["Client Browser"]
AdminUser["Admin User"]
Nginx["nginx:80<br>Reverse Proxy"]
Frontend["frontend:5173<br>Vue.js Development Server"]
Backend["backend:8000<br>Django ASGI Server"]
PostgreSQL["postgres:5432<br>PostgreSQL 15<br>Database: coredb"]
Redis["redis:6379<br>Redis Alpine<br>Channel Layer"]
StaticVolume["static_volume<br>Django Static Files"]
MediaFiles["./media<br>User Uploads"]
PostgresData["postgres_data<br>Database Storage"]

    Client --> Nginx
    AdminUser --> Nginx
    Nginx -->|proxy_pass frontend:5173| Frontend
    Nginx --> Backend
    Nginx --> StaticVolume
    Nginx --> MediaFiles
    Backend -->|"DB_HOST=postgres"| PostgreSQL
    Backend --> Redis
    Backend --> StaticVolume
    Backend --> MediaFiles
    PostgreSQL --> PostgresData
subgraph Storage ["Storage"]
    StaticVolume
    MediaFiles
    PostgresData
end

subgraph Data_Infrastructure ["Data Infrastructure"]
    PostgreSQL
    Redis
end

subgraph Application_Layer ["Application Layer"]
    Frontend
    Backend
end

subgraph Reverse_Proxy_Layer ["Reverse Proxy Layer"]
    Nginx
end

subgraph External_Access ["External Access"]
    Client
    AdminUser
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L1-L77) | L1–L77 |
| [`nginx.conf`](../docker/nginx/nginx.conf#L1-L75) | L1–L75 |

### Port Configuration and Service Communication

| Service | Internal Port | External Port | Protocol | Purpose |
| --- | --- | --- | --- | --- |
| `nginx` | 80 | 80 | HTTP | Reverse proxy and static file serving |
| `backend` | 8000 | 8000 | HTTP/WebSocket | Django ASGI application |
| `frontend` | 5173 | 5173 | HTTP | Vue.js development server |
| `postgres` | 5432 | 5432 | TCP | PostgreSQL database |
| `redis` | 6379 | 6379 | TCP | Redis cache and channel layer |

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L11-L72) | L11–L72 |

## Database Infrastructure

### PostgreSQL Configuration

The system uses PostgreSQL 15 as the primary database with the following configuration:

```mermaid
flowchart TD

PostgresContainer["postgres:15<br>Container"]
PostgresDB["Database: coredb<br>User: rpote"]
PostgresVolume["postgres_data<br>Persistent Storage"]
DjangoSettings["DATABASES<br>settings.py"]
DjangoModels["Django Models<br>User, Room, Topic, Message"]

    DjangoSettings --> PostgresDB
subgraph Django_Backend ["Django Backend"]
    DjangoSettings
    DjangoModels
    DjangoModels --> DjangoSettings
end

subgraph PostgreSQL_Service ["PostgreSQL Service"]
    PostgresContainer
    PostgresDB
    PostgresVolume
    PostgresContainer --> PostgresDB
    PostgresDB --> PostgresVolume
end
```

**Database Connection Settings:**

* **Engine**: `django.db.backends.postgresql`
* **Host**: `postgres` (service name in Docker network)
* **Port**: `5432`
* **Database Name**: Configured via `DB_NAME` environment variable
* **Authentication**: Username and password via `DB_USER` and `DB_PASSWORD`

**Health Check Configuration:**
The PostgreSQL service includes a health check to ensure database availability before dependent services start:

* **Test Command**: `pg_isready -U rpote -d coredb`
* **Interval**: 5 seconds
* **Timeout**: 5 seconds
* **Retries**: 5 attempts

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L3-L17) | L3–L17 |
| [`settings.py`](../backend/config/settings.py#L192-L201) | L192–L201 |

## Cache and Real-time Infrastructure

### Redis Configuration

Redis serves dual purposes in the infrastructure: caching and real-time communication via Django Channels.

```mermaid
flowchart TD

RedisContainer["redis:alpine<br>Container"]
RedisMemory["In-Memory Storage<br>Channel Layers & Cache"]
ChannelLayers["CHANNEL_LAYERS<br>channels_redis.core.RedisChannelLayer"]
WebSocketConsumers["Chat Consumers<br>Real-time Messaging"]
CacheFramework["Django Cache<br>(Future Use)"]

    ChannelLayers --> RedisMemory
    CacheFramework --> RedisMemory
subgraph Django_Backend_Usage ["Django Backend Usage"]
    ChannelLayers
    WebSocketConsumers
    CacheFramework
    WebSocketConsumers --> ChannelLayers
end

subgraph Redis_Service ["Redis Service"]
    RedisContainer
    RedisMemory
    RedisContainer --> RedisMemory
end
```

**Channel Layer Configuration:**

* **Backend**: `channels_redis.core.RedisChannelLayer`
* **Host**: `redis` (service name)
* **Port**: `6379`
* **Usage**: WebSocket group management and message distribution

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L19-L24) | L19–L24 |
| [`settings.py`](../backend/config/settings.py#L203-L210) | L203–L210 |

## Reverse Proxy Configuration

### Nginx Service Configuration

Nginx acts as the entry point for all client requests, routing traffic to appropriate backend services and serving static content.

```mermaid
flowchart TD

NginxServer["nginx:80<br>Main Server Block"]
StaticRule["location /static/<br>alias /app/staticfiles/"]
MediaRule["location /media/<br>alias /app/media/"]
AdminRule["location /admin/<br>proxy_pass backend:8000"]
GraphQLRule["location /graphql/<br>proxy_pass backend:8000"]
WebSocketRule["location /ws/<br>WebSocket Upgrade<br>proxy_pass backend:8000"]
FrontendRule["location /<br>proxy_pass frontend:5173"]
DjangoBackend["backend:8000<br>Django ASGI"]
VueFrontend["frontend:5173<br>Vue Dev Server"]
StaticFiles["static_volume<br>Django Static Files"]
MediaFiles["./media<br>User Uploads"]

    StaticRule --> StaticFiles
    MediaRule --> MediaFiles
    AdminRule --> DjangoBackend
    GraphQLRule --> DjangoBackend
    WebSocketRule --> DjangoBackend
    FrontendRule --> VueFrontend
subgraph Static_Assets ["Static Assets"]
    StaticFiles
    MediaFiles
end

subgraph Backend_Services ["Backend Services"]
    DjangoBackend
    VueFrontend
end

subgraph Nginx_Routing_Rules ["Nginx Routing Rules"]
    NginxServer
    StaticRule
    MediaRule
    AdminRule
    GraphQLRule
    WebSocketRule
    FrontendRule
    NginxServer --> StaticRule
    NginxServer --> MediaRule
    NginxServer --> AdminRule
    NginxServer --> GraphQLRule
    NginxServer --> WebSocketRule
    NginxServer --> FrontendRule
end
```

**Key Nginx Directives:**

| Location | Purpose | Configuration |
| --- | --- | --- |
| `/static/` | Django static files | `alias /app/staticfiles/; expires 7d;` |
| `/media/` | User uploaded files | `alias /app/media/; expires 7d;` |
| `/admin/` | Django admin interface | `proxy_pass http://backend:8000` |
| `/graphql/` | GraphQL API endpoint | `proxy_pass http://backend:8000` |
| `/ws/` | WebSocket connections | WebSocket upgrade headers |
| `/` | Vue.js frontend | `proxy_pass http://frontend:5173` |

**WebSocket Support:**

```
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "Upgrade";
```

**Sources:**

| File | Lines |
|------|-------|
| [`nginx.conf`](../docker/nginx/nginx.conf#L1-L75) | L1–L75 |

## Network Configuration

### Service Networking and Dependencies

```mermaid
flowchart TD

PostgresHealthy["postgres<br>condition: service_healthy"]
RedisStarted["redis<br>condition: service_started"]
BackendReady["backend<br>depends_on: postgres, redis"]
FrontendReady["frontend<br>depends_on: backend"]
NginxReady["nginx<br>depends_on: backend, frontend"]
DockerNetwork["Default Docker Network<br>Service Discovery"]
DNSResolution["Internal DNS<br>Service Names"]

    DNSResolution --> BackendReady
subgraph Network_Communication ["Network Communication"]
    DockerNetwork
    DNSResolution
    DockerNetwork --> DNSResolution
end

subgraph Service_Dependency_Chain ["Service Dependency Chain"]
    PostgresHealthy
    RedisStarted
    BackendReady
    FrontendReady
    NginxReady
    PostgresHealthy --> BackendReady
    RedisStarted --> BackendReady
    BackendReady --> FrontendReady
    BackendReady --> NginxReady
    FrontendReady --> NginxReady
end
```

**Service Dependencies:**

* **backend**: Waits for `postgres` (healthy) and `redis` (started)
* **frontend**: Waits for `backend` to be available
* **nginx**: Waits for both `backend` and `frontend`

**Internal Service Discovery:**
Services communicate using Docker's built-in DNS resolution:

* `postgres` → PostgreSQL database
* `redis` → Redis server
* `backend` → Django application
* `frontend` → Vue.js development server

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L36-L72) | L36–L72 |

## Environment Configuration

### Environment Variables and Settings

The infrastructure relies on environment variables for configuration across services:

```mermaid
flowchart TD

EnvFile[".env.docker<br>Configuration File"]
DockerCompose["docker-compose.yml<br>Environment Variables"]
DatabaseConfig["DATABASES<br>DB_HOST, DB_PORT<br>DB_NAME, DB_USER, DB_PASSWORD"]
RedisConfig["CHANNEL_LAYERS<br>REDIS_HOST, REDIS_PORT"]
SecurityConfig["SECRET_KEY<br>DEBUG, ALLOWED_HOSTS"]
PostgresEnv["POSTGRES_DB<br>POSTGRES_USER<br>POSTGRES_PASSWORD"]
BackendEnv["DJANGO_SETTINGS_MODULE<br>DB_HOST, REDIS_HOST"]

    EnvFile --> DatabaseConfig
    EnvFile --> RedisConfig
    EnvFile --> SecurityConfig
    DockerCompose --> PostgresEnv
    DockerCompose --> BackendEnv
subgraph Service_Configuration ["Service Configuration"]
    PostgresEnv
    BackendEnv
end

subgraph Django_Settings ["Django Settings"]
    DatabaseConfig
    RedisConfig
    SecurityConfig
end

subgraph Environment_Sources ["Environment Sources"]
    EnvFile
    DockerCompose
end
```

**Critical Environment Variables:**

| Variable | Service | Purpose | Example Value |
| --- | --- | --- | --- |
| `DB_HOST` | backend | Database connection | `postgres` |
| `DB_PORT` | backend | Database port | `5432` |
| `REDIS_HOST` | backend | Redis connection | `redis` |
| `REDIS_PORT` | backend | Redis port | `6379` |
| `DJANGO_SETTINGS_MODULE` | backend | Django configuration | `backend.config.settings` |
| `POSTGRES_DB` | postgres | Database name | `coredb` |
| `POSTGRES_USER` | postgres | Database user | `rpote` |

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L41-L46) | L41–L46 |
| [`settings.py`](../backend/config/settings.py#L25-L31) | L25–L31 |
| [`settings.py`](../backend/config/settings.py#L192-L210) | L192–L210 |

### Volume Management

Persistent data storage is handled through Docker volumes:

| Volume | Purpose | Mount Point | Persistence |
| --- | --- | --- | --- |
| `postgres_data` | Database files | `/var/lib/postgresql/data/` | Persistent |
| `static_volume` | Django static files | `/app/staticfiles` | Shared |
| `./media` | User uploads | `/app/media` | Host-mounted |

**Sources:**

| File | Lines |
|------|-------|
| [`docker-compose.yml`](../docker-compose.yml#L74-L76) | L74–L76 |
| [`docker-compose.yml`](../docker-compose.yml#L31-L33) | L31–L33 |
| [`docker-compose.yml`](../docker-compose.yml#L65-L67) | L65–L67 |
