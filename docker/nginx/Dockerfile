# docker/nginx/Dockerfile
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
