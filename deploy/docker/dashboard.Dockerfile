FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY dashboard/package.json dashboard/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY dashboard/ .

# Build the Next.js application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]
