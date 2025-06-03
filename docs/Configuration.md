# Configuration

> **Relevant source files**
> * [.gitignore](../.gitignore)
> * [backend/config/asgi.py](../backend/config/asgi.py)
> * [backend/config/settings.py](../backend/config/settings.py)
> * [backend/config/urls.py](../backend/config/urls.py)
> * [backend/core/graphql/utils.py](../backend/core/graphql/utils.py)
> * [docker-compose.yml](../docker-compose.yml)
> * [docker/nginx/nginx.conf](../docker/nginx/nginx.conf)
> * [frontend/vite.config.ts](../frontend/vite.config.ts)
> * [scripts/run.sh](../scripts/run.sh)
> * [scripts/test.sh](../scripts/test.sh)

This document covers the Django backend configuration system, including settings management, ASGI setup, URL routing, and environment variables. It details how the backend is configured for both development and production environments.

For frontend build configuration, see [Application Setup](./Application-Setup.md). For Docker containerization setup, see [Docker Configuration](./Docker-Configuration.md).

## Django Settings Architecture

The EduSphere backend uses Django's settings system with environment-based configuration through the `django-environ` package. The main configuration is centralized in `settings.py` with environment variables controlling deployment-specific values.

```mermaid
flowchart TD

SettingsFile["settings.py<br>Main Configuration"]
EnvFile[".env<br>Environment Variables"]
EnvVars["environ.Env<br>Environment Parser"]
Database["DATABASES<br>PostgreSQL Config"]
Channels["CHANNEL_LAYERS<br>Redis Config"]
GraphQL["GRAPHENE<br>GraphQL Config"]
JWT["GRAPHQL_JWT<br>Authentication Config"]
Security["CORS/CSRF<br>Security Config"]
Logging["LOGGING<br>Debug System"]
Apps["INSTALLED_APPS<br>Django Applications"]
Middleware["MIDDLEWARE<br>Request Processing"]
Templates["TEMPLATES<br>Template Engine"]
StaticFiles["STATIC_ROOT<br>Static Files"]

    SettingsFile --> Database
    SettingsFile --> Channels
    SettingsFile --> GraphQL
    SettingsFile --> JWT
    SettingsFile --> Security
    SettingsFile --> Logging
    SettingsFile --> Apps
    SettingsFile --> Middleware
    SettingsFile --> Templates
    SettingsFile --> StaticFiles
subgraph Application_Components ["Application Components"]
    Apps
    Middleware
    Templates
    StaticFiles
end

subgraph Django_Core_Systems ["Django Core Systems"]
    Database
    Channels
    GraphQL
    JWT
    Security
    Logging
end

subgraph Configuration_Layer ["Configuration Layer"]
    SettingsFile
    EnvFile
    EnvVars
    EnvFile --> EnvVars
    EnvVars --> SettingsFile
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L1-L264) | L1–L264 |

## Core Configuration Components

### Environment Variable Management

The system uses `django-environ` to manage environment-specific settings with secure defaults:

| Variable | Purpose | Default | Required |
| --- | --- | --- | --- |
| `SECRET_KEY` | Django cryptographic signing | None | Yes |
| `DEBUG` | Development mode flag | `False` | No |
| `DB_NAME` | PostgreSQL database name | None | Yes |
| `DB_USER` | Database username | None | Yes |
| `DB_PASSWORD` | Database password | None | Yes |
| `DB_HOST` | Database host | `localhost` | No |
| `DB_PORT` | Database port | `5432` | No |
| `REDIS_HOST` | Redis server host | `localhost` | No |

The environment configuration is initialized in [backend/config/settings.py L16-L31](../backend/config/settings.py#L16-L31)

:

```
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(ENV_PATH)
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
```

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L16-L35) | L16–L35 |
| [`.gitignore`](../.gitignore#L5-L7) | L5–L7 |

### Database Configuration

EduSphere uses PostgreSQL as the primary database with configuration in the `DATABASES` setting:

```mermaid
flowchart TD

DBConfig["DATABASES<br>settings.py:192-201"]
Engine["django.db.backends.postgresql"]
Connection["Connection Parameters"]
DBName["DB_NAME"]
DBUser["DB_USER"]
DBPass["DB_PASSWORD"]
DBHost["DB_HOST"]
DBPort["DB_PORT"]

    DBName --> Connection
    DBUser --> Connection
    DBPass --> Connection
    DBHost --> Connection
    DBPort --> Connection
