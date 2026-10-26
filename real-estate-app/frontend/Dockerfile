# Stage 1: Build the Vite React application
FROM docker.io/library/node:18-alpine AS build
WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Build the app (Vite generates the 'dist' folder)
RUN npm run build

# Stage 2: Serve the app using Nginx
FROM docker.io/library/nginx:alpine
# Copy the built files from Stage 1 into Nginx's public folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]