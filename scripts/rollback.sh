#!/bin/bash
# Production Rollback Script
# Usage: ./rollback.sh [backup_timestamp]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DEPLOY_DIR="/opt/foodxchange"
BACKUP_DIR="${DEPLOY_DIR}/backups"
LOG_FILE="${DEPLOY_DIR}/logs/rollback.log"

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

# Find latest backup
find_latest_backup() {
    if [ -n "${1:-}" ]; then
        # Use specified backup
        backup_timestamp="$1"
    else
        # Find latest backup
        backup_timestamp=$(ls -t "${BACKUP_DIR}"/deployment_*.info 2>/dev/null | head -1 | sed 's/.*deployment_\(.*\)\.info/\1/')
        
        if [ -z "$backup_timestamp" ]; then
            error "No backup found to rollback to"
        fi
    fi
    
    log "Using backup from: ${backup_timestamp}"
}

# Verify backup files
verify_backup() {
    log "Verifying backup files..."
    
    required_files=(
        "${BACKUP_DIR}/db_backup_${backup_timestamp}.sql.gz"
        "${BACKUP_DIR}/images_${backup_timestamp}.txt"
        "${BACKUP_DIR}/deployment_${backup_timestamp}.info"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Required backup file missing: $file"
        fi
    done
    
    log "Backup files verified"
}

# Rollback database
rollback_database() {
    log "Rolling back database..."
    
    # Create current backup before rollback
    current_timestamp=$(date +%Y%m%d_%H%M%S)
    docker compose -f docker-compose.production.yml exec -T db \
        pg_dump -U foodxchange foodxchange_prod | \
        gzip > "${BACKUP_DIR}/db_pre_rollback_${current_timestamp}.sql.gz"
    
    # Restore database from backup
    log "Restoring database from backup..."
    gunzip -c "${BACKUP_DIR}/db_backup_${backup_timestamp}.sql.gz" | \
        docker compose -f docker-compose.production.yml exec -T db \
        psql -U foodxchange foodxchange_prod
    
    log "Database rollback completed"
}

# Rollback application
rollback_application() {
    log "Rolling back application..."
    
    # Read deployment info
    source "${BACKUP_DIR}/deployment_${backup_timestamp}.info"
    
    # Pull previous version
    log "Pulling previous version: ${VERSION}"
    export VERSION
    docker compose -f docker-compose.production.yml pull
    
    # Deploy previous version
    log "Deploying previous version..."
    docker compose -f docker-compose.production.yml up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Health check
    for i in {1..30}; do
        if docker compose -f docker-compose.production.yml exec -T web curl -f http://localhost:8000/health; then
            log "Services are healthy"
            break
        fi
        
        if [ $i -eq 30 ]; then
            error "Services failed health check after rollback"
        fi
        
        sleep 10
    done
    
    log "Application rollback completed"
}

# Post-rollback checks
post_rollback_checks() {
    log "Running post-rollback checks..."
    
    # Check service health
    if ! docker compose -f docker-compose.production.yml exec -T web curl -f http://localhost:8000/health; then
        error "Health check failed after rollback"
    fi
    
    # Check database connectivity
    if ! docker compose -f docker-compose.production.yml exec -T web python -c "from foodxchange.database import get_db; list(get_db())"; then
        error "Database connectivity check failed"
    fi
    
    log "Post-rollback checks passed"
}

# Main rollback flow
main() {
    log "=== Starting FoodXchange Production Rollback ==="
    
    cd "$DEPLOY_DIR"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Execute rollback steps
    find_latest_backup "$@"
    verify_backup
    
    # Confirm rollback
    echo -e "${YELLOW}WARNING: This will rollback to backup from ${backup_timestamp}${NC}"
    echo -e "${YELLOW}This action cannot be undone without another deployment.${NC}"
    read -p "Type 'ROLLBACK' to confirm: " confirmation
    
    if [ "$confirmation" != "ROLLBACK" ]; then
        log "Rollback cancelled by user"
        exit 0
    fi
    
    rollback_database
    rollback_application
    post_rollback_checks
    
    log "=== Rollback completed successfully ==="
    
    # Send notification (if configured)
    if [ -n "${SLACK_WEBHOOK:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"⚠️ FoodXchange rolled back to ${backup_timestamp}\"}" \
            "$SLACK_WEBHOOK"
    fi
}

# Run main function
main "$@"