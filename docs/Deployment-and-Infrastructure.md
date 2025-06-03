# Deployment and Infrastructure

> **Relevant source files**
> * [.dockerignore](../.dockerignore)
> * [README.md](../README.md)
> * [backend/README.md](../backend/README.md)
> * [docker/backend/Dockerfile](../docker/backend/Dockerfile)
> * [docker/frontend/Dockerfile](../docker/frontend/Dockerfile)
> * [docker/nginx/Dockerfile](../docker/nginx/Dockerfile)
> * [frontend/README.md](../frontend/README.md)
> * [requirements.txt](../requirements.txt)

This document covers the containerized deployment architecture and infrastructure configuration for the EduSphere platform. It details Docker container orchestration, service configuration, and production deployment setup. For specific Docker container implementation details, see [Docker Configuration](./Docker-Configuration.md). For individual service configurations including Nginx, PostgreSQL, and Redis setup, see [Infrastructure Setup](./Infrastructure-Setup.md).

## Deployment Architecture Overview

EduSphere uses a containerized microservices architecture orchestrated with Docker Compose, providing isolated, scalable service deployment.

### Service Container Architecture

```mermaid
flowchart TD

nginx["nginx<br>Port: 80<br>Image: nginx:alpine"]
frontend["frontend<br>Port: 5173<br>Node.ts Application"]
backend["backend<br>Port: 8000<br>Django ASGI"]
postgres["postgres<br>Port: 5432<br>PostgreSQL Database"]
redis["redis<br>Port: 6379<br>Redis Cache"]
browser["Web Browser"]
admin["Admin Interface"]
pgdata["postgres_data<br>Volume"]
staticfiles["staticfiles<br>Volume"]
mediafiles["media<br>Volume"]

    browser --> nginx
    admin --> nginx
    nginx --> staticfiles
    postgres --> pgdata
    backend --> staticfiles
    backend --> mediafiles
subgraph Persistent_Storage ["Persistent Storage"]
    pgdata
    staticfiles
    mediafiles
end

subgraph External_Access ["External Access"]
    browser
    admin
end

subgraph Docker_Compose_Network ["Docker Compose Network"]
    nginx
    frontend
    backend
    postgres
    redis
    nginx --> frontend
    nginx --> backend
    frontend --> backend
    backend --> postgres
    backend --> redis
end
```

**Container Network Communication**

* All services communicate through Docker's internal network using service names as hostnames
* External access is routed through `nginx` reverse proxy on port 80
* Database and cache services are isolated from direct external access

