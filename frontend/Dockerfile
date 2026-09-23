# ----------------------
# Stage 1 — Install dependencies
# ----------------------
FROM node:22-alpine AS deps
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# ----------------------
# Stage 2 — Build
# ----------------------
FROM node:22-alpine AS builder
WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the app
COPY . .

# Copy .env into the build context so Next.js can read it
COPY .env .env

# Build Next.js app
RUN npm run build

# ----------------------
# Stage 3 — Production runner
# ----------------------
FROM node:22-alpine AS runner
WORKDIR /app

# Copy build output and public folder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY package*.json ./

# Install only production dependencies
RUN npm ci --omit=dev

# Expose port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
