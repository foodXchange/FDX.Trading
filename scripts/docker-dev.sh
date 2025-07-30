#!/bin/bash

# FoodXchange Docker Development Workflow Script
# This script provides all common Docker commands for daily development

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project name
PROJECT_NAME="foodxchange"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_success "Docker is running"
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}=== FoodXchange Docker Development Menu ===${NC}"
    echo "1. 🚀 Start Development Environment"
    echo "2. 🛑 Stop Development Environment"
    echo "3. 📊 View Status"
    echo "4. 📜 View Logs"
    echo "5. 🔍 Run Azure Health Check"
    echo "6. 🧪 Run Tests"
    echo "7. 🐚 Open Shell"
    echo "8. 🗄️  Database Console"
    echo "9. 🔄 Restart Services"
    echo "10. 🏗️  Rebuild Containers"
    echo "11. 🧹 Clean Up"
    echo "12. 📦 Backup Database"
    echo "13. 🔧 Development Setup"
    echo "14. 📋 Show Docker Commands Cheatsheet"
    echo "0. Exit"
    echo -n "Select option: "
}

# Start development environment
start_dev() {
    print_status "Starting FoodXchange development environment..."
    
    # Check if .env exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your Azure credentials"
        return
    fi
    
    docker-compose up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 5
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        print_success "All services started successfully!"
        echo -e "\n${GREEN}Access your application at:${NC}"
        echo "  - Application: http://localhost:8003"
        echo "  - Database Admin: http://localhost:8080"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
    else
        print_error "Some services failed to start. Check logs with option 4."
    fi
}

# Stop development environment
stop_dev() {
    print_status "Stopping FoodXchange development environment..."
    docker-compose down
    print_success "All services stopped"
}

# View status
view_status() {
    print_status "FoodXchange Docker Status:"
    docker-compose ps
    echo -e "\n${BLUE}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# View logs
view_logs() {
    echo "Select service to view logs:"
    echo "1. Web Application"
    echo "2. PostgreSQL"
    echo "3. Redis"
    echo "4. Azure Monitor"
    echo "5. All Services"
    echo -n "Select option: "
    read log_option
    
    case $log_option in
        1) docker-compose logs -f --tail=100 web ;;
        2) docker-compose logs -f --tail=100 postgres ;;
        3) docker-compose logs -f --tail=100 redis ;;
        4) docker-compose logs -f --tail=100 azure-health ;;
        5) docker-compose logs -f --tail=100 ;;
        *) print_error "Invalid option" ;;
    esac
}

# Run Azure health check
azure_health_check() {
    print_status "Running Azure health check..."
    docker-compose exec web python quick_health_check.py
    
    print_status "Validating Azure endpoints..."
    docker-compose exec web python validate_endpoints.py
}

# Run tests
run_tests() {
    echo "Select test type:"
    echo "1. All Tests"
    echo "2. Azure Connection Tests"
    echo "3. Unit Tests"
    echo "4. Integration Tests"
    echo -n "Select option: "
    read test_option
    
    case $test_option in
        1) 
            print_status "Running all tests..."
            docker-compose exec web python -m pytest
            ;;
        2) 
            print_status "Running Azure connection tests..."
            docker-compose exec web python azure_connection_test.py
            ;;
        3) 
            print_status "Running unit tests..."
            docker-compose exec web python -m pytest tests/unit/
            ;;
        4) 
            print_status "Running integration tests..."
            docker-compose exec web python -m pytest tests/integration/
            ;;
        *) print_error "Invalid option" ;;
    esac
}

# Open shell
open_shell() {
    echo "Select container:"
    echo "1. Web Application"
    echo "2. PostgreSQL"
    echo "3. Redis"
    echo -n "Select option: "
    read shell_option
    
    case $shell_option in
        1) docker-compose exec web bash ;;
        2) docker-compose exec postgres bash ;;
        3) docker-compose exec redis sh ;;
        *) print_error "Invalid option" ;;
    esac
}

# Database console
db_console() {
    print_status "Opening PostgreSQL console..."
    docker-compose exec postgres psql -U postgres -d foodxchange
}

# Restart services
restart_services() {
    echo "Select service to restart:"
    echo "1. Web Application"
    echo "2. All Services"
    echo -n "Select option: "
    read restart_option
    
    case $restart_option in
        1) 
            print_status "Restarting web application..."
            docker-compose restart web
            ;;
        2) 
            print_status "Restarting all services..."
            docker-compose restart
            ;;
        *) print_error "Invalid option" ;;
    esac
    
    print_success "Services restarted"
}

