#!/bin/bash

# Quick Start Script for One Development AI Agent
# This script automates the initial setup process

set -e

echo "========================================="
echo "One Development AI Agent - Quick Start"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_status "Python 3 found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_status "Node.js found"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL not found in PATH (may still be installed)"
else
    print_status "PostgreSQL found"
fi

echo ""
echo "========================================="
echo "Backend Setup"
echo "========================================="

# Setup backend
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
print_status "Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_status "Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=onedevelopment_agent
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379/0
EOF
    print_status ".env file created"
    print_warning "Please update OPENAI_API_KEY in backend/.env"
else
    print_status ".env file already exists"
fi

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations > /dev/null 2>&1
python manage.py migrate > /dev/null 2>&1
print_status "Database migrations completed"

# Initialize data
echo "Initializing database with suggested questions and knowledge..."
python manage.py init_data > /dev/null 2>&1
print_status "Initial data loaded"

cd ..

echo ""
echo "========================================="
echo "Frontend Setup"
echo "========================================="

# Setup frontend
cd frontend

# Install dependencies
echo "Installing Node.js dependencies (this may take a few minutes)..."
npm install > /dev/null 2>&1
print_status "Node.js dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
    print_status ".env file created"
else
    print_status ".env file already exists"
fi

cd ..

echo ""
echo "========================================="
echo "Setup Complete! 🎉"
echo "========================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start the Django backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "2. In a new terminal, start the React frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo ""
print_warning "Don't forget to:"
echo "   - Update your OpenAI API key in backend/.env"
echo "   - Configure PostgreSQL database if not using default"
echo "   - Create a superuser: python manage.py createsuperuser"
echo ""
echo "For detailed instructions, see SETUP.md"
echo ""

