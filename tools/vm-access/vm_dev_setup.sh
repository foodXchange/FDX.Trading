#!/bin/bash
# FDX VM Development Environment Setup
# Run this on your VM to set up a complete development environment

echo "🚀 Setting up FDX Development Environment on VM..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install development tools
echo "🛠️ Installing development tools..."
sudo apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    htop \
    tmux \
    vim \
    nano \
    tree \
    ncdu \
    jq \
    ripgrep \
    fd-find

# Install Python development tools
echo "🐍 Installing Python development tools..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    ipython3

# Install Node.js for any frontend work
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Set up development directory structure
echo "📁 Setting up directory structure..."
cd ~
mkdir -p foodxchange/{dev,prod,logs,backups,scripts}

# Create development environment
echo "🔧 Creating development virtual environment..."
cd ~/foodxchange/dev
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Copy production files to dev (if they exist)
if [ -d ~/foodxchange/prod ]; then
    echo "📋 Copying production files to dev environment..."
    cp -r ~/foodxchange/prod/* ~/foodxchange/dev/ 2>/dev/null || true
fi

# Install VS Code Server (for web-based IDE)
echo "💻 Installing code-server for web IDE..."
curl -fsSL https://code-server.dev/install.sh | sh
sudo systemctl enable --now code-server@$USER

# Configure code-server
mkdir -p ~/.config/code-server
cat > ~/.config/code-server/config.yaml << EOF
bind-addr: 0.0.0.0:8080
auth: password
password: fdx2030dev
cert: false
EOF

sudo systemctl restart code-server@$USER

# Set up tmux configuration
echo "⚡ Configuring tmux..."
cat > ~/.tmux.conf << 'EOF'
# Enable mouse support
set -g mouse on

# Set prefix to Ctrl+A
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# Split panes with | and -
bind | split-window -h
bind - split-window -v

# Reload config with r
bind r source-file ~/.tmux.conf \; display "Config reloaded!"

# Status bar
set -g status-bg colour235
set -g status-fg white
set -g status-left '#[fg=green][#S] '
set -g status-right '#[fg=yellow]#(hostname) #[fg=white]%H:%M'

# Window status
setw -g window-status-format " #I: #W "
setw -g window-status-current-format " #I: #W "
setw -g window-status-current-style bg=colour239,fg=white

# Pane borders
set -g pane-border-style fg=colour238
set -g pane-active-border-style fg=colour51

# History
set -g history-limit 10000
EOF

# Create helpful aliases
echo "🔗 Setting up aliases..."
cat >> ~/.bashrc << 'EOF'

# FDX Development Aliases
alias fdx='cd ~/foodxchange'
alias fdxdev='cd ~/foodxchange/dev && source venv/bin/activate'
alias fdxprod='cd ~/foodxchange/prod'
alias fdxlogs='tail -f ~/foodxchange/logs/*.log'
alias fdxstart='cd ~/foodxchange/dev && source venv/bin/activate && python app.py'
alias fdxtest='cd ~/foodxchange/dev && source venv/bin/activate && python -m pytest'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline -10'

# System monitoring
alias ports='sudo netstat -tlnp'
alias mem='free -h'
alias disk='df -h'

# Tmux session for development
alias devtmux='tmux new-session -s fdxdev -c ~/foodxchange/dev || tmux attach -t fdxdev'
EOF

# Create development session script
cat > ~/foodxchange/scripts/start_dev.sh << 'EOF'
#!/bin/bash
# Start FDX development environment

# Create tmux session with multiple panes
tmux new-session -d -s fdxdev -c ~/foodxchange/dev

# Window 1: Main editor
tmux rename-window -t fdxdev:0 'Editor'
tmux send-keys -t fdxdev:0 'source venv/bin/activate' C-m
tmux send-keys -t fdxdev:0 'clear' C-m

# Window 2: Server
tmux new-window -t fdxdev:1 -n 'Server' -c ~/foodxchange/dev
tmux send-keys -t fdxdev:1 'source venv/bin/activate' C-m
tmux send-keys -t fdxdev:1 'python app.py' C-m

# Window 3: Database/Testing
tmux new-window -t fdxdev:2 -n 'Database' -c ~/foodxchange/dev
tmux send-keys -t fdxdev:2 'source venv/bin/activate' C-m
tmux send-keys -t fdxdev:2 'ipython3' C-m

# Window 4: Logs
tmux new-window -t fdxdev:3 -n 'Logs' -c ~/foodxchange
tmux send-keys -t fdxdev:3 'tail -f logs/*.log' C-m

# Attach to session
tmux attach-session -t fdxdev
EOF

chmod +x ~/foodxchange/scripts/start_dev.sh

# Create a development configuration file
cat > ~/foodxchange/dev/.env.development << 'EOF'
# Development Environment Configuration
DEBUG=True
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Use same database as production (be careful!)
# Or set up a separate dev database
DATABASE_URL=postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require

# Development server
HOST=0.0.0.0
PORT=5000
EOF

# Install development dependencies
echo "📚 Installing development Python packages..."
cd ~/foodxchange/dev
source venv/bin/activate
pip install \
    flask \
    fastapi \
    uvicorn \
    psycopg2-binary \
    python-dotenv \
    requests \
    pandas \
    ipython \
    ipdb \
    pytest \
    black \
    flake8 \
    pre-commit

# Set up git (if not already configured)
if ! git config user.name > /dev/null 2>&1; then
    echo "⚙️ Configuring git..."
    git config --global user.name "FDX Developer"
    git config --global user.email "dev@fdx.trading"
fi

# Final instructions
echo "
✅ Development environment setup complete!

📍 Key Locations:
   - Development: ~/foodxchange/dev
   - Production: ~/foodxchange/prod
   - Logs: ~/foodxchange/logs
   - Scripts: ~/foodxchange/scripts

🚀 Quick Start Commands:
   - Start dev environment: devtmux (or ~/foodxchange/scripts/start_dev.sh)
   - Go to dev folder: fdxdev
   - Start dev server: fdxstart
   - View logs: fdxlogs

💻 VS Code Web Access:
   - URL: http://$(hostname -I | awk '{print $1}'):8080
   - Password: fdx2030dev

🔧 Tmux Commands:
   - Create new session: tmux new -s session-name
   - List sessions: tmux ls
   - Attach to session: tmux attach -t session-name
   - Detach: Ctrl+A, then D
   - Split horizontal: Ctrl+A, then |
   - Split vertical: Ctrl+A, then -
   - Switch panes: Ctrl+A, then arrow keys

📝 Next Steps:
   1. Source your bashrc: source ~/.bashrc
   2. Start development session: devtmux
   3. Access VS Code: http://VM-IP:8080
"