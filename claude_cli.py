#!/usr/bin/env python3
"""
Simple Claude CLI tool using anthropic library
"""

import os
import sys
from anthropic import Anthropic

def setup_api_key():
    """Setup Claude API key"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("🔑 Claude API Key not found in environment variables")
        api_key = input("Enter your Claude API key: ").strip()
        
        if not api_key:
            print("❌ API key is required")
            return None
        
        if not api_key.startswith("sk-"):
            print("❌ Invalid API key format. Should start with 'sk-'")
            return None
    
    return api_key

def chat_with_claude():
    """Interactive chat with Claude"""
    api_key = setup_api_key()
    if not api_key:
        return
    
    client = Anthropic(api_key=api_key)
    
    print("🤖 Claude CLI - Interactive Chat")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 50)
    
    messages = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Get Claude's response
            print("🤖 Claude: ", end="", flush=True)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=messages
            )
            
            claude_response = response.content[0].text
            print(claude_response)
            
            # Add Claude's response to conversation
            messages.append({"role": "assistant", "content": claude_response})
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def ask_claude(question):
    """Ask Claude a single question"""
    api_key = setup_api_key()
    if not api_key:
        return
    
    client = Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": question}]
        )
        
        print("🤖 Claude's response:")
        print(response.content[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])
        ask_claude(question)
    else:
        # Interactive mode
        chat_with_claude()

if __name__ == "__main__":
    main() 