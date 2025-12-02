# 🐳 Docker Setup Guide for Cursor Cloud Agents

This guide explains how to use Docker with the One Development AI Agent for Cursor cloud agents.

## 📋 Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)
- OpenAI API key (for the AI agent)

## 🚀 Quick Start

### Option 1: Using Dockerfile Directly (For Cursor Cloud Agents Snapshot)

This is the recommended approach for creating a machine snapshot in Cursor:

```bash
# Build the Docker image
docker build -t onedev-agent:latest .

# Run the container interactively (for development/snapshot)
docker run -it --rm \
  -p 8000:8000 \
  -p 3000:3000 \
  -e OPENAI_API_KEY=your-api-key-here \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=onedevelopment_agent \
  -e DB_USER=postgres \
  -e DB_PASSWORD=your-password \
  -v $(pwd)/backend:/app/backend \
  -v $(pwd)/frontend:/app/frontend \
  onedev-agent:latest bash
```

### Option 2: Using Docker Compose (Full Stack)

For a complete setup with PostgreSQL and Redis:

1. **Create a `.env` file** in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=onedevelopment_agent
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Redis
REDIS_URL=redis://redis:6379/0

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
```

2. **Start all services:**

```bash
docker-compose up -d
```

3. **Initialize the database:**

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Initialize data
docker-compose exec backend python manage.py init_data

# Create superuser (optional)
docker-compose exec backend python manage.py createsuperuser
```

4. **Access the application:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

## 🔧 Dockerfile Details

The main Dockerfile includes:

- **Python 3.9** - Base runtime
- **Node.js 18** - For frontend development
- **PostgreSQL client** - Database connectivity
- **All Python dependencies** - From `backend/requirements.txt`
- **All Node dependencies** - From `frontend/package.json`
- **Development tools** - Git, curl, wget

## 📦 Container Structure

```
/app/
├── backend/          # Django backend application
├── frontend/         # React frontend application
└── data_ingestion/   # Data ingestion scripts
```

## 🛠️ Common Commands

### Build the image

```bash
docker build -t onedev-agent:latest .
```

### Run migrations

```bash
docker-compose exec backend python manage.py migrate
```

### Access Django shell

```bash
docker-compose exec backend python manage.py shell
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services

```bash
docker-compose down
```

### Stop and remove volumes (clean slate)

```bash
docker-compose down -v
```

### Rebuild after code changes

```bash
docker-compose up -d --build
```

## 🎯 For Cursor Cloud Agents

When setting up a machine snapshot in Cursor:

1. **Use the Dockerfile directly** - This creates a complete development environment
2. **The container includes:**
   - All Python dependencies installed
   - All Node.js dependencies installed
   - PostgreSQL client for database access
   - Git for version control
   - All development tools

3. **After taking the snapshot, you can:**
   - Run `python manage.py runserver` to start Django
   - Run `npm start` in the frontend directory to start React
   - Access the application on ports 8000 and 3000

## 🔐 Environment Variables

Required environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DB_NAME` - Database name (default: onedevelopment_agent)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `SECRET_KEY` - Django secret key (generate a new one for production)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

## 🐛 Troubleshooting

### Port already in use

If ports 8000 or 3000 are already in use:

```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
  - "3001:3000"  # Use 3001 instead of 3000
```

### Database connection issues

Make sure the database service is healthy:

```bash
docker-compose ps
docker-compose logs db
```

### Permission issues

If you encounter permission issues with volumes:

```bash
# On Linux/Mac
sudo chown -R $USER:$USER ./backend ./frontend

# Or run with user mapping
docker run -u $(id -u):$(id -g) ...
```

### Rebuild from scratch

```bash
# Remove everything
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

## 📝 Notes

- The Dockerfile is optimized for development and includes all dependencies
- For production, consider using multi-stage builds and optimizing the image size
- ChromaDB data is stored in a volume for persistence
- Static files are collected in a volume for better performance
- Media files (PDFs) are stored in a volume

## 🔗 Related Documentation

- [README.md](README.md) - Project overview
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [SETUP.md](SETUP.md) - Detailed setup instructions



