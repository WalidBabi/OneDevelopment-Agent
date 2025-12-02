# Dockerfile for One Development AI Agent - Cursor Cloud Agents
# This Dockerfile sets up a complete development environment for the AI agent

FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_VERSION=18.x

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client
    postgresql-client \
    # Build tools for Python packages
    gcc \
    g++ \
    make \
    # Git for version control
    git \
    # Curl and wget for downloads
    curl \
    wget \
    # Node.js and npm (for frontend development)
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - \
    && apt-get install -y nodejs \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/backend/requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy backend code
COPY backend/ /app/backend/

# Copy frontend package files
COPY frontend/package*.json /app/frontend/

# Install frontend dependencies
RUN cd /app/frontend && npm install

# Copy frontend code
COPY frontend/ /app/frontend/

# Copy other necessary files
COPY data_ingestion/ /app/data_ingestion/ 2>/dev/null || true
COPY *.md /app/ 2>/dev/null || true
COPY *.sh /app/ 2>/dev/null || true

# Set working directory to backend
WORKDIR /app/backend

# Create directories for static files, media, and ChromaDB
RUN mkdir -p /app/backend/staticfiles \
    /app/backend/media \
    /app/backend/chroma_db

# Expose ports
# 8000 for Django backend
# 3000 for React frontend (development)
EXPOSE 8000 3000

# Default command - can be overridden
# This allows the container to be used interactively for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



