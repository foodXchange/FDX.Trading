# Using Claude Code on Azure VM

## Option 1: Install Claude Code on VM (Recommended)

### Connect to VM
```bash
ssh -i <your-key> azureuser@4.206.1.15
```

### Install Claude Code
```bash
# Install Node.js first (required)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Claude Code
npm install -g @anthropic-ai/claude-cli

# Or using npx without install
npx @anthropic-ai/claude-cli
```

### Set up API key
```bash
export ANTHROPIC_API_KEY="your-api-key"
# Or add to ~/.bashrc for permanent setup
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc
```

### Use Claude Code on VM
```bash
# Start Claude Code
claude

# Now you can run all import commands directly on VM
# Claude will have access to the VM's file system and better database connectivity
```

## Option 2: VS Code Remote SSH (Visual)

1. Install VS Code on your Windows machine
2. Install "Remote - SSH" extension
3. Connect to VM:
   - Press F1 → "Remote-SSH: Connect to Host"
   - Enter: `azureuser@4.206.1.15`
   - Select your SSH key

4. Once connected, open terminal in VS Code
5. Install Claude Code extension or use terminal

## Option 3: Windows Terminal SSH + Claude

```bash
# In Windows Terminal/PowerShell
ssh -i <key> azureuser@4.206.1.15

# Keep this session open
# Open another terminal on your local machine
# Run Claude Code locally but execute commands via SSH
```

## Quick VM Setup for Import

Once connected to VM via any method:

```bash
# 1. Quick install everything needed
sudo apt update
sudo apt install -y python3-pip
pip3 install pandas psycopg2-binary openpyxl python-dotenv

# 2. Create working directory
mkdir ~/foodxchange
cd ~/foodxchange

# 3. Create .env file
nano .env
# Paste your DATABASE_URL and AZURE_OPENAI_KEY

# 4. Upload files (from your local machine)
scp -i <key> "C:/Users/foodz/Downloads/Suppliers 29_7_2025.xlsx" azureuser@4.206.1.15:~/foodxchange/
scp -i <key> simple_vm_import.py azureuser@4.206.1.15:~/foodxchange/

# 5. Run import
python3 simple_vm_import.py
```

## Benefits of Claude Code on VM:
- ✅ Direct access to VM file system
- ✅ Can run long imports without timeout
- ✅ Better database connectivity (same Azure network)
- ✅ Can monitor progress in real-time
- ✅ Background processes keep running

Would you like me to help you set up any of these options?