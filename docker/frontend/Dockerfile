FROM node:18-alpine

WORKDIR /app

# Copy the package.json and install dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy the rest of the application
COPY . .

# Command to run the dev server
ENTRYPOINT ["npm", "--prefix", "frontend", "run"]
CMD ["dev", "--", "--host", "0.0.0.0"]
