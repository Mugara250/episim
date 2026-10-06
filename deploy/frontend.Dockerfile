# Production frontend: builds the Vite SPA, then serves it (and proxies the
# API) from Caddy, which provisions HTTPS certificates automatically.
FROM node:20 AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
# Vite inlines this at build time - changing it requires a rebuild.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM caddy:2
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv/dist
