@echo off
setlocal enabledelayedexpansion

REM FoodXchange Management Script with Multi-Environment Support
REM Usage: fx <command> [environment] [options]

if "%1"=="" goto help

REM Set default environment
set ENV=dev
if "%2"=="dev" set ENV=dev
if "%2"=="staging" set ENV=staging
if "%2"=="production" set ENV=production
if "%2"=="prod" set ENV=production

REM ========== Environment Commands ==========
if "%1"=="env" (
    if "%2"=="" (
        echo Current environment: %ENV%
        echo.
        echo Available environments:
        echo   - dev (development)
        echo   - staging
        echo   - production
    ) else (
        echo Switching to %2 environment...
        set ENV=%2
    )
    goto end
)

REM ========== Docker Commands ==========
if "%1"=="start" (
    echo Starting FoodXchange services [%ENV%]...
    
    if "%ENV%"=="production" (
        echo.
        echo WARNING: You cannot start production locally!
        echo Production must be deployed through GitHub Actions.
        echo Use 'fx deploy production' to trigger deployment.
        goto end
    )
    
    docker-compose -f docker-compose.%ENV%.yml up -d
    
    if "%ENV%"=="dev" (
        echo.
        echo Development services started:
        echo - Web app: http://localhost:8003
        echo - Database: localhost:5432
        echo - Redis: localhost:6379
        echo - pgAdmin: http://localhost:5050
    )
    
    if "%ENV%"=="staging" (
        echo.
        echo Staging services started:
        echo - Web app: http://localhost:8000
        echo - Health check: http://localhost:8000/health
    )
    goto end
)

if "%1"=="stop" (
    echo Stopping FoodXchange services [%ENV%]...
    docker-compose -f docker-compose.%ENV%.yml down
    goto end
)

if "%1"=="restart" (
    echo Restarting FoodXchange services [%ENV%]...
    docker-compose -f docker-compose.%ENV%.yml down
    docker-compose -f docker-compose.%ENV%.yml up -d
    goto end
)

if "%1"=="logs" (
    if "%3"=="" (
        docker-compose -f docker-compose.%ENV%.yml logs -f --tail=100
    ) else (
        docker-compose -f docker-compose.%ENV%.yml logs -f --tail=100 %3
    )
    goto end
)

if "%1"=="status" (
    echo FoodXchange services status [%ENV%]:
    docker-compose -f docker-compose.%ENV%.yml ps
    goto end
)

REM ========== Database Commands ==========
if "%1"=="db" (
    set DB_CONTAINER=foodxchange_db_%ENV%
    
    if "%2"=="connect" (
        echo Connecting to %ENV% database...
        docker exec -it %DB_CONTAINER% psql -U foodxchange -d foodxchange_%ENV%
        goto end
    )
    
    if "%2"=="backup" (
        if not exist backups mkdir backups
        set backup_file=foodxchange_%ENV%_backup_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
        set backup_file=!backup_file: =0!
        echo Creating %ENV% database backup: !backup_file!
        docker exec %DB_CONTAINER% pg_dump -U foodxchange foodxchange_%ENV% > backups\!backup_file!
        echo Backup created: backups\!backup_file!
        goto end
    )
    
    if "%2"=="restore" (
        if "%3"=="" (
            echo Usage: fx db restore [backup_file]
            goto end
        )
        echo WARNING: This will overwrite the %ENV% database!
        set /p confirm="Type 'YES' to confirm: "
        if "!confirm!"=="YES" (
            echo Restoring %ENV% database from %3...
            docker exec -i %DB_CONTAINER% psql -U foodxchange foodxchange_%ENV% < %3
            echo Database restored from %3
        ) else (
            echo Restore cancelled.
        )
        goto end
    )
    
    if "%2"=="migrate" (
        echo Running database migrations on %ENV%...
        docker-compose -f docker-compose.%ENV%.yml exec web alembic upgrade head
        goto end
    )
    
    if "%2"=="rollback" (
        echo Rolling back last migration on %ENV%...
        docker-compose -f docker-compose.%ENV%.yml exec web alembic downgrade -1
        goto end
    )
    
    echo Unknown database command: %2
    goto help
)

REM ========== Development Commands ==========
if "%1"=="shell" (
    if "%3"=="" (
        echo Entering web container shell [%ENV%]...
        docker-compose -f docker-compose.%ENV%.yml exec web /bin/sh
    ) else (
        echo Entering %3 container shell [%ENV%]...
        docker-compose -f docker-compose.%ENV%.yml exec %3 /bin/sh
    )
    goto end
)

if "%1"=="test" (
    if "%ENV%"=="production" (
        echo Cannot run tests on production!
        goto end
    )
    echo Running tests in %ENV% environment...
    docker-compose -f docker-compose.%ENV%.yml exec web pytest -v
    goto end
)

if "%1"=="lint" (
    echo Running code linters...
    docker-compose -f docker-compose.%ENV%.yml exec web black --check foodxchange
    docker-compose -f docker-compose.%ENV%.yml exec web flake8 foodxchange
    docker-compose -f docker-compose.%ENV%.yml exec web mypy foodxchange
    goto end
)

if "%1"=="format" (
    echo Formatting code...
    docker-compose -f docker-compose.%ENV%.yml exec web black foodxchange
    goto end
)

