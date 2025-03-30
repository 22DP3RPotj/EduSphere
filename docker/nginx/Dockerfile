FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /app/staticfiles

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
