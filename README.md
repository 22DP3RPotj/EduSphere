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

### Manual Setup

#### Prerequisites
  - Python 3.9+
  - Node.js 16+
  - PostgreSQL 14+
  - Redis 6+

#### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/22DP3RPotj/EduSphere.git
   cd EduSphere
   ```
2. Configure environment variables (create `.env` file):
   ```env
   SECRET_KEY=secret_key
   DB_NAME=coredb
   DB_USER=db_user
   DB_PASSWORD=db_password
   DB_HOST=localhost
   DB_PORT=5432

   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

#### Backend Setup
1. Navigate to backend directory:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt # Windows: add '--no-binary uvloop'
   ```
4. Create database
   ```bash
   psql -U <db_user> -d postgres -c "CREATE DATABASE coredb;"
   ```
5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

#### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

#### Running the Application
```bash
./scripts/run.sh
```
Access the application at [http://localhost](http://localhost)

### Docker Setup

#### Prerequisites
- Docker and Docker Compose

#### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/22DP3RPotj/EduSphere.git
   cd EduSphere
   ```

2. Create `.env.docker` file in the project root (or use the provided template):
   ```env
   SECRET_KEY=secret_key
   DEBUG=True

   DB_NAME=coredb
   DB_USER=db_user
   DB_PASSWORD=db_password
   DB_HOST=postgres
   DB_PORT=5432

   REDIS_HOST=redis
   REDIS_PORT=6379
   ```

3. Build and start the Docker containers:
   ```bash
   docker compose up -d --build
   ```

4. Run initial setup commands:
   ```bash
   # Run migrations
   docker compose exec backend python manage.py migrate

   # Create a superuser
   docker compose exec backend python manage.py createsuperuser

   # Collect static files
   docker compose exec backend python manage.py collectstatic --noinput
   ```

5. Access the application:
   - Frontend: http://localhost
   - Django Admin: http://localhost/admin
   - GraphiQL: http://localhost/graphql

## PostgreSQL Backup & Restore

### Backup PostgreSQL Database

```bash
pg_dump -U <db_user> -d coredb > backup.sql
```

### Restore PostgreSQL Backup

```bash
psql -U <db_user> -d coredb < backup.sql
```

## Testing

### Running the tests

```bash
python manage.py test backend/core
```

## Project Structure
```
.
├── backend/
│   ├── config/          # Django settings and routing
│   ├── core/            # Main application logic
│   │   ├── chat/        # WebSocket consumers for real-time chat
│   │   ├── graphql/     # GraphQL schema and resolvers
│   │   └── models.py    # Room and Message models
│   ├── requirements.txt
│   └── README.md        # Technical backend documentation
├── frontend/
│   ├── public/
│   ├── src/             # Vue components and stores
│   │   ├── api/         # WebSocket and API integration
│   │   ├── components/  # Chat and UI components
│   │   ├── views/       # Room and authentication views
│   │   └── stores/      # Pinia state management
│   ├── package.json
│   └── README.md        # Frontend development guide
├── docker/              # Docker configuration files
│   ├── backend/         # Backend Docker setup
│   ├── frontend/        # Frontend Docker setup
│   └── nginx/           # Nginx configuration
├── scripts/
│   ├── run.sh           # Combined server startup
│   └── test.sh          # Test runner
├── docker-compose.yml   # Docker Compose configuration
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
