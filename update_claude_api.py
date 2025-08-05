#!/usr/bin/env python3
"""
Script to update Claude API key in Cursor settings
"""

import json
import os
import sys
from pathlib import Path

def get_cursor_settings_path():
    """Get the path to Cursor settings.json file"""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
    else:
        return Path.home() / ".config" / "Cursor" / "User" / "settings.json"

def update_claude_api_key(api_key):
    """Update Claude API key in Cursor settings"""
    settings_path = get_cursor_settings_path()
    
    # Check if settings file exists
    if not settings_path.exists():
        print(f"❌ Cursor settings file not found at: {settings_path}")
        return False
    
    try:
        # Read current settings
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Create backup
        backup_path = settings_path.with_suffix('.json.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Backup created at: {backup_path}")
        
        # Update Claude settings
        claude_settings = {
            "claude.apiKey": api_key,
            "claude.enabled": True,
            "claude.model": "claude-3-5-sonnet-20241022",
            "claude.maxTokens": 4096,
            "claude.temperature": 0.7
        }
        
        # Update settings
        settings.update(claude_settings)
        
        # Write updated settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        
        print("✅ Claude API key updated successfully!")
        print(f"📁 Settings file: {settings_path}")
        print("🔄 Please restart Cursor for changes to take effect")
        return True
        
    except Exception as e:
        print(f"❌ Error updating settings: {e}")
        return False

def main():
    print("🚀 Claude API Key Updater for Cursor")
    print("=" * 40)
    
    # Get API key from user
    api_key = input("Enter your Claude API key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty")
        return
    
    if not api_key.startswith("sk-"):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return
    
    # Update the settings
    if update_claude_api_key(api_key):
        print("\n🎉 Setup complete! Restart Cursor to use Claude.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 