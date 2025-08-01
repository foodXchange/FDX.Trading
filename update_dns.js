#!/usr/bin/env node
/**
 * DNS Update Script for fdx.trading
 * Updates DNS records to point to Azure App Service
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// DNS records that need to be set
const REQUIRED_RECORDS = [
  {
    type: 'CNAME',
    name: 'www',
    value: 'foodxchange-deploy-app.azurewebsites.net',
    ttl: 1800
  },
  {
    type: 'TXT',
    name: 'asuid.www',
    value: '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77',
    ttl: 1800
  }
];

function loadConfig() {
  const configFile = path.join(os.homedir(), '.namecheap-cli', 'config.json');
  
  if (!fs.existsSync(configFile)) {
    console.error('❌ Config file not found. Please run: node namecheap-config.js first');
    process.exit(1);
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
    
    // Check if config has been updated
    if (config.apiUser === 'YOUR_NAMECHEAP_USERNAME' || 
        config.apiKey === 'YOUR_NAMECHEAP_API_KEY') {
      console.error('❌ Please update the config file with your Namecheap credentials:');
      console.error(`   ${configFile}`);
      process.exit(1);
    }
    
    return config;
  } catch (error) {
    console.error('❌ Error reading config file:', error.message);
    process.exit(1);
  }
}

async function updateDNSRecords() {
  console.log('🚀 Starting DNS update for fdx.trading...\n');
  
  const config = loadConfig();
  console.log(`📋 Using config for user: ${config.apiUser}`);
  console.log(`📍 From IP address: ${config.ipAddress}\n`);
  
  try {
    // Try to use namecheap-cli
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);
    
    console.log('🔧 Setting up DNS records...');
    
    for (const record of REQUIRED_RECORDS) {
      console.log(`\n📝 Setting ${record.type} record: ${record.name} -> ${record.value}`);
      
      try {
        let command;
        if (record.type === 'CNAME') {
          command = `npx namecheap-cli dns add-record fdx.trading CNAME ${record.name} ${record.value} ${record.ttl}`;
        } else if (record.type === 'TXT') {
          command = `npx namecheap-cli dns add-record fdx.trading TXT ${record.name} "${record.value}" ${record.ttl}`;
        }
        
        console.log(`   Running: ${command}`);
        const result = await execAsync(command);
        console.log(`   ✅ Success: ${record.name}`);
        
      } catch (error) {
        console.error(`   ❌ Failed to set ${record.name}: ${error.message}`);
        
        // Provide manual instructions
        console.log(`   📝 Manual setup for ${record.name}:`);
        console.log(`      Type: ${record.type}`);
        console.log(`      Name: ${record.name}`);
        console.log(`      Value: ${record.value}`);
        console.log(`      TTL: ${record.ttl}`);
      }
    }
    
    console.log('\n🎉 DNS update process completed!');
    console.log('\n⏳ DNS propagation may take 5-60 minutes.');
    console.log('💡 Monitor with: python check_dns.py monitor');
    
  } catch (error) {
    console.error('❌ Error during DNS update:', error.message);
    console.log('\n📝 Manual DNS Setup Required:');
    
    REQUIRED_RECORDS.forEach(record => {
      console.log(`\n${record.type} Record:`);
      console.log(`  Name: ${record.name}`);
      console.log(`  Value: ${record.value}`);
      console.log(`  TTL: ${record.ttl}`);
    });
  }
}

function showManualInstructions() {
  console.log('📋 Manual DNS Setup Instructions for fdx.trading\n');
  console.log('Login to your Namecheap account and add these records:\n');
  
  REQUIRED_RECORDS.forEach((record, index) => {
    console.log(`${index + 1}. ${record.type} Record:`);
    console.log(`   Type: ${record.type}`);
    console.log(`   Host: ${record.name}`);
    console.log(`   Value: ${record.value}`);
    console.log(`   TTL: ${record.ttl}`);
    console.log('');
  });
  
  console.log('After adding these records:');
  console.log('• Wait 5-60 minutes for DNS propagation');
  console.log('• Run: python check_dns.py monitor');
  console.log('• When both records show as correct, the domain will be ready!');
}

// Main execution
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--manual') || args.includes('-m')) {
    showManualInstructions();
  } else {
    updateDNSRecords().catch(error => {
      console.error('❌ Script failed:', error.message);
      console.log('\n📝 Falling back to manual instructions:');
      showManualInstructions();
    });
  }
}