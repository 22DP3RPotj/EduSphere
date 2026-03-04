# Build stage - Build the Vue.js frontend
FROM node:alpine AS builder

WORKDIR /app

RUN npm install -g pnpm

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install

COPY frontend/ ./
RUN pnpm build

# Production stage - Nginx with built frontend
FROM nginx:stable-alpine

RUN apk add --no-cache apache2-utils

COPY --from=builder /app/dist /usr/share/nginx/html

COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
