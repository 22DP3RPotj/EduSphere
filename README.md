# Course Marketplace Platform

[![Project License](LICENSE)](https://opensource.org/licenses/MIT)

A full-stack course marketplace platform with real-time communication features. Built with Django (backend) and Vue.js (frontend).

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation Guide](#installation-guide)
  - [Prerequisites](#prerequisites)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Manual Setup](#manual-setup)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
    - [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Multi-role System**: Creators, Learners, and Admins
- **Course Management**: Create, publish, and sell courses
- **Real-Time Chat**: WebSocket-based messaging system
- **Payment Processing**: Integrated Stripe/PayPal payments
- **Advanced Search**: Filter courses by price, rating, and category
- **Admin Dashboard**: Manage users, courses, and transactions

## Architecture Overview

### Backend (Django)
- **Framework**: Django + Django Channels
- **Database**: PostgreSQL (primary), Redis (real-time)
- **APIs**: GraphQL endpoints
- **Authentication**: JWT with OAuth2 social login
- **Key Features**:
  - WebSocket implementation for chat
  - Commission-based payment system
  - Role-based access control

### Frontend (Vue.js)
- **Framework**: Vue 3 + Vue Router
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Key Features**:
  - Responsive course marketplace UI
  - Interactive dashboards
  - Real-time chat interface

## Installation Guide

### Prerequisites
- For Docker setup: Docker and Docker Compose
- For manual setup:
  - Python 3.9+
  - Node.js 16+
  - PostgreSQL 14+
  - Redis 6+

### Docker Setup (Recommended)

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


#### PostgreSQL Backup & Restore

##### Backup PostgreSQL Database

```bash
docker exec -t edusphere-postgres-1 pg_dump -U <db_user> -d coredb > backup.sql
```

##### Restore PostgreSQL Backup

```bash
docker exec -i edusphere-postgres-1 psql -U <db_user> -d coredb < backup.sql
```

### Manual Setup

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
4. Configure environment variables (create `.env` file):
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

## Project Structure
```
.
├── backend/
│   ├── config/          # Django settings and routing
│   ├── core/            # Main application logic
│   ├── requirements.txt
│   └── README.md        # Technical backend documentation
├── frontend/
│   ├── public/
│   ├── src/             # Vue components and stores
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
├── docker-bake.hcl      # Docker Bake configuration
├── docker-bake.sh       # Docker Bake helper script
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
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
