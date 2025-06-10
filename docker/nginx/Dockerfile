# docker/nginx/Dockerfile
# Build stage - Build the Vue.js frontend
FROM node:slim AS builder

WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy the package.json and install dependencies
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install

# Copy the frontend source code and build
COPY frontend/ ./
RUN pnpm build

# Production stage - Nginx with built frontend
FROM nginx:alpine

# Copy the built frontend files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Create directories for static and media files (for Django)
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
