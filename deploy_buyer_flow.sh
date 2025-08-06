#!/bin/bash
# Deploy ultra simple buyer flow to VM

echo "======================================"
echo "DEPLOYING BUYER FLOW TO VM"
echo "======================================"

# Copy file to VM
echo "1. Copying simple_buyer_flow.py to VM..."
scp simple_buyer_flow.py fdxadmin@74.248.141.31:/home/fdxadmin/

# Connect and run
echo "2. Starting on VM..."
ssh fdxadmin@74.248.141.31 << 'EOF'
cd /home/fdxadmin
pkill -f "uvicorn simple_buyer_flow"
nohup python3 -m uvicorn simple_buyer_flow:app --host 0.0.0.0 --port 8000 > buyer_flow.log 2>&1 &
echo "Started buyer flow on port 8000"
EOF

echo "======================================"
echo "BUYER FLOW DEPLOYED!"
echo "======================================"
echo ""
echo "Access at: http://74.248.141.31:8000"
echo ""
echo "Features:"
echo "✓ Google-style search box"
echo "✓ Text or image URL input"
echo "✓ AI matching for 25 suppliers"
echo "✓ Checkbox selection"
echo "✓ Full conversation tracking"
echo ""
echo "Next: Add seller flow after testing"