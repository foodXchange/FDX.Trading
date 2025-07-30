#!/bin/bash

# FoodXchange Docker Development Aliases
# Add this to your ~/.bashrc or ~/.zshrc:
# source /path/to/foodxchange/scripts/docker-aliases.sh

# Basic Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcr='docker-compose restart'
alias dcl='docker-compose logs -f'
alias dcb='docker-compose build'
alias dce='docker-compose exec'
alias dcp='docker-compose ps'

# FoodXchange specific commands
alias fx-up='docker-compose up -d && echo "🚀 FoodXchange is running on http://localhost:8003"'
alias fx-down='docker-compose down'
alias fx-restart='docker-compose restart web'
alias fx-logs='docker-compose logs -f web'
alias fx-logs-all='docker-compose logs -f'
alias fx-status='docker-compose ps'

# Development commands
alias fx-shell='docker-compose exec web bash'
alias fx-python='docker-compose exec web python'
alias fx-pip='docker-compose exec web pip'
alias fx-test='docker-compose exec web python -m pytest'
alias fx-test-azure='docker-compose exec web python azure_connection_test.py'
alias fx-health='docker-compose exec web python quick_health_check.py'
alias fx-validate='docker-compose exec web python validate_endpoints.py'

# Database commands
alias fx-db='docker-compose exec postgres psql -U postgres -d foodxchange'
alias fx-db-shell='docker-compose exec postgres bash'
alias fx-migrate='docker-compose exec web python manage.py migrate'
alias fx-makemigrations='docker-compose exec web python manage.py makemigrations'
alias fx-dbshell='docker-compose exec web python manage.py dbshell'

# Build and maintenance
alias fx-build='docker-compose build'
alias fx-rebuild='docker-compose build --no-cache'
alias fx-pull='docker-compose pull'
alias fx-clean='docker system prune -f'
alias fx-clean-all='docker-compose down -v && docker system prune -af'

# Quick development workflow
alias fx-dev='fx-up && fx-logs'
alias fx-fresh='fx-down && fx-up && fx-health'
alias fx-reset='docker-compose down -v && docker-compose up -d --build'

# Backup and restore
alias fx-backup='docker-compose exec -T postgres pg_dump -U postgres foodxchange | gzip > foodxchange_backup_$(date +%Y%m%d_%H%M%S).sql.gz'
alias fx-restore='gunzip -c $1 | docker-compose exec -T postgres psql -U postgres foodxchange'

# Resource monitoring
alias fx-stats='docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
alias fx-top='docker-compose top'

# Azure specific
alias fx-azure-test='docker-compose exec web python scripts/run_all_azure_tests.py'
alias fx-azure-monitor='docker-compose logs -f azure-health'

# Helper functions

# Execute command in web container
fx-exec() {
    docker-compose exec web "$@"
}

# Run Python script in web container
fx-run() {
    docker-compose exec web python "$@"
}

# Install Python package and update requirements
fx-install() {
    docker-compose exec web pip install "$1"
    echo "Installed $1. Don't forget to add it to requirements.txt!"
}

# Search logs for errors
fx-errors() {
    docker-compose logs --tail=1000 | grep -E "(ERROR|CRITICAL|Exception|Traceback)" --color=always
}

# Quick status check
fx-check() {
    echo "🐳 Docker Status:"
    docker-compose ps
    echo -e "\n🔍 Azure Health:"
    docker-compose exec web python quick_health_check.py 2>/dev/null || echo "Services not running"
    echo -e "\n📊 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Development menu
fx-menu() {
    bash scripts/docker-dev.sh
}

# Print all FoodXchange aliases
fx-help() {
    echo "🐳 FoodXchange Docker Aliases:"
    echo ""
    echo "🚀 Quick Start:"
    echo "  fx-up          - Start all services"
    echo "  fx-down        - Stop all services"
    echo "  fx-dev         - Start and watch logs"
    echo "  fx-menu        - Interactive menu"
    echo ""
    echo "📊 Monitoring:"
    echo "  fx-logs        - Follow web logs"
    echo "  fx-status      - Show container status"
    echo "  fx-health      - Run health check"
    echo "  fx-stats       - Show resource usage"
    echo ""
    echo "🛠 Development:"
    echo "  fx-shell       - Open web shell"
    echo "  fx-db          - Open database console"
    echo "  fx-test        - Run tests"
    echo "  fx-exec <cmd>  - Execute command"
    echo ""
    echo "🧹 Maintenance:"
    echo "  fx-build       - Build containers"
    echo "  fx-clean       - Clean Docker cache"
    echo "  fx-reset       - Full reset"
    echo ""
    echo "💾 Backup:"
    echo "  fx-backup      - Backup database"
    echo "  fx-restore <file> - Restore database"
}

# Completion for fx-exec and fx-run
if [ -n "$BASH_VERSION" ]; then
    complete -F _command fx-exec
    complete -F _command fx-run
fi

echo "✅ FoodXchange Docker aliases loaded! Type 'fx-help' for available commands."