# Course Marketplace Platform

[![Project License](LICENSE)](https://opensource.org/licenses/MIT)

A full-stack course marketplace platform with real-time communication features. Built with Django (backend) and Vue.js (frontend).

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation Guide](#installation-guide)
  - [Prerequisites](#prerequisites)
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
- **APIs**: REST + GraphQL endpoints
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
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Redis 6+

### Backend Setup
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
   pip install -r requirements.txt --no-binary uvloop  # Omit --no-binary on Linux
   ```
4. Configure environment variables (create `.env` file):
   ```env
   SECRET_KEY=your_django_secret
   DB_NAME=marketplace
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```
5. Run migrations:
   ```bash
   python manage.py makemigrations
   ```
   ```bash
   python manage.py migrate
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application
```bash
./scripts/run.sh
```
#### Start backend (from `backend` directory):
```bash
python manage.py runserver
```
#### Start frontend (from `frontend` directory):
```bash
npm run dev
```
Access the application at [http://localhost:8080](http://localhost:8080)

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
├── scripts/
│   ├── run.sh           # Combined server startup
│   └── test.sh          # Test runner
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