subgraph Environment_Variables ["Environment Variables"]
    DBName
    DBUser
    DBPass
    DBHost
    DBPort
end

subgraph Database_Configuration ["Database Configuration"]
    DBConfig
    Engine
    Connection
    Connection --> DBConfig
    Engine --> DBConfig
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L192-L201) | L192–L201 |

### Real-time Communication Setup

Django Channels with Redis backend provides WebSocket support:

| Setting | Value | Purpose |
| --- | --- | --- |
| `CHANNEL_LAYERS.default.BACKEND` | `channels_redis.core.RedisChannelLayer` | Redis channel layer |
| `CHANNEL_LAYERS.default.CONFIG.hosts` | `[(REDIS_HOST, 6379)]` | Redis connection |

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L203-L210) | L203–L210 |

## ASGI Configuration

The ASGI application handles both HTTP and WebSocket protocols through Django Channels:

```mermaid
flowchart TD

ProtocolRouter["ProtocolTypeRouter<br>Protocol Dispatcher"]
HTTPApp["get_asgi_application()<br>Django HTTP Handler"]
WSApp["WebSocket Handler"]
OriginValidator["AllowedHostsOriginValidator<br>Security Check"]
JWTMiddleware["JwtAuthMiddleware<br>Authentication"]
URLRouter["URLRouter<br>WebSocket Routing"]
WSPatterns["websocket_urlpatterns<br>Chat Routes"]

    WSApp --> OriginValidator
subgraph WebSocket_Stack ["WebSocket Stack"]
    OriginValidator
    JWTMiddleware
    URLRouter
    WSPatterns
    OriginValidator --> JWTMiddleware
    JWTMiddleware --> URLRouter
    URLRouter --> WSPatterns
end

subgraph ASGI_Application ["ASGI Application"]
    ProtocolRouter
    HTTPApp
    WSApp
    ProtocolRouter --> HTTPApp
    ProtocolRouter --> WSApp
end
```

