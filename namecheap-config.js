// Namecheap CLI Configuration Setup
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration template
const configTemplate = {
  "apiUser": "YOUR_NAMECHEAP_USERNAME",
  "apiKey": "YOUR_NAMECHEAP_API_KEY", 
  "userName": "YOUR_NAMECHEAP_USERNAME",
  "ipAddress": "YOUR_PUBLIC_IP_ADDRESS"
};

async function getPublicIP() {
  try {
    const https = require('https');
    return new Promise((resolve, reject) => {
      https.get('https://api.ipify.org', (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => resolve(data));
      }).on('error', reject);
    });
  } catch (error) {
    console.log('Could not get public IP automatically');
    return 'YOUR_PUBLIC_IP_HERE';
  }
}

async function setupConfig() {
  console.log('🔧 Setting up Namecheap CLI Configuration\n');
  
  // Get public IP
  const publicIP = await getPublicIP();
  console.log(`📍 Your public IP: ${publicIP}\n`);
  
  // Update config with actual IP
  configTemplate.ipAddress = publicIP;
  
  // Create config directory
  const configDir = path.join(os.homedir(), '.namecheap-cli');
  const configFile = path.join(configDir, 'config.json');
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  // Write config file
  fs.writeFileSync(configFile, JSON.stringify(configTemplate, null, 2));
  
  console.log('📋 Configuration steps:');
  console.log('1. Get your Namecheap API credentials:');
  console.log('   - Login to Namecheap account');
  console.log('   - Go to Profile > Tools > Namecheap API access');
  console.log('   - Enable API access and get your API key');
  console.log('');
  console.log('2. Edit the config file:');
  console.log(`   ${configFile}`);
  console.log('');
  console.log('3. Replace the following values:');
  console.log('   - YOUR_NAMECHEAP_USERNAME: Your Namecheap username');
  console.log('   - YOUR_NAMECHEAP_API_KEY: Your API key from step 1');
  console.log('');
  console.log('4. Your public IP is already set to:', publicIP);
  console.log('');
  console.log('✅ Config file created at:', configFile);
  
  return configFile;
}

if (require.main === module) {
  setupConfig().catch(console.error);
}

module.exports = { setupConfig, configTemplate };