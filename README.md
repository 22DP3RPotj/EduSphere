# Real-time Chat Platform

[LICENSE](LICENSE)

A full-stack real-time messaging platform built with Django (backend) and Vue.js (frontend). Create chat rooms, join conversations, and communicate in real-time with WebSocket technology.

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation Guide](#installation-guide)
- [PostgreSQL Backup & Restore](#postgresql-backup--restore)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

> **Note**: This application is designed to run via Docker. Manual local setup is not covered here.

## Features
- **Real-Time Chat**: WebSocket-based messaging system with instant message delivery
- **Chat Rooms**: Create and join topic-based chat rooms
- **Message Management**: Edit and delete your own messages
- **User Authentication**: Secure JWT-based authentication
- **Room Participation**: Host rooms or join as a participant
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Architecture Overview

### Backend (Django)
- **Framework**: Django + Django Channels
- **Database**: PostgreSQL (primary), Redis (real-time)
- **APIs**: GraphQL endpoints
- **Authentication**: JWT
- **Key Features**:
  - WebSocket implementation for real-time chat
  - Message CRUD operations with ownership validation
  - Room-based chat organization
  - User authentication and authorization

### Frontend (Vue.js)
- **Framework**: Vue 3 + Vue Router
- **State Management**: Pinia
- **Styling**: CSS
- **Key Features**:
  - Real-time chat interface
  - Responsive room management
  - Message editing and deletion
  - User authentication flows
  - WebSocket connection management

## Installation Guide

### Prerequisites
- Docker and Docker Compose

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/22DP3RPotj/EduSphere.git
   cd EduSphere
   ```

2. Configure environment variables by copying the example file:
   ```bash
   cp .env.example docker.env
   ```
   Edit `docker.env` and fill in your values.

3. Build and start the containers:
   ```bash
   make docker-compose-build
   ```

4. Access the application (migrations run automatically on container startup):
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - GraphQL: http://localhost/graphql

### Manual Migration and Setup

If you need to manually run migrations or create a superuser:

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create a superuser
docker compose exec backend python manage.py createsuperuser

# Collect static files (if needed)
docker compose exec backend python manage.py collectstatic --noinput
```

### Stopping and Cleaning Up

To stop the containers:
```bash
make docker-compose-remove
```

## PostgreSQL Backup & Restore

### Backup PostgreSQL Database

```bash
docker compose exec postgres pg_dump -U <POSTGRES_USER> -d <POSTGRES_DB> > backup.sql
```

### Restore PostgreSQL Backup

```bash
docker compose exec -T postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB> < backup.sql
```

## Testing

### Running the tests

```bash
make test
```

For targeted runs:
```bash
# Unit tests only
make unit-test

# With coverage report
make report
```

## Project Structure
```
.
├── backend/
│   ├── config/          # Django settings and routing
│   ├── core/            # Shared models, middleware, tasks
│   ├── account/         # User accounts and authentication
│   ├── room/            # Chat room logic
│   ├── messaging/       # Messages and chat consumers
│   ├── access/          # Permissions and access control
│   ├── invite/          # Room invitations
│   ├── moderation/      # Moderation tools
│   ├── graphql/         # GraphQL schema and resolvers
│   └── infra/           # Infrastructure views and middleware
├── frontend/
│   ├── public/
│   ├── src/             # Vue components and stores
│   └── README.md        # Frontend development guide
├── docker/
│   ├── backend/         # Backend Dockerfile and entrypoint
│   └── nginx/           # Nginx Dockerfile, config, and entrypoint
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Environment variable template
├── Makefile             # Development and Docker commands
├── README.md            # Main documentation (you are here)
└── LICENSE
```

## Contributing
1. Fork the repository
2. Create feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Submit a pull request

## License
Distributed under the MIT License. See [LICENSE](https://opensource.org/licenses/MIT) for more information.
