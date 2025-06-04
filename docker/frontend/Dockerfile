# docker/frontend/Dockerfile
# Build stage
FROM node:slim AS builder

WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy the package.json and install dependencies
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install

# Copy the frontend source code
COPY frontend/ ./
RUN pnpm build

# Serve stage - copy built files to nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config if you have one for frontend
# COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