REM ========== Deployment Commands ==========
if "%1"=="deploy" (
    if "%2"=="staging" (
        echo Deploying to staging...
        echo.
        echo This will:
        echo 1. Push current branch to 'staging' branch
        echo 2. Trigger automatic staging deployment
        echo.
        set /p confirm="Continue? (y/n): "
        if "!confirm!"=="y" (
            git push origin HEAD:staging
            echo.
            echo Deployment triggered! Check GitHub Actions for progress.
            echo https://github.com/YOUR_REPO/actions
        )
        goto end
    )
    
    if "%2"=="production" (
        echo.
        echo PRODUCTION DEPLOYMENT CHECKLIST:
        echo ================================
        echo [ ] All tests passing on staging?
        echo [ ] Database migrations reviewed?
        echo [ ] Team notified about deployment?
        echo [ ] Rollback plan prepared?
        echo.
        echo To deploy to production:
        echo 1. Go to GitHub Actions
        echo 2. Run "Deploy to Production" workflow
        echo 3. Enter version (e.g., v1.0.0)
        echo 4. Type 'DEPLOY' to confirm
        echo 5. Wait for manual approval
        echo.
        echo URL: https://github.com/YOUR_REPO/actions/workflows/deploy-production.yml
        goto end
    )
    
    echo Unknown deployment target: %2
    echo Available: staging, production
    goto end
)

REM ========== Git Commands ==========
if "%1"=="git" (
    if "%2"=="flow" (
        echo Current Git workflow:
        echo.
        git branch --show-current
        echo.
        echo Branches:
        git branch -a
        echo.
        echo Recent commits:
        git log --oneline -10
        goto end
    )
    
    if "%2"=="push" (
        echo Pushing to remote...
        git push origin HEAD
        echo.
        echo Remember:
        echo - Push to 'main' for development
        echo - Push to 'staging' to deploy to staging
        echo - Use GitHub Actions for production
        goto end
    )
    goto help
)

REM ========== Environment Setup Commands ==========
if "%1"=="setup" (
    if "%2"=="env" (
        echo Setting up environment files...
        
        if not exist .env.development (
            copy .env.example .env.development
            echo Created .env.development
        )
        
        if not exist .env.staging (
            copy .env.example .env.staging
            echo Created .env.staging
            echo.
            echo IMPORTANT: Update .env.staging with staging credentials!
        )
        
        if not exist .env.production (
            copy .env.example .env.production
            echo Created .env.production
            echo.
            echo IMPORTANT: Update .env.production with production credentials!
        )
        goto end
    )
    
    if "%2"=="github" (
        echo.
        echo GitHub Secrets to Configure:
        echo ===========================
        echo.
        echo Repository Secrets:
        echo - AZURE_OPENAI_ENDPOINT
        echo - AZURE_OPENAI_KEY
        echo - STAGING_SSH_KEY
        echo - STAGING_HOST
        echo - STAGING_USER
        echo - PRODUCTION_SSH_KEY
        echo - PRODUCTION_HOSTS (comma-separated)
        echo - PRODUCTION_USER
        echo - SLACK_WEBHOOK (optional)
        echo.
        echo Environment Secrets (staging):
        echo - DB_PASSWORD_STAGING
        echo - REDIS_PASSWORD_STAGING
        echo - SECRET_KEY_STAGING
        echo.
        echo Environment Secrets (production):
        echo - DB_PASSWORD_PROD
        echo - REDIS_PASSWORD_PROD
        echo - SECRET_KEY_PROD
        echo.
        echo Variables:
        echo - PRODUCTION_APPROVERS (comma-separated GitHub usernames)
        goto end
    )
    goto help
)

REM ========== Monitoring Commands ==========
if "%1"=="monitor" (
    if "%2"=="health" (
        echo Checking %ENV% health...
        if "%ENV%"=="dev" (
            curl -f http://localhost:8003/health
        )
        if "%ENV%"=="staging" (
            curl -f http://localhost:8000/health
        )
        goto end
    )
    
    if "%2"=="logs" (
        echo Tailing %ENV% logs...
        docker-compose -f docker-compose.%ENV%.yml logs -f --tail=100
        goto end
    )
    goto help
)

REM ========== Clean Commands ==========
if "%1"=="clean" (
    echo Cleaning up %ENV% Docker resources...
    docker-compose -f docker-compose.%ENV%.yml down -v
    
    if "%2"=="all" (
        echo Cleaning all Docker resources...
        docker system prune -af
        docker volume prune -f
    )
    goto end
)

:help
echo FoodXchange Management Tool - Multi-Environment Support
echo.
echo Usage: fx ^<command^> [environment] [options]
echo.
echo Environments:
echo   dev, staging, production (default: dev)
echo.
echo Docker Commands:
echo   fx start [env]           - Start services
echo   fx stop [env]            - Stop services
echo   fx restart [env]         - Restart services
echo   fx logs [env] [service]  - View logs
echo   fx status [env]          - Show service status
echo   fx clean [env] [all]     - Clean up resources
echo.
echo Database Commands:
echo   fx db connect [env]      - Connect to database
echo   fx db backup [env]       - Create backup
echo   fx db restore [env] file - Restore from backup
echo   fx db migrate [env]      - Run migrations
echo   fx db rollback [env]     - Rollback migration
echo.
echo Development Commands:
echo   fx shell [env] [service] - Enter container shell
echo   fx test [env]            - Run tests
echo   fx lint                  - Run linters
echo   fx format                - Format code
echo.
echo Deployment Commands:
echo   fx deploy staging        - Deploy to staging
echo   fx deploy production     - Show production deploy instructions
echo.
echo Setup Commands:
echo   fx setup env             - Create environment files
echo   fx setup github          - Show GitHub secrets setup
echo.
echo Git Commands:
echo   fx git flow              - Show git workflow status
echo   fx git push              - Push to remote
echo.
echo Monitoring Commands:
echo   fx monitor health [env]  - Check health
echo   fx monitor logs [env]    - Tail logs
echo.
echo Examples:
echo   fx start                 - Start dev environment
echo   fx start staging         - Start staging environment
echo   fx db backup production  - Backup production database
echo   fx deploy staging        - Deploy to staging
echo.

:end
endlocal