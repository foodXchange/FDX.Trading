#!/bin/bash

# FDX VM Control Panel Deployment Script
# This script deploys the control panel on your VM

set -e

echo "==========================================="
echo "   FDX VM Control Panel Deployment"
echo "==========================================="

# Configuration
INSTALL_DIR="/home/fdxfounder/vm-control-panel"
SERVICE_NAME="vm-control-panel"
PORT=5555
USER="fdxfounder"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as correct user
if [ "$USER" != "$USER" ]; then
    print_error "Please run this script as user: $USER"
    exit 1
fi

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/templates
mkdir -p $INSTALL_DIR/static

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx supervisor

# Create Python virtual environment
print_status "Creating Python virtual environment..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
psutil==5.9.6
aiofiles==23.2.1
httpx==0.25.1
python-dotenv==1.0.0
azure-monitor-query==1.2.0
azure-identity==1.15.0
azure-storage-blob==12.19.0
azure-communication-email==1.0.0
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Copy application files
print_status "Copying application files..."
# Note: You'll need to upload these files to the VM
# For now, we'll create a placeholder

cat > $INSTALL_DIR/vm_control_fastapi.py << 'EOF'
# Placeholder - Upload the actual vm_control_fastapi.py file
print("Please upload the actual vm_control_fastapi.py file")
EOF

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=FDX VM Control Panel
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/uvicorn vm_control_fastapi:app --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/vm-control-panel > /dev/null << EOF
server {
    listen 5555;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $INSTALL_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/vm-control-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Create environment file
print_status "Creating environment configuration..."
cat > $INSTALL_DIR/.env << EOF
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=foodxchange-rg
AZURE_VM_NAME=fdx-vm
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection-string
AZURE_COMMUNICATION_CONNECTION_STRING=your-communication-connection-string
AZURE_LOG_WORKSPACE_ID=your-log-workspace-id

# VM Configuration
VM_IP=4.206.1.15
VM_USER=fdxfounder
EOF

# Set permissions
print_status "Setting permissions..."
chmod 600 $INSTALL_DIR/.env
chown -R $USER:$USER $INSTALL_DIR

# Create log directory
print_status "Creating log directory..."
sudo mkdir -p /var/log/vm-control-panel
sudo chown $USER:$USER /var/log/vm-control-panel

# Enable and start service
print_status "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Check service status
sleep 3
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "Service started successfully!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 5555/tcp comment 'VM Control Panel'

# Create update script
print_status "Creating update script..."
cat > $INSTALL_DIR/update.sh << 'EOF'
#!/bin/bash
cd $(dirname $0)
source venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart vm-control-panel
echo "Update complete!"
EOF
chmod +x $INSTALL_DIR/update.sh

# Final instructions
echo ""
echo "==========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "==========================================="
echo ""
echo "VM Control Panel is now running on:"
echo "  - Local: http://localhost:$PORT"
echo "  - External: http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo "Next steps:"
echo "1. Upload vm_control_fastapi.py to $INSTALL_DIR/"
echo "2. Upload templates/dashboard_fastapi.html to $INSTALL_DIR/templates/"
echo "3. Configure Azure credentials in $INSTALL_DIR/.env"
echo "4. Restart service: sudo systemctl restart $SERVICE_NAME"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Check status: sudo systemctl status $SERVICE_NAME"
echo "  - Restart: sudo systemctl restart $SERVICE_NAME"
echo "  - Update: cd $INSTALL_DIR && ./update.sh"
echo ""
echo "==========================================="

# Create quick access script
cat > ~/vm-control.sh << EOF
#!/bin/bash
echo "VM Control Panel Commands:"
echo "  status  - Check service status"
echo "  logs    - View logs"
echo "  restart - Restart service"
echo "  update  - Update application"
echo ""
case \$1 in
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        ;;
    update)
        cd $INSTALL_DIR && ./update.sh
        ;;
    *)
        echo "Opening VM Control Panel..."
        xdg-open "http://localhost:$PORT" 2>/dev/null || echo "Visit http://localhost:$PORT"
        ;;
esac
EOF
chmod +x ~/vm-control.sh

print_status "Quick access script created at ~/vm-control.sh"