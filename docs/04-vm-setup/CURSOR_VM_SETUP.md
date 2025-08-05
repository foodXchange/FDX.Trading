# Installing Cursor with Claude on Azure VM

## Method 1: Cursor via Remote SSH (Recommended)

### On Your Windows Machine:
1. **Download Cursor** from https://cursor.sh
2. Install Cursor on Windows
3. Open Cursor
4. Install "Remote - SSH" extension (same as VS Code)
5. Connect to VM:
   - Press `Ctrl+Shift+P`
   - Type "Remote-SSH: Connect to Host"
   - Enter: `azureuser@4.206.1.15`

### Now Cursor runs locally but edits/executes on VM!
- Terminal is on VM
- Files are on VM
- Claude/GPT-4 works normally
- Database connections are faster

## Method 2: Install Cursor Directly on VM (X11 Forwarding)

### Enable X11 Forwarding:
```bash
# On Windows, install VcXsrv or Xming first
# Then connect with X11 forwarding
ssh -X -i <your-key> azureuser@4.206.1.15
```

### Install Cursor on VM:
```bash
# Download Cursor AppImage
wget https://downloader.cursor.sh/linux/appImage/x64 -O cursor.AppImage
chmod +x cursor.AppImage

# Install dependencies
sudo apt update
sudo apt install -y libfuse2 xvfb

# Run Cursor (will forward GUI to your Windows X server)
./cursor.AppImage
```

## Method 3: Terminal-Only Cursor Features

### Use Cursor's AI in regular terminal:
```bash
# Connect to VM
ssh -i <your-key> azureuser@4.206.1.15

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install AI coding assistants
npm install -g aider-chat  # AI pair programmer
npm install -g @anthropic-ai/claude-cli  # Claude in terminal

# Set up API keys
export ANTHROPIC_API_KEY="your-claude-key"
export OPENAI_API_KEY="your-openai-key"  # if using GPT-4
```

## Quick VM Import Setup

Once connected (any method):

```bash
# 1. Create project directory
mkdir ~/foodxchange && cd ~/foodxchange

# 2. Install Python packages
pip3 install pandas psycopg2-binary openpyxl python-dotenv openai

# 3. Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
EOF

# 4. Upload Excel file (from your local machine)
# In another terminal:
scp -i <key> "C:/Users/foodz/Downloads/Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/foodxchange/

# 5. Create import script
wget https://raw.githubusercontent.com/your-repo/simple_vm_import.py
# Or create it in Cursor

# 6. Run import with screen (keeps running if disconnected)
screen -S import
python3 simple_vm_import.py
# Press Ctrl+A then D to detach
```

## Recommended: Cursor Remote SSH

This is the best approach because:
- ✅ Full Cursor IDE experience
- ✅ Claude/GPT-4 chat built-in
- ✅ Terminal runs on VM (fast database access)
- ✅ No X11 forwarding needed
- ✅ Works exactly like local development

Would you like help setting up Cursor Remote SSH?