#!/usr/bin/env python3
"""
CLI Chat with Gemini AI
A simple command-line interface to chat with Google's Gemini AI model.
"""

import json
import requests
import sys
from typing import Dict, Any

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyATAmr0h8d-HE-3-nji2cxUxHnpYjqol18"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

class GeminiChat:
    def __init__(self):
        self.conversation_history = []
        
    def send_message(self, message: str) -> str:
        """Send a message to Gemini and return the response."""
        try:
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": message
                            }
                        ]
                    }
                ]
            }
            
            # Add conversation history for context (optional)
            if self.conversation_history:
                payload["contents"] = self.conversation_history + payload["contents"]
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Make the API request
            response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                
                # Update conversation history
                self.conversation_history.extend([
                    {"parts": [{"text": message}]},
                    {"parts": [{"text": ai_response}]}
                ])
                
                return ai_response
            else:
                return "Sorry, I couldn't generate a response."
                
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Gemini API: {e}"
        except KeyError as e:
            return f"Error parsing response: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.")

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🤖 Gemini AI Chat - Command Line Interface")
    print("=" * 60)
    print("Type your message and press Enter to chat with Gemini.")
    print("Commands:")
    print("  /clear  - Clear conversation history")
    print("  /quit   - Exit the chat")
    print("  /help   - Show this help message")
    print("-" * 60)

def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print("  /clear  - Clear conversation history")
    print("  /quit   - Exit the chat")
    print("  /help   - Show this help message")
    print("\nJust type your message to chat with Gemini AI!")

def main():
    """Main chat loop."""
    chat = GeminiChat()
    print_banner()
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() == '/quit':
                print("\n👋 Goodbye! Thanks for chatting with Gemini AI.")
                break
            elif user_input.lower() == '/clear':
                chat.clear_history()
                continue
            elif user_input.lower() == '/help':
                print_help()
                continue
            elif user_input.startswith('/'):
                print("❌ Unknown command. Type /help for available commands.")
                continue
            
            # Send message to Gemini
            print("\n🤖 Gemini: ", end="", flush=True)
            response = chat.send_message(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()