#!/bin/bash

# Setup script for Poland VM
echo "Setting up FDX application on Poland VM..."

# Install Python packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Create application directory
mkdir -p /home/fdxadmin/fdx
cd /home/fdxadmin/fdx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn psycopg2-binary python-dotenv jinja2 python-multipart

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require
USER_EMAIL=udi@fdx.trading
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
EOF

# Setup Nginx
sudo tee /etc/nginx/sites-available/fdx << 'EOF'
server {
    listen 80;
    server_name 74.248.141.31;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/fdx /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Create systemd service
sudo tee /etc/systemd/system/fdx.service << 'EOF'
[Unit]
Description=FDX Trading Application
After=network.target

[Service]
User=fdxadmin
WorkingDirectory=/home/fdxadmin/fdx
Environment="PATH=/home/fdxadmin/fdx/venv/bin"
ExecStart=/home/fdxadmin/fdx/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fdx
sudo systemctl start fdx

echo "Setup complete! Application should be running on http://74.248.141.31"