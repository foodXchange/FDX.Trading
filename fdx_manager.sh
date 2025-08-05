#!/bin/bash

# FoodXchange Manager - One-command control center
# Run from your local machine for quick management

# Configuration
SSH_KEY="~/.ssh/fdx_founders_key"
VM_USER="fdxfounder"
VM_IP="4.206.1.15"
RESOURCE_GROUP="foodxchange-founders-rg"
VM_NAME="fdx-founders-vm"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Helper function for SSH commands
run_ssh() {
    ssh -i $SSH_KEY $VM_USER@$VM_IP "$1"
}

# Main menu
show_menu() {
    clear
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   FoodXchange Manager v1.0${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "1)  📊 Check System Status"
    echo "2)  🖥️  Connect to Claude Session"
    echo "3)  📋 View Application Logs"
    echo "4)  🔄 Restart Application"
    echo "5)  💾 Run Manual Backup"
    echo "6)  📈 View Real-time Metrics"
    echo "7)  💰 Check Azure Costs"
    echo "8)  🛑 Stop VM (Save Money)"
    echo "9)  ▶️  Start VM"
    echo "10) 📧 Test Email Service"
    echo "11) 🏥 Run Health Check"
    echo "12) 📱 Show Mobile Commands"
    echo "0)  ❌ Exit"
    echo ""
    echo -e "${YELLOW}Choose an option:${NC} "
}

# Function implementations
check_status() {
    echo -e "${GREEN}Checking system status...${NC}"
    
    # Check if VM is running
    echo -e "\n${BLUE}VM Status:${NC}"
    az vm get-instance-view \
        --resource-group $RESOURCE_GROUP \
        --name $VM_NAME \
        --query instanceView.statuses[1] \
        --output table
    
    # Check app health
    echo -e "\n${BLUE}App Health:${NC}"
    if curl -s http://$VM_IP:8000/health > /dev/null; then
        echo -e "${GREEN}✅ App is running${NC}"
    else
        echo -e "${RED}❌ App is down${NC}"
    fi
    
    # Check system resources
    echo -e "\n${BLUE}System Resources:${NC}"
    run_ssh "df -h / | grep -v Filesystem && echo '' && free -h | grep -E 'Mem:|Swap:'"
    
    echo -e "\n${BLUE}Running Sessions:${NC}"
    run_ssh "tmux ls 2>/dev/null || echo 'No tmux sessions running'"
}

connect_claude() {
    echo -e "${GREEN}Connecting to Claude session...${NC}"
    echo -e "${YELLOW}Remember: Ctrl+B then D to detach${NC}"
    sleep 2
    ssh -i $SSH_KEY -t $VM_USER@$VM_IP "tmux attach -t fdx-claude || (~/fdx/scripts/claude_session_manager.sh start && tmux attach -t fdx-claude)"
}

view_logs() {
    echo -e "${GREEN}Viewing application logs...${NC}"
    run_ssh "tail -f ~/fdx/logs/app.log"
}

restart_app() {
    echo -e "${YELLOW}Restarting application...${NC}"
    run_ssh "sudo systemctl restart fdx-app || (cd ~/fdx/app && source venv/bin/activate && pkill -f uvicorn && nohup uvicorn app:app --host 0.0.0.0 --port 8000 &)"
    sleep 5
    
    if curl -s http://$VM_IP:8000/health > /dev/null; then
        echo -e "${GREEN}✅ App restarted successfully${NC}"
    else
        echo -e "${RED}❌ App failed to restart${NC}"
    fi
}

run_backup() {
    echo -e "${GREEN}Running manual backup...${NC}"
    run_ssh "~/fdx/scripts/backup_system.sh"
}

view_metrics() {
    echo -e "${GREEN}Opening real-time metrics...${NC}"
    echo -e "${BLUE}Grafana:${NC} http://$VM_IP:3000 (admin/admin)"
    echo -e "${BLUE}Netdata:${NC} http://$VM_IP:19999"
    echo ""
    echo "Press Enter to open in browser..."
    read
    
    # Try to open in default browser
    if command -v xdg-open > /dev/null; then
        xdg-open "http://$VM_IP:3000" &
        xdg-open "http://$VM_IP:19999" &
    elif command -v open > /dev/null; then
        open "http://$VM_IP:3000" &
        open "http://$VM_IP:19999" &
    else
        echo "Please open the URLs manually in your browser"
    fi
}

check_costs() {
    echo -e "${GREEN}Checking Azure costs...${NC}"
    ./monitor_costs_automated.sh
}

stop_vm() {
    echo -e "${YELLOW}Stopping VM to save costs...${NC}"
    echo -e "${RED}Warning: This will make your app inaccessible!${NC}"
    echo -n "Are you sure? (y/n): "
    read confirm
    
    if [ "$confirm" = "y" ]; then
        az vm deallocate --resource-group $RESOURCE_GROUP --name $VM_NAME
        echo -e "${GREEN}✅ VM stopped. You're now saving ~$4/day${NC}"
    else
        echo "Cancelled"
    fi
}

start_vm() {
    echo -e "${GREEN}Starting VM...${NC}"
    az vm start --resource-group $RESOURCE_GROUP --name $VM_NAME
    
    # Wait for VM to be ready
    echo "Waiting for VM to be ready..."
    sleep 30
    
    # Get new IP (might change)
    NEW_IP=$(az vm show \
        --resource-group $RESOURCE_GROUP \
        --name $VM_NAME \
        --show-details \
        --query publicIps \
        --output tsv)
    
    if [ "$NEW_IP" != "$VM_IP" ]; then
        echo -e "${YELLOW}Note: VM IP changed to $NEW_IP${NC}"
        echo "Update your scripts with the new IP"
    fi
    
    echo -e "${GREEN}✅ VM started${NC}"
}

test_email() {
    echo -e "${GREEN}Testing email service...${NC}"
    run_ssh "cd ~/fdx/app && source venv/bin/activate && python setup_sendgrid.py"
}

health_check() {
    echo -e "${GREEN}Running comprehensive health check...${NC}"
    run_ssh "cd ~/fdx/app && source venv/bin/activate && python automated_health_check.py"
}

show_mobile() {
    echo -e "${BLUE}📱 Mobile Quick Commands${NC}"
    echo ""
    echo "From Termius or any SSH app:"
    echo ""
    echo -e "${GREEN}Quick Status:${NC}"
    echo "ssh -i key fdxfounder@$VM_IP 'fdx-status'"
    echo ""
    echo -e "${GREEN}Attach to Claude:${NC}"
    echo "ssh -i key fdxfounder@$VM_IP -t 'tmux attach -t fdx-claude'"
    echo ""
    echo -e "${GREEN}View Logs:${NC}"
    echo "ssh -i key fdxfounder@$VM_IP 'tail -20 ~/fdx/logs/app.log'"
    echo ""
    echo -e "${YELLOW}Pro tip: Save these as Termius snippets!${NC}"
}

# Main loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) check_status ;;
        2) connect_claude ;;
        3) view_logs ;;
        4) restart_app ;;
        5) run_backup ;;
        6) view_metrics ;;
        7) check_costs ;;
        8) stop_vm ;;
        9) start_vm ;;
        10) test_email ;;
        11) health_check ;;
        12) show_mobile ;;
        0) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
done