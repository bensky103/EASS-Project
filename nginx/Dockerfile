# Stage 1: Build frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY ../stock-frontend/package.json ../stock-frontend/package-lock.json ./
RUN npm ci
COPY ../stock-frontend .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html 