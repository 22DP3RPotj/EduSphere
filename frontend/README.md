# Frontend (Vue)

The frontend is built using **Vue.js** and interacts with the **Django** backend via API.

## Features
- Course listing and search with filters
- Secure authentication via JWT
- Payment integration
- Real-time chat with WebSocket support
- User dashboards (Creator, Learner, Admin)

## Architecture Overview
- **Framework**: Vue 3 + Vue Router
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **API Communication**: Fetches data from Django backend

## Running the Frontend
Refer to the main [README](../README.md) for installation and setup instructions.

To start the frontend development server:
```bash
npm run dev
```

## Linting and Building
```bash
npm run lint  # Lint the code
npm run build  # Minify and prepare for production
```

## Installation
For installation instructions, refer to the main [README](../README.md#installation-guide).
