# Backend (Django)

The backend is built using **Django** and **Django Channels** to support real-time features like chat and notifications.

## Features
- Real-time chat via WebSockets
- User authentication (JWT-based)
- Chat rooms with topics
- Message management (create, edit, delete)
- GraphQL API for data queries and mutations
- PostgreSQL database with Redis for real-time operations

## Architecture Overview
- **Framework**: Django + Django Channels
- **Database**: PostgreSQL (primary), Redis (real-time)
- **APIs**: GraphQL endpoints
- **Authentication**: JWT
- **WebSocket Support**: Integrated for real-time messaging via Channels

## Running the Backend

### Docker Setup
Refer to the main [README](../README.md#docker-setup) for Docker installation and setup instructions.

The backend automatically runs migrations on container startup.

### Manual Migration

To manually run migrations:
```bash
docker-compose exec backend python manage.py migrate
```

To create new migrations after model changes:
```bash
docker-compose exec backend python manage.py makemigrations
```

### Local Development

To start the backend server locally after setup:
```bash
python manage.py runserver
```

## API Endpoints
The backend exposes GraphQL APIs at `/graphql/`

## Installation
For installation and setup instructions, refer to the main [README](../README.md#installation-guide).
