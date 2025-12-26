# Frontend (Vue)

The frontend is built using **Vue.js** and interacts with the **Django** backend via GraphQL API.

## Features
- Real-time chat interface with WebSocket support
- Secure authentication via JWT
- Chat room management
- Message editing and deletion
- Responsive design for desktop and mobile

## Architecture Overview
- **Framework**: Vue 3 + Vue Router
- **State Management**: Pinia
- **Styling**: CSS
- **API Communication**: GraphQL queries and mutations to Django backend
- **WebSocket**: Real-time message updates via Channels

## Running the Frontend

### Docker Setup
Refer to the main [README](../README.md#docker-setup) for Docker installation and setup instructions.

The frontend is automatically built and served via Nginx in Docker.

### Local Development

To start the frontend development server:
```bash
npm run dev
```

## Building for Production

```bash
npm run build  # Build optimized production bundle
```

## Code Quality

```bash
npm run lint  # Lint the code for issues
```

## Installation
For installation and setup instructions, refer to the main [README](../README.md#installation-guide).
