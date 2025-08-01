# FoodXchange Dev Container Setup

This guide explains how to use the development container for FoodXchange, which provides a consistent development environment with all dependencies pre-configured.

## Prerequisites

1. **Docker Desktop** - Must be installed and running
2. **VS Code** - Latest version recommended
3. **Dev Containers Extension** - Install from VS Code marketplace

## Quick Start

### Option 1: Using VS Code (Recommended)

1. **Open the project in VS Code**
   ```bash
   code .
   ```

2. **Open in Dev Container**
   - Press `F1` or `Ctrl+Shift+P`
   - Type "Dev Containers: Reopen in Container"
   - Press `Enter`

3. **Wait for build**
   - The container will build automatically
   - This may take a few minutes on first run
   - Subsequent starts will be much faster

### Option 2: Using Docker Compose directly

```bash
# Build and start the dev environment
docker-compose -f docker-compose.dev.yml up -d

# Access the container
docker exec -it foodxchange-dev bash
```

## What's Included

The dev container provides:

- **Python 3.11** with all dependencies installed
- **PostgreSQL 15** database (port 5432)
- **Redis 7** cache (port 6379)
- **Development tools**: pytest, black, flake8, mypy, etc.
- **VS Code extensions** pre-configured
- **Auto-reload** development server

## Starting the Development Server

Once inside the dev container:

### Option 1: Direct command
```bash
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload
```

### Option 2: Using the provided script
```bash
./start_server_9000.sh
```

### Option 3: Using the dev server script
```bash
python dev_server.py
```

## Port Forwarding

The dev container automatically forwards these ports:

- **9000** - FoodXchange application
- **5432** - PostgreSQL database
- **6379** - Redis cache

## Development Workflow

1. **Start the dev container** (see Quick Start above)
2. **Start the server** (see Starting the Development Server above)
3. **Make changes** to your code
4. **Auto-reload** will automatically restart the server
5. **View changes** at http://localhost:9000

## Database Setup

The PostgreSQL database is automatically initialized with:

- Database: `foodxchange_dev`
- User: `postgres`
- Password: `postgres`
- Connection: `postgresql://postgres:postgres@db:5432/foodxchange_dev`

## Environment Variables

The dev container sets these environment variables:

```bash
FLASK_ENV=development
FLASK_DEBUG=1
PORT=9000
PYTHONPATH=/workspace
DATABASE_URL=postgresql://postgres:postgres@db:5432/foodxchange_dev
REDIS_URL=redis://redis:6379/0
```

## VS Code Extensions

The following extensions are automatically installed:

- Python (ms-python.python)
- Flake8 (ms-python.flake8)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- Jupyter (ms-toolsai.jupyter)
- Docker (ms-azuretools.vscode-docker)
- Tailwind CSS (bradlc.vscode-tailwindcss)
- Prettier (esbenp.prettier-vscode)
- JSON (ms-vscode.vscode-json)
- YAML (redhat.vscode-yaml)
- PowerShell (ms-vscode.powershell)

## Troubleshooting

### Container won't start
1. Ensure Docker Desktop is running
2. Check available disk space
3. Try rebuilding: `docker-compose -f docker-compose.dev.yml build --no-cache`

### Port conflicts
If ports 9000, 5432, or 6379 are already in use:
1. Stop other services using these ports
2. Or modify the port mappings in `docker-compose.dev.yml`

### Database connection issues
1. Ensure the database container is running: `docker ps`
2. Check logs: `docker logs foodxchange-dev-db`
3. Restart the database: `docker restart foodxchange-dev-db`

### Permission issues
The container runs as the `vscode` user (UID 1000). If you encounter permission issues:
```bash
sudo chown -R 1000:1000 .
```

## Stopping the Dev Container

### From VS Code
- Close VS Code
- Or use "Dev Containers: Rebuild Container" to restart

### From Docker Compose
```bash
docker-compose -f docker-compose.dev.yml down
```

## Cleaning Up

To completely remove the dev environment:
```bash
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
```

## Benefits of Dev Containers

1. **Consistent Environment** - Same setup across all developers
2. **Isolated Dependencies** - No conflicts with local Python installations
3. **Easy Setup** - New developers can start immediately
4. **Production-like** - Environment matches production closely
5. **Version Control** - Environment configuration is versioned
6. **Clean Slate** - Easy to reset to a clean state

## Next Steps

Once the dev container is running:

1. **Explore the codebase** - All files are mounted in `/workspace`
2. **Run tests** - `pytest tests/`
3. **Format code** - `black .` and `isort .`
4. **Check linting** - `flake8 .`
5. **Start developing** - Make changes and see them auto-reload! 