# Rebuild containers
rebuild_containers() {
    print_status "Rebuilding containers..."
    docker-compose build --no-cache
    print_success "Containers rebuilt successfully"
    
    echo -n "Start services now? (y/n): "
    read start_now
    if [ "$start_now" = "y" ]; then
        start_dev
    fi
}

# Clean up
clean_up() {
    print_warning "Clean up options:"
    echo "1. Remove stopped containers"
    echo "2. Remove all containers (keeps volumes)"
    echo "3. Remove everything (INCLUDING DATA!)"
    echo "4. Clean Docker system"
    echo -n "Select option: "
    read clean_option
    
    case $clean_option in
        1) 
            print_status "Removing stopped containers..."
            docker-compose rm -f
            ;;
        2) 
            print_status "Removing all containers..."
            docker-compose down
            ;;
        3) 
            print_warning "This will DELETE ALL DATA! Are you sure? (yes/no): "
            read confirm
            if [ "$confirm" = "yes" ]; then
                docker-compose down -v --remove-orphans
                print_success "All containers and volumes removed"
            else
                print_status "Cancelled"
            fi
            ;;
        4) 
            print_status "Cleaning Docker system..."
            docker system prune -f
            print_success "Docker system cleaned"
            ;;
        *) print_error "Invalid option" ;;
    esac
}

# Backup database
backup_database() {
    print_status "Backing up database..."
    
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/foodxchange_backup_$TIMESTAMP.sql"
    
    docker-compose exec -T postgres pg_dump -U postgres foodxchange > $BACKUP_FILE
    
    if [ -f $BACKUP_FILE ]; then
        gzip $BACKUP_FILE
        print_success "Database backed up to: ${BACKUP_FILE}.gz"
    else
        print_error "Backup failed"
    fi
}

# Development setup
dev_setup() {
    print_status "Development setup options:"
    echo "1. Install new Python package"
    echo "2. Run database migrations"
    echo "3. Create superuser"
    echo "4. Load sample data"
    echo "5. Generate requirements.txt"
    echo -n "Select option: "
    read setup_option
    
    case $setup_option in
        1) 
            echo -n "Enter package name: "
            read package_name
            docker-compose exec web pip install $package_name
            print_warning "Remember to add $package_name to requirements.txt"
            ;;
        2) 
            print_status "Running database migrations..."
            docker-compose exec web python manage.py migrate
            ;;
        3) 
            print_status "Creating superuser..."
            docker-compose exec web python manage.py createsuperuser
            ;;
        4) 
            print_status "Loading sample data..."
            docker-compose exec web python scripts/load_sample_data.py
            ;;
        5) 
            print_status "Generating requirements.txt..."
            docker-compose exec web pip freeze > requirements.txt
            print_success "requirements.txt updated"
            ;;
        *) print_error "Invalid option" ;;
    esac
}

# Show Docker commands cheatsheet
show_cheatsheet() {
    echo -e "\n${BLUE}=== Docker Commands Cheatsheet ===${NC}"
    echo -e "${GREEN}Container Management:${NC}"
    echo "  docker-compose ps                    # List containers"
    echo "  docker-compose up -d                 # Start in background"
    echo "  docker-compose down                  # Stop and remove"
    echo "  docker-compose restart web           # Restart service"
    echo ""
    echo -e "${GREEN}Logs and Debugging:${NC}"
    echo "  docker-compose logs -f web           # Follow logs"
    echo "  docker-compose exec web bash         # Open shell"
    echo "  docker stats                         # Resource usage"
    echo ""
    echo -e "${GREEN}Development:${NC}"
    echo "  docker-compose exec web python app.py    # Run script"
    echo "  docker-compose build --no-cache          # Rebuild"
    echo "  docker-compose exec web pip install pkg  # Install package"
    echo ""
    echo -e "${GREEN}Database:${NC}"
    echo "  docker-compose exec postgres psql -U postgres -d foodxchange"
    echo ""
    echo -e "${GREEN}Cleanup:${NC}"
    echo "  docker system prune -f               # Clean cache"
    echo "  docker-compose down -v               # Remove everything"
}

# Main loop
main() {
    check_docker
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) start_dev ;;
            2) stop_dev ;;
            3) view_status ;;
            4) view_logs ;;
            5) azure_health_check ;;
            6) run_tests ;;
            7) open_shell ;;
            8) db_console ;;
            9) restart_services ;;
            10) rebuild_containers ;;
            11) clean_up ;;
            12) backup_database ;;
            13) dev_setup ;;
            14) show_cheatsheet ;;
            0) 
                print_status "Exiting..."
                exit 0 
                ;;
            *) print_error "Invalid option" ;;
        esac
        
        echo -e "\nPress Enter to continue..."
        read
    done
}

# Run main function
main