Sources: [README.md L114-L163](../README.md#L114-L163)

 [docker-compose.yml](../docker-compose.yml)

### Docker Compose Service Definitions

```mermaid
flowchart TD

postgresImage["postgres:16"]
redisImage["redis:6.0-alpine"]
nginxDockerfile["docker/nginx/Dockerfile"]
nginxConf["nginx.conf"]
nginxPort["80:80"]
backendDockerfile["docker/backend/Dockerfile"]
backendCmd["uvicorn config.asgi:application"]
backendPort["8000:8000"]
backendEnv[".env.docker"]
frontendDockerfile["docker/frontend/Dockerfile"]
frontendCmd["npm run dev --host 0.0.0.0"]
frontendPort["5173:5173"]

    nginxDockerfile --> nginxConf
    backendDockerfile --> backendCmd
    backendEnv --> backendCmd
    frontendDockerfile --> frontendCmd
subgraph Database_Services ["Database Services"]
    postgresImage
    redisImage
    nginxDockerfile
    backendDockerfile
    backendEnv
    frontendDockerfile
end

subgraph Nginx_Service ["Nginx Service"]
    nginxConf
    nginxPort
    backendCmd
    backendPort
    frontendCmd
    frontendPort
    nginxConf --> nginxPort
    backendCmd --> backendPort
    frontendCmd --> frontendPort
end

subgraph Backend_Service ["Backend Service"]
end

subgraph Frontend_Service ["Frontend Service"]
end
```

**Service Dependencies**

* `backend` depends on `postgres` and `redis` services being healthy
* `frontend` can start independently but requires `backend` for API communication
* `nginx` serves as the entry point and depends on both `frontend` and `backend`

Sources: [docker/frontend/Dockerfile L12-L14](../docker/frontend/Dockerfile#L12-L14)

 [docker/backend/Dockerfile L25-L26](../docker/backend/Dockerfile#L25-L26)

 [docker/nginx/Dockerfile L3](../docker/nginx/Dockerfile#L3-L3)

## Environment Configuration

### Docker Environment Setup

The platform uses environment-specific configuration through `.env.docker` file for containerized deployment:

| Variable | Purpose | Default Value |
| --- | --- | --- |
| `SECRET_KEY` | Django cryptographic signing | (required) |
| `DEBUG` | Django debug mode | `True` |
| `DB_HOST` | PostgreSQL container hostname | `postgres` |
| `DB_NAME` | Database name | `coredb` |
| `DB_USER` | Database username | `db_user` |
| `DB_PASSWORD` | Database password | (required) |
| `REDIS_HOST` | Redis container hostname | `redis` |
| `REDIS_PORT` | Redis port | `6379` |

**Container Network Hostnames**

* Database hostname uses Docker service name: `DB_HOST=postgres`
* Redis hostname uses Docker service name: `REDIS_HOST=redis`
* This enables automatic service discovery within the Docker network

Sources: [README.md L127-L140](../README.md#L127-L140)

### Production vs Development Configuration

```mermaid
flowchart TD

prodEnv[".env.docker<br>DEBUG=False"]
prodFrontend["Built Static Files<br>nginx Served"]
prodBackend["ASGI Production<br>uvicorn"]
prodStatic["collectstatic<br>Static Files"]
devEnv[".env.docker<br>DEBUG=True"]
devFrontend["Vite Dev Server<br>Hot Reload"]
devBackend["Django Debug<br>Auto-reload"]

    prodEnv --> prodStatic
subgraph Production_Environment ["Production Environment"]
    prodStatic
end

subgraph Development_Environment ["Development Environment"]
    prodEnv
    prodFrontend
    prodBackend
    devEnv
    devFrontend
    devBackend
    prodEnv --> prodFrontend
    prodEnv --> prodBackend
    devEnv --> devFrontend
    devEnv --> devBackend
end
```

**Development Configuration**

* Frontend runs Vite development server with hot module replacement
* Backend uses Django's development server with auto-reload
* Debug mode enabled for detailed error reporting

**Production Considerations**

* Static files served directly by Nginx for performance
* `collectstatic` command gathers Django static files
* Debug mode disabled for security

Sources: [README.md L155-L156](../README.md#L155-L156)

 [docker/frontend/Dockerfile L13-L14](../docker/frontend/Dockerfile#L13-L14)

## Database and Cache Infrastructure

### PostgreSQL Database Configuration

```mermaid
flowchart TD

postgresContainer["postgres:16<br>Service Name: postgres"]
postgresPort["Port: 5432"]
postgresData["Volume: postgres_data"]
postgresEnv["Environment:<br>POSTGRES_DB=coredb<br>POSTGRES_USER=db_user"]
djangoSettings["Django Settings<br>DATABASES configuration"]
psycopg2["psycopg2==2.9.10<br>PostgreSQL adapter"]
migrations["Django Migrations<br>python manage.py migrate"]

    psycopg2 --> postgresContainer
    migrations --> postgresContainer
subgraph Backend_Integration ["Backend Integration"]
    djangoSettings
    psycopg2
    migrations
    djangoSettings --> psycopg2
end

subgraph PostgreSQL_Container ["PostgreSQL Container"]
    postgresContainer
    postgresPort
    postgresData
    postgresEnv
    postgresContainer --> postgresPort
    postgresContainer --> postgresData
    postgresContainer --> postgresEnv
end
```

**Database Setup Commands**

```sql
# Run migrations inside container
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

Sources: [README.md L148-L156](../README.md#L148-L156)

 [requirements.txt L26](../requirements.txt#L26-L26)

### Redis Cache and Channel Layer

```mermaid
flowchart TD

redisContainer["redis:6.0-alpine<br>Service Name: redis"]
redisPort["Port: 6379"]
redisConfig["No persistence<br>In-memory cache"]
channelsRedis["channels_redis==4.2.1<br>WebSocket backend"]
redisClient["redis==6.0.0<br>Python client"]
channelLayers["Channel Layers<br>Real-time messaging"]

    channelsRedis --> redisContainer
    redisClient --> redisContainer
subgraph Django_Integration ["Django Integration"]
    channelsRedis
    redisClient
    channelLayers
    channelLayers --> channelsRedis
end

subgraph Redis_Container ["Redis Container"]
    redisContainer
    redisPort
    redisConfig
    redisContainer --> redisPort
    redisContainer --> redisConfig
end
```

**Redis Usage Patterns**

* **Channel Layers**: WebSocket message broadcasting for real-time chat
* **Session Storage**: User session data caching
* **Temporary Data**: Short-lived application state

Sources: [requirements.txt L4](../requirements.txt#L4-L4)

 [requirements.txt L33](../requirements.txt#L33-L33)

 [README.md L138-L139](../README.md#L138-L139)

## Container Build and Runtime Configuration

### Backend Container Build Process

The Django backend container uses a Python slim base image with optimized dependency installation:

```mermaid
flowchart TD

baseImage["python:slim<br>Base Image"]
systemDeps["System Dependencies<br>gcc, python3-dev, libpq-dev"]
pythonDeps["Python Dependencies<br>requirements.txt"]
appCopy["Application Code<br>Copy project files"]
workdir["/app<br>Working Directory"]
entrypoint["uvicorn backend.config.asgi:application"]
expose["--host 0.0.0.0 --port 8000"]
staticDir["staticfiles/<br>media/"]

    appCopy --> staticDir
subgraph Runtime_Configuration ["Runtime Configuration"]
    workdir
    entrypoint
    expose
    staticDir
    workdir --> entrypoint
    entrypoint --> expose
end

subgraph Build_Process ["Build Process"]
    baseImage
    systemDeps
    pythonDeps
    appCopy
    baseImage --> systemDeps
    systemDeps --> pythonDeps
    pythonDeps --> appCopy
end
```

**Container Optimization**

* Multi-stage build process minimizes final image size
* System dependencies cleaned after installation
* Static file directories pre-created for volume mounting

Sources: [docker/backend/Dockerfile L1-L27](../docker/backend/Dockerfile#L1-L27)

### Frontend Container Development Setup

The Vue.js frontend container provides development server with hot reload capabilities:

```mermaid
flowchart TD

nodeBase["node:slim<br>Base Image"]
npmInstall["npm install<br>Package Dependencies"]
viteServer["Vite Dev Server<br>Hot Module Replacement"]
hotReload["Hot Reload<br>File Watching"]
hostBinding["--host 0.0.0.0<br>Container Access"]
sourceMap["Source Maps<br>Debugging"]

    viteServer --> hotReload
    viteServer --> hostBinding
    viteServer --> sourceMap
subgraph Development_Features ["Development Features"]
    hotReload
    hostBinding
    sourceMap
end

subgraph Frontend_Container ["Frontend Container"]
    nodeBase
    npmInstall
    viteServer
    nodeBase --> npmInstall
    npmInstall --> viteServer
end
```

**Development Workflow**

* Source code changes trigger automatic rebuilds
* Browser automatically refreshes on file modifications
* Container exposes development server on all interfaces

Sources: [docker/frontend/Dockerfile L1-L14](../docker/frontend/Dockerfile#L1-L14)

### Nginx Reverse Proxy Configuration

```mermaid
flowchart TD

nginxBase["nginx:alpine<br>Base Image"]
nginxConf["nginx.conf<br>Configuration File"]
staticMount["/app/staticfiles<br>Static File Directory"]
frontendProxy["/ → frontend:5173<br>Vue.js Application"]
backendProxy["/api/ → backend:8000<br>Django API"]
staticFiles["/static/ → /app/staticfiles<br>Static Assets"]
adminProxy["/admin/ → backend:8000<br>Django Admin"]

    nginxConf --> frontendProxy
    nginxConf --> backendProxy
    nginxConf --> staticFiles
    nginxConf --> adminProxy
subgraph Routing_Configuration ["Routing Configuration"]
    frontendProxy
    backendProxy
    staticFiles
    adminProxy
end

subgraph Nginx_Container ["Nginx Container"]
    nginxBase
    nginxConf
    staticMount
    nginxBase --> nginxConf
    nginxBase --> staticMount
end
```

**Reverse Proxy Benefits**

* Single entry point for all client requests
* SSL termination point for HTTPS
* Static file serving without backend overhead
* Load balancing capability for horizontal scaling

Sources: [docker/nginx/Dockerfile L1-L11](../docker/nginx/Dockerfile#L1-L11)

 [README.md L159-L162](../README.md#L159-L162)