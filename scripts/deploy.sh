#!/bin/bash
# Production Deployment Script
# Usage: ./deploy.sh <version>

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DEPLOY_DIR="/opt/foodxchange"
BACKUP_DIR="${DEPLOY_DIR}/backups"
LOG_FILE="${DEPLOY_DIR}/logs/deployment.log"
VERSION="${1:-latest}"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
pre_deploy_checks() {
    log "Starting pre-deployment checks..."
    
    # Check disk space
    available_space=$(df -h "$DEPLOY_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if (( $(echo "$available_space < 5" | bc -l) )); then
        error "Insufficient disk space. Available: ${available_space}G, Required: 5G"
    fi
    
    # Check if services are running
    if ! docker compose -f docker-compose.production.yml ps | grep -q "Up"; then
        warning "Some services are not running"
    fi
    
    # Check database connectivity
    if ! docker compose -f docker-compose.production.yml exec -T db pg_isready -U foodxchange; then
        error "Database is not ready"
    fi
    
    log "Pre-deployment checks passed"
}

# Backup current state
backup_current_state() {
    log "Creating backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="${BACKUP_DIR}/backup_${timestamp}.tar.gz"
    
    # Backup database
    docker compose -f docker-compose.production.yml exec -T db \
        pg_dump -U foodxchange foodxchange_prod | \
        gzip > "${BACKUP_DIR}/db_backup_${timestamp}.sql.gz"
    
    # Backup current docker images
    docker images --format "{{.Repository}}:{{.Tag}}" | \
        grep foodxchange > "${BACKUP_DIR}/images_${timestamp}.txt"
    
    # Create deployment snapshot
    echo "VERSION=${VERSION}" > "${BACKUP_DIR}/deployment_${timestamp}.info"
    echo "TIMESTAMP=${timestamp}" >> "${BACKUP_DIR}/deployment_${timestamp}.info"
    echo "DEPLOYED_BY=${USER}" >> "${BACKUP_DIR}/deployment_${timestamp}.info"
    
    log "Backup completed: ${backup_file}"
}

# Deploy new version
deploy() {
    log "Starting deployment of version ${VERSION}..."
    
    # Pull new images
    log "Pulling new images..."
    docker compose -f docker-compose.production.yml pull
    
    # Deploy with zero downtime using rolling update
    log "Performing rolling update..."
    
    # Scale up new containers
    docker compose -f docker-compose.production.yml up -d --no-deps --scale web=2 web
    
    # Wait for new containers to be healthy
    log "Waiting for new containers to be healthy..."
    sleep 30
    
    # Check health of new containers
    for i in {1..30}; do
        if docker compose -f docker-compose.production.yml exec -T web curl -f http://localhost:8000/health; then
            log "New containers are healthy"
            break
        fi
        
        if [ $i -eq 30 ]; then
            error "New containers failed health check"
        fi
        
        sleep 10
    done
    
    # Remove old containers
    log "Removing old containers..."
    docker compose -f docker-compose.production.yml up -d --no-deps web
    
    # Run database migrations
    log "Running database migrations..."
    docker compose -f docker-compose.production.yml exec -T web alembic upgrade head
    
    # Clean up old images
    log "Cleaning up old images..."
    docker image prune -af
    
    log "Deployment completed successfully!"
}

# Post-deployment checks
post_deploy_checks() {
    log "Running post-deployment checks..."
    
    # Check service health
    if ! docker compose -f docker-compose.production.yml exec -T web curl -f http://localhost:8000/health; then
        error "Health check failed after deployment"
    fi
    
    # Check version
    deployed_version=$(docker compose -f docker-compose.production.yml exec -T web curl -s http://localhost:8000/api/version | jq -r '.version')
    if [ "$deployed_version" != "$VERSION" ]; then
        warning "Version mismatch. Expected: ${VERSION}, Got: ${deployed_version}"
    fi
    
    # Check database connectivity
    if ! docker compose -f docker-compose.production.yml exec -T web python -c "from foodxchange.database import get_db; list(get_db())"; then
        error "Database connectivity check failed"
    fi
    
    log "Post-deployment checks passed"
}

# Main deployment flow
main() {
    log "=== Starting FoodXchange Production Deployment ==="
    log "Version: ${VERSION}"
    
    cd "$DEPLOY_DIR"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$BACKUP_DIR"
    
    # Execute deployment steps
    pre_deploy_checks
    backup_current_state
    deploy
    post_deploy_checks
    
    log "=== Deployment completed successfully ==="
    log "Version ${VERSION} is now live!"
    
    # Send notification (if configured)
    if [ -n "${SLACK_WEBHOOK:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"✅ FoodXchange ${VERSION} deployed successfully!\"}" \
            "$SLACK_WEBHOOK"
    fi
}

# Run main function
main "$@"