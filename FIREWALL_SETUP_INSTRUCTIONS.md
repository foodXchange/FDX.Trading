# Azure PostgreSQL Firewall Configuration

## Your Current IP Address: 85.65.236.169

## Quick Steps to Add Your IP to Azure PostgreSQL:

1. **Open Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Navigate to Your PostgreSQL Server**
   - Search for "foodxchangepgfr" in the search bar
   - Click on your PostgreSQL flexible server

3. **Add Firewall Rule**
   - In the left menu, click on "Networking"
   - Under "Firewall rules", click "+ Add current client IP address"
   - Or manually add:
     - Rule name: `ClientIP_85_65_236_169`
     - Start IP: `85.65.236.169`
     - End IP: `85.65.236.169`
   - Click "Save"

4. **Alternative: Add Allow All Rule (Less Secure)**
   - Rule name: `AllowAll`
   - Start IP: `0.0.0.0`
   - End IP: `255.255.255.255`
   - Click "Save"
   - **Note**: Only use this for testing, remove it later!

## After Adding the Firewall Rule:

1. Wait 1-2 minutes for the rule to take effect
2. Run `python auto_db_setup.py` to test the connection
3. Open pgAdmin and use these connection details:
   - Host: `foodxchangepgfr.postgres.database.azure.com`
   - Port: `5432`
   - Database: `foodxchange_db`
   - Username: `foodxchangedbadmin`
   - Password: `Ud30078123`

## If Connection Still Fails:

1. Check if your IP has changed (run `python check_my_ip.py` again)
2. Ensure the PostgreSQL server is running in Azure Portal
3. Verify the server name and credentials are correct
4. Check if SSL is required (it should be enabled by default)