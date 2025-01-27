# Build stage
FROM node:18-slim as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-slim
WORKDIR /app

COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./

# Install dependencies including react-scripts
RUN npm ci

EXPOSE 3000
CMD ["npm", "start"]