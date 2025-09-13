#!/bin/bash

# Deployment script for py2048
# This script is executed on the remote server via GitHub Actions

set -e

echo "🚀 Starting py2048 deployment..."

# Configuration
DEPLOY_DIR="~/py2048"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to deployment directory
cd $DEPLOY_DIR

# Check if .env file exists
if [[ ! -f $ENV_FILE ]]; then
    print_error ".env file not found!"
    print_error "This file should have been created automatically by GitHub Actions."
    print_error "If running manual deployment, please create .env file with required variables:"
    echo ""
    echo "Required variables:"
    echo "  DASHSCOPE_API_KEY=your_api_key_here"
    echo "  MODEL_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1"
    echo "  DEFAULT_MODEL=qwen-plus" 
    echo "  INVIT_CODE=PLAY!2048"
    echo "  NODE_ENV=production"
    echo "  PYTHONPATH=/app"
    echo ""
    exit 1
else
    print_success ".env file found and configured"
    print_status "Environment configuration:"
    # Show configured values (without exposing sensitive data)
    if grep -q "DASHSCOPE_API_KEY=" $ENV_FILE; then
        echo "  ✅ AI API Key configured"
    else
        print_warning "  ⚠️  AI API Key not found"
    fi
    
    if grep -q "MODEL_API_URL=" $ENV_FILE; then
        echo "  ✅ AI Model URL configured" 
    else
        print_warning "  ⚠️  AI Model URL not found"
    fi
    
    if grep -q "INVIT_CODE=" $ENV_FILE; then
        echo "  ✅ Invitation code configured"
    else
        print_warning "  ⚠️  Invitation code not found"
    fi
fi

# Login to GitHub Container Registry
print_status "Logging into GitHub Container Registry..."
if [[ -n "$GITHUB_TOKEN" ]]; then
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin
else
    print_error "GITHUB_TOKEN not found in environment"
    exit 1
fi

# Pull latest images
print_status "Pulling latest Docker images..."
docker pull ghcr.io/awesomepenguin/py2048-backend:latest
docker pull ghcr.io/awesomepenguin/py2048-frontend:latest

# Stop existing containers (if any)
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Clean up old images and containers
print_status "Cleaning up old Docker resources..."
docker system prune -f --volumes || true

# Start new containers
print_status "Starting new containers..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check backend health
backend_health=$(docker-compose exec -T backend curl -f http://localhost:8000/status || echo "failed")
if [[ $backend_health == *"failed"* ]]; then
    print_error "Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# Check frontend health
frontend_health=$(docker-compose exec -T frontend wget --no-verbose --tries=1 --spider http://localhost:3000 || echo "failed")
if [[ $frontend_health == *"failed"* ]]; then
    print_error "Frontend health check failed"
    docker-compose logs frontend
    exit 1
fi

# Check nginx health
nginx_health=$(docker-compose exec -T nginx nginx -t || echo "failed")
if [[ $nginx_health == *"failed"* ]]; then
    print_error "Nginx configuration test failed"
    docker-compose logs nginx
    exit 1
fi

print_success "All services are healthy!"

# Show running containers
print_status "Running containers:"
docker-compose ps

# Show service URLs
print_success "Deployment completed successfully! 🎉"
echo ""
echo "Services are available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  Nginx (Load Balancer): http://localhost:80"
echo ""
echo "To check logs: docker-compose logs -f [service_name]"
echo "To restart services: docker-compose restart"
echo "To stop services: docker-compose down"
echo ""
print_status "Deployment finished at $(date)"
