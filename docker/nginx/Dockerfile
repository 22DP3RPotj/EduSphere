# Build stage - Build the Vue.js frontend
FROM node:alpine AS builder

WORKDIR /app

RUN npm install -g pnpm@10

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install

COPY frontend/ ./
RUN pnpm build

# Production stage - Nginx with built frontend
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY docker/nginx/templates/nginx.conf.template /etc/nginx/templates/default.conf.template


EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
