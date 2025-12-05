# Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies with yarn (more reliable)
COPY package*.json yarn.lock* ./
RUN yarn install --frozen-lockfile || yarn install

# Copy source and build
COPY . .
RUN yarn build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
