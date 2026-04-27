# Stage 1: Build
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Runtime: generate env-config.js from environment variables
CMD echo "window.__ENV__ = { REACT_APP_API_URL: \"${REACT_APP_API_URL:-http://localhost:8000}\" };" > /usr/share/nginx/html/env-config.js && nginx -g "daemon off;"