The ASGI configuration in [backend/config/asgi.py L7-L14](../backend/config/asgi.py#L7-L14)

 creates a `ProtocolTypeRouter` that:

* Routes HTTP requests to Django's standard ASGI application
* Routes WebSocket connections through security validation and JWT authentication
* Applies URL routing to WebSocket connections via `websocket_urlpatterns`

**Sources:**

| File | Lines |
|------|-------|
| [`asgi.py`](../backend/config/asgi.py#L1-L14) | L1–L14 |
| [`settings.py`](../backend/config/settings.py#L141-L141) | L141 |

## URL Routing Configuration

The main URL configuration provides API endpoints with security middleware:

```mermaid
flowchart TD

AdminURL["/admin/<br>Django Admin"]
GraphQLURL["/graphql/<br>GraphQL Endpoint"]
APIURL["/api/<br>REST API"]
JWTCookie["jwt_cookie<br>JWT Token Management"]
CSRFProtect["csrf_protect<br>CSRF Protection"]
EnsureCSRF["ensure_csrf_cookie<br>CSRF Cookie Setup"]
FileUpload["FileUploadGraphQLView<br>GraphQL + File Upload"]

    GraphQLURL --> JWTCookie
subgraph GraphQL_Security_Stack ["GraphQL Security Stack"]
    JWTCookie
    CSRFProtect
    EnsureCSRF
    FileUpload
    JWTCookie --> CSRFProtect
    CSRFProtect --> EnsureCSRF
    EnsureCSRF --> FileUpload
end

subgraph URL_Patterns ["URL Patterns"]
    AdminURL
    GraphQLURL
    APIURL
end
```

The GraphQL endpoint at `/graphql/` is wrapped with multiple security decorators in [backend/config/urls.py L11-L15](../backend/config/urls.py#L11-L15)

:

* `jwt_cookie`: Manages JWT tokens in cookies
* `csrf_protect`: Enforces CSRF protection
* `ensure_csrf_cookie`: Ensures CSRF cookies are set
* `FileUploadGraphQLView`: Handles GraphQL queries with file uploads

**Sources:**

| File | Lines |
|------|-------|
| [`urls.py`](../backend/config/urls.py#L9-L17) | L9–L17 |

## Authentication and Security Configuration

### JWT Authentication Settings

The JWT configuration provides secure token-based authentication:

| Setting | Value | Purpose |
| --- | --- | --- |
| `JWT_VERIFY_EXPIRATION` | `True` | Validate token expiration |
| `JWT_EXPIRATION_DELTA` | `10 minutes` | Access token lifetime |
| `JWT_REFRESH_EXPIRATION_DELTA` | `7 days` | Refresh token lifetime |
| `JWT_BLACKLIST_ENABLED` | `True` | Enable token blacklisting |
| `JWT_CSRF_ROTATION` | `True` | Rotate CSRF tokens |

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L153-L163) | L153–L163 |

### CORS and CSRF Configuration

Cross-origin and CSRF settings for frontend-backend communication:

```mermaid
flowchart TD

CORS["CORS Settings<br>Cross-Origin Requests"]
CSRF["CSRF Settings<br>Cross-Site Request Forgery"]
Sessions["Session Settings<br>User Sessions"]
CORSCredentials["CORS_ALLOW_CREDENTIALS: True"]
CORSOrigins["CORS_ALLOWED_ORIGINS<br>localhost, 127.0.0.1"]
CSRFTrusted["CSRF_TRUSTED_ORIGINS<br>localhost, 127.0.0.1"]
CSRFCookie["CSRF_COOKIE_HTTPONLY: False"]
CSRFSameSite["CSRF_COOKIE_SAMESITE: Lax"]

    CORS --> CORSCredentials
    CORS --> CORSOrigins
    CSRF --> CSRFTrusted
    CSRF --> CSRFCookie
    CSRF --> CSRFSameSite
subgraph CSRF_Configuration ["CSRF Configuration"]
    CSRFTrusted
    CSRFCookie
    CSRFSameSite
end

subgraph CORS_Configuration ["CORS Configuration"]
    CORSCredentials
    CORSOrigins
end

subgraph Security_Configuration ["Security Configuration"]
    CORS
    CSRF
    Sessions
end
```

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L165-L182) | L165–L182 |

## Logging Configuration

The logging system provides structured logging for debugging and monitoring:

```mermaid
flowchart TD

LogConfig["LOGGING<br>Django Logging Dict"]
Formatters["verbose<br>Log Format"]
Handlers["File Handlers"]
Loggers["Logger Definitions"]
GraphQLLog["logs/graphql.log<br>GraphQL Operations"]
GeneralLog["logs/general.log<br>General Application"]
GraphQLLogger["backend.core.graphql.middleware<br>DEBUG Level"]
RootLogger["Root Logger<br>WARNING Level"]

    Handlers --> GraphQLLog
    Handlers --> GeneralLog
    GraphQLLogger --> GraphQLLog
    RootLogger --> GeneralLog
subgraph Logger_Sources ["Logger Sources"]
    GraphQLLogger
    RootLogger
end

subgraph Log_Files ["Log Files"]
    GraphQLLog
    GeneralLog
end

subgraph Logging_Configuration ["Logging Configuration"]
    LogConfig
    Formatters
    Handlers
    Loggers
    LogConfig --> Formatters
    LogConfig --> Handlers
    LogConfig --> Loggers
end
```

The logging configuration in [backend/config/settings.py L107-L139](../backend/config/settings.py#L107-L139)

 creates:

* Structured log formatting with timestamp and module information
* Separate log files for GraphQL operations and general application logs
* Debug-level logging for GraphQL middleware
* Warning-level logging for general application events

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L107-L139) | L107–L139 |

## Development vs Production Settings

### Development Configuration

Development settings prioritize debugging and rapid iteration:

* `DEBUG = True` enables detailed error pages
* `GRAPHQL_JWT.JWT_COOKIE_SECURE = False` allows HTTP cookies
* CORS and CSRF settings allow `localhost` origins
* GraphiQL interface enabled for GraphQL debugging

### Production Considerations

Several settings are marked for production adjustment:

```css
# TODO: When moving to production with HTTPS
SECURE_SETTINGS = {
    "SECURE_SSL_REDIRECT": True,
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    # ...
}
```

Production changes needed:

* Enable HTTPS redirects and HSTS headers
* Set `JWT_COOKIE_SECURE = True` for HTTPS-only cookies
* Change `CSRF_COOKIE_SAMESITE` and `SESSION_COOKIE_SAMESITE` to `"Strict"`
* Disable GraphiQL interface
* Configure proper `ALLOWED_HOSTS` for production domains

**Sources:**

| File | Lines |
|------|-------|
| [`settings.py`](../backend/config/settings.py#L76-L86) | L76–L86 |
| [`settings.py`](../backend/config/settings.py#L157-L169) | L157–L169 |
