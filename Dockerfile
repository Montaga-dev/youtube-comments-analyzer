# Multi-stage build for React + FastAPI
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /app/client
COPY client/package*.json ./
RUN npm ci --only=production
COPY client/ ./
RUN npm run build

# Python backend
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY server/ ./

# Copy built frontend
COPY --from=frontend-build /app/client/build ./static

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "main.py"] 