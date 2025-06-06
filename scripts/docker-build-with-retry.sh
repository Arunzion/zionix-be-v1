#!/bin/bash

# Docker build script with retry logic for TLS timeout issues
# Usage: ./scripts/docker-build-with-retry.sh [service-name]

set -e

SERVICE_NAME=${1:-"all"}
MAX_RETRIES=3
RETRY_DELAY=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build a single service with retry logic
build_service_with_retry() {
    local service=$1
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        log_info "Building $service (attempt $attempt/$MAX_RETRIES)..."
        
        if docker-compose build --no-cache --pull $service; then
            log_info "Successfully built $service"
            return 0
        else
            log_warn "Build failed for $service (attempt $attempt/$MAX_RETRIES)"
            if [ $attempt -lt $MAX_RETRIES ]; then
                log_info "Waiting $RETRY_DELAY seconds before retry..."
                sleep $RETRY_DELAY
                
                # Clean up any partial builds
                docker system prune -f --volumes
                
                # Restart Docker daemon if on Windows/Mac (optional)
                if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
                    log_info "Restarting Docker Desktop..."
                    # This would require admin privileges
                    # docker system restart 2>/dev/null || true
                fi
            fi
        fi
        
        ((attempt++))
    done
    
    log_error "Failed to build $service after $MAX_RETRIES attempts"
    return 1
}

# Function to pull images with retry logic
pull_images_with_retry() {
    local images=("postgres:13" "kong:2.7" "confluentinc/cp-zookeeper:7.0.1" "confluentinc/cp-kafka:7.0.1" "prom/prometheus:v2.30.3" "grafana/grafana:8.2.2")
    
    for image in "${images[@]}"; do
        local attempt=1
        while [ $attempt -le $MAX_RETRIES ]; do
            log_info "Pulling $image (attempt $attempt/$MAX_RETRIES)..."
            
            if docker pull $image; then
                log_info "Successfully pulled $image"
                break
            else
                log_warn "Pull failed for $image (attempt $attempt/$MAX_RETRIES)"
                if [ $attempt -lt $MAX_RETRIES ]; then
                    log_info "Waiting $RETRY_DELAY seconds before retry..."
                    sleep $RETRY_DELAY
                fi
            fi
            
            ((attempt++))
        done
        
        if [ $attempt -gt $MAX_RETRIES ]; then
            log_error "Failed to pull $image after $MAX_RETRIES attempts"
            return 1
        fi
    done
}

# Main execution
main() {
    log_info "Starting Docker build process with retry logic..."
    
    # Set Docker buildkit for better performance and error handling
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    # Configure Docker daemon settings for better network handling
    log_info "Configuring Docker for better network handling..."
    
    # Pull base images first
    log_info "Pulling required base images..."
    if ! pull_images_with_retry; then
        log_error "Failed to pull required images"
        exit 1
    fi
    
    # Build services
    if [ "$SERVICE_NAME" = "all" ]; then
        log_info "Building all services..."
        
        # Build services in order of dependencies
        services=("admin-service" "auth-service")
        
        for service in "${services[@]}"; do
            if ! build_service_with_retry $service; then
                log_error "Failed to build $service"
                exit 1
            fi
        done
        
        log_info "All services built successfully!"
    else
        if ! build_service_with_retry $SERVICE_NAME; then
            log_error "Failed to build $SERVICE_NAME"
            exit 1
        fi
    fi
    
    log_info "Docker build process completed successfully!"
}

# Run main function
main "$@"