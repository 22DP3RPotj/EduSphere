# Backend (Django)

The backend is built using **Django** and **Django Channels** to support real-time features like chat and notifications.

## Features
- User authentication (JWT-based with OAuth2 support)
- Course management (CRUD operations for courses)
- WebSockets for real-time messaging
- PostgreSQL database with Redis for real-time operations

## Architecture Overview
- **Framework**: Django + Django Channels
- **Database**: PostgreSQL (primary), Redis (real-time)
- **APIs**: GraphQL endpoints
- **Authentication**: JWT with OAuth2 social login
- **WebSocket Support**: Integrated for real-time messaging

## Running the Backend
Refer to the main [README](../README.md) for installation and setup instructions.

To start the backend server after setup:
```bash
python manage.py runserver
```

## API Endpoints
The backend exposes REST and GraphQL APIs.

## Installation
For installation instructions, refer to the main [README](../README.md#installation-guide).
