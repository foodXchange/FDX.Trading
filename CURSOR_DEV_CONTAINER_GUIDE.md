# Using Dev Containers in Cursor

This guide explains how to use the FoodXchange development container specifically with Cursor IDE.

## Quick Start in Cursor

### Step 1: Open Project
1. **Launch Cursor**
2. **Open the FoodXchange project folder**
3. **Ensure Docker Desktop is running**

### Step 2: Start Dev Container
1. **Open Command Palette**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Or press `F1`

2. **Start Container**
   - Type: `Dev Containers: Reopen in Container`
   - Press Enter

3. **Wait for Build**
   - Cursor will build the container (first time takes a few minutes)
   - You'll see a notification when ready

### Step 3: Start Development Server
Once inside the container, open Cursor's integrated terminal and run:

```bash
# Option 1: Direct command
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload

# Option 2: Using the script
./start_server_9000.sh

# Option 3: Using the dev server
python dev_server.py
```

## Cursor-Specific Features

### AI Integration
- **Code Completion**: Works with the container's Python environment
- **Chat**: Can reference the container's file system and dependencies
- **Code Generation**: Understands the project structure inside the container

### Terminal Integration
- **Integrated Terminal**: Runs inside the container automatically
- **Multiple Terminals**: Can open multiple terminal tabs
- **Command History**: Preserved across container sessions

### Debugging
- **Python Debugger**: Works seamlessly with container environment
- **Breakpoints**: Set and hit breakpoints inside the container
- **Variable Inspection**: Access container environment variables

### File System
- **Live Sync**: Changes made in Cursor are immediately reflected in the container
- **Mount Points**: All project files are mounted at `/workspace`
- **Permissions**: Proper file permissions handled automatically

## Development Workflow in Cursor

### 1. Code Editing
- Edit files normally in Cursor
- Changes are automatically synced to the container
- Auto-reload will restart the server when you save

### 2. Terminal Commands
```bash
# Check if you're in the container
ls -la /.dockerenv

# Install additional packages
pip install package-name

# Run tests
pytest tests/

# Format code
black .
isort .

# Check linting
flake8 .
```

### 3. Database Access
```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@db:5432/foodxchange_dev

# Connect to Redis
redis-cli -h redis -p 6379
```

### 4. Package Management
```bash
# Install new dependencies
pip install new-package

# Update requirements
pip freeze > requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

## Cursor Extensions in Container

The following extensions are automatically available:

- **Python** - Full Python language support
- **Flake8** - Linting
- **Black Formatter** - Code formatting
- **isort** - Import sorting
- **Jupyter** - Notebook support
- **Docker** - Docker integration
- **Tailwind CSS** - CSS framework support
- **Prettier** - Code formatting
- **JSON** - JSON support
- **YAML** - YAML support

## Troubleshooting in Cursor

### Container Won't Start
1. **Check Docker**: Ensure Docker Desktop is running
2. **Check Ports**: Ensure ports 9000, 5432, 6379 are free
3. **Rebuild**: Use "Dev Containers: Rebuild Container"

### Terminal Issues
1. **Restart Terminal**: Close and reopen the terminal
2. **Check Container**: Run `docker ps` to see if container is running
3. **Reconnect**: Use "Dev Containers: Reopen in Container"

### AI Features Not Working
1. **Check Context**: Ensure Cursor has access to the project files
2. **Restart Cursor**: Close and reopen Cursor
3. **Check Permissions**: Ensure files are readable

### Performance Issues
1. **Resource Limits**: Check Docker Desktop resource allocation
2. **Volume Mounts**: Large projects may be slower with volume mounts
3. **Extensions**: Disable unnecessary extensions

## Advanced Cursor Features

### Multi-Container Development
You can work with multiple containers simultaneously:

1. **Open multiple Cursor windows**
2. **Each window can connect to different containers**
3. **Share code between containers**

### Custom Extensions
Add custom extensions to the container:

1. **Edit `.devcontainer/devcontainer.json`**
2. **Add extensions to the `extensions` array**
3. **Rebuild the container**

### Environment Variables
Access container environment variables in Cursor:

```bash
# View all environment variables
env

# Access specific variables
echo $DATABASE_URL
echo $REDIS_URL
```

## Best Practices for Cursor + Dev Containers

### 1. Use Integrated Terminal
- Always use Cursor's integrated terminal when in a container
- Avoid external terminals for container commands

### 2. Leverage AI Features
- Use Cursor's AI to understand the containerized codebase
- Ask for help with container-specific issues

### 3. Use Debugging
- Set breakpoints in Cursor
- Debug directly in the container environment

### 4. Version Control
- All changes are automatically versioned
- Git operations work normally in the container

### 5. Package Management
- Install packages through the container terminal
- Update requirements files as needed

## Next Steps

Once you're comfortable with the dev container in Cursor:

1. **Explore the codebase** - Use Cursor's AI to understand the project
2. **Run tests** - Use the integrated terminal for testing
3. **Debug issues** - Use Cursor's debugging features
4. **Collaborate** - Share the dev container setup with your team
5. **Customize** - Modify the container configuration for your needs

The combination of Cursor's AI capabilities with the consistent dev container environment provides an excellent development experience! 