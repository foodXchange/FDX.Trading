# Run Claude CLI Import on VM

## 1. Connect to VM
```bash
ssh azureuser@74.248.141.31
# Password: [Your VM Password]
```

## 2. Quick Setup (Copy & Paste)
```bash
# Install everything needed
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs python3-pip
npm install -g @anthropic-ai/claude-cli

# Python packages
pip3 install pandas psycopg2-binary openpyxl python-dotenv openai==0.28

# Create workspace
mkdir -p ~/foodxchange && cd ~/foodxchange

# Create .env with all credentials
cat > .env << 'EOF'
DATABASE_URL=postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require
AZURE_OPENAI_KEY=4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz
AZURE_OPENAI_ENDPOINT=https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
EOF
```

## 3. Upload Files (from your PC)
```bash
# In a new terminal on your PC:
scp "C:\Users\foodz\Downloads\Suppliers 29_7_2025.xlsx" azureuser@74.248.141.31:~/foodxchange/
scp ai_enhanced_import.py azureuser@74.248.141.31:~/foodxchange/
```

## 4. Run AI-Enhanced Import
```bash
# Back on VM
cd ~/foodxchange
python3 ai_enhanced_import.py
```

## OR Use Claude CLI Directly

```bash
# Set Claude API key (if you have one)
export ANTHROPIC_API_KEY="your-claude-api-key"

# Run Claude
claude

# In Claude, you can ask:
# "Help me import Suppliers 29_7_2025.xlsx to PostgreSQL with AI enhancement"
# Claude will guide you through the process interactively
```

## What This Does:

1. **Imports all 23,206 suppliers**
2. **AI-enhances each supplier** with:
   - Detailed product catalogs
   - Specific product names and sizes
   - Certifications and capabilities
   - Target markets and MOQs
3. **No timeouts** - runs on Azure network
4. **Progress tracking** - see real-time updates

## Expected Timeline:
- Setup: 5 minutes
- File upload: 2 minutes
- Import with AI: 1-2 hours
- Result: Complete commerce super-brain database!

## Monitor Progress:
```bash
# Check log
tail -f ai_import.log

# Check database count
python3 -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM suppliers')
print(f'Suppliers: {cur.fetchone()[0]:,}')
"
```

## Performance Benefits

### Poland Central Location
- **Latency from Israel**: ~30ms (6x faster than US East)
- **Network**: Optimized for European traffic
- **Cost**: $57/month (saving $3/month)

### Database Connection
- **Server**: fdx-poland-db.postgres.database.azure.com
- **Database**: foodxchange
- **Location**: Poland Central
- **Performance**: Optimized for read-heavy workloads