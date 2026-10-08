"""
Command Processing Module
Handles all voice commands and responses
"""

import datetime
import webbrowser
import wikipedia
import pyjokes
import pywhatkit as kit
import random
import requests
from typing import Dict, Callable, Optional

class CommandProcessor:
    """Process voice commands and generate responses"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        
        # Command registry
        self.commands: Dict[str, Callable] = {
            'time': self.get_time,
            'date': self.get_date,
            'weather': self.get_weather,
            'joke': self.tell_joke,
            'search': self.search_web,
            'open': self.open_website,
            'help': self.show_help,
            'stop': self.stop,
            'exit': self.exit_assistant,
            'clear': self.clear,
            'hello': self.say_hello,
            'how are you': self.how_are_you,
            'thank you': self.thank_you,
            'your name': self.get_name,
            'who are you': self.get_name,
        }
        
        # Response templates
        self.responses = {
            'error': "I'm sorry, I encountered an error processing your command.",
            'not_found': "I don't understand that command. Say 'help' to see available commands.",
            'welcome': "Hello! How can I help you today?",
            'goodbye': "Goodbye! It was nice helping you.",
        }
        
    def process_command(self, text: str) -> str:
        """
        Process a command and return response
        
        Args:
            text: Command text
            
        Returns:
            Response string
        """
        text = text.lower().strip()
        
        # Check for wake word
        if text.startswith(self.assistant.wake_word):
            text = text.replace(self.assistant.wake_word, '', 1).strip()
            if not text:
                return "Yes, I'm listening. What can I help you with?"
                
        # Check for command matches
        for command, handler in self.commands.items():
            if command in text:
                try:
                    return handler(text)
                except Exception as e:
                    print(f"Error executing command {command}: {e}")
                    return self.responses['error']
                    
        # Default response
        return self.responses['not_found']
        
    def get_time(self, text: str = "") -> str:
        """Get current time"""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
        
    def get_date(self, text: str = "") -> str:
        """Get current date"""
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
        
    def get_weather(self, text: str = "") -> str:
        """Get weather information"""
        # For demo, returns mock weather
        # In production, integrate with a weather API
        cities = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris']
        city = random.choice(cities)
        temp = random.randint(-5, 35)
        conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy']
        condition = random.choice(conditions)
        
        return f"The weather in {city} is {condition} with a temperature of {temp}°C"
        
    def tell_joke(self, text: str = "") -> str:
        """Tell a random joke"""
        try:
            # Try pyjokes first
            joke = pyjokes.get_joke(language='en', category='all')
            if joke:
                return joke
        except:
            pass
            
        # Fallback jokes
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fish wearing a bowtie? Sofishticated!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        return random.choice(jokes)
        
    def search_web(self, text: str = "") -> str:
        """Search the web"""
        # Extract search query
        query = text.replace('search', '', 1).strip()
        if not query:
            return "What would you like me to search for?"
            
        try:
            # Search using pywhatkit
            kit.search(query)
            return f"Searching for {query} in your browser"
        except Exception as e:
            print(f"Search error: {e}")
            return "I encountered an error performing the search"
            
    def open_website(self, text: str = "") -> str:
        """Open a website"""
        # Extract website name
        site = text.replace('open', '', 1).strip()
        if not site:
            return "What website would you like to open?"
            
        # Add https:// if not present
        if not site.startswith('http'):
            site = 'https://' + site
            
        try:
            webbrowser.open(site)
            return f"Opening {site} in your browser"
        except Exception as e:
            print(f"Open website error: {e}")
            return "I encountered an error opening the website"
            
    def show_help(self, text: str = "") -> str:
        """Show help information"""
        help_text = """
        Here are my available commands:
        
        • "time" or "what time" - Get the current time
        • "date" or "what date" - Get today's date
        • "weather" - Get weather information
        • "joke" or "tell joke" - Hear a funny joke
        • "search [query]" - Search the web
        • "open [website]" - Open a website
        • "hello" or "hi" - Say hello
        • "how are you" - Check how I'm doing
        • "your name" or "who are you" - Learn about me
        • "thank you" - You're welcome
        • "stop" - Stop listening
        • "exit" or "goodbye" - Exit the assistant
        • "clear" - Clear the chat
        • "help" - Show this help message
        
        You can also say "assistant" followed by a command.
        """
        return help_text.strip()
        
    def stop(self, text: str = "") -> str:
        """Stop listening"""
        self.assistant.stop_speaking()
        return "Stopped listening"
        
    def exit_assistant(self, text: str = "") -> str:
        """Exit the assistant"""
        return "Goodbye! Take care."
        
    def clear(self, text: str = "") -> str:
        """Clear chat"""
        return "Chat cleared"
        
    def say_hello(self, text: str = "") -> str:
        """Say hello"""
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! I'm ready to assist you.",
            "Good to see you! How can I help?"
        ]
        return random.choice(greetings)
        
    def how_are_you(self, text: str = "") -> str:
        """Respond to how are you"""
        responses = [
            "I'm doing great! Thanks for asking.",
            "I'm wonderful! How are you?",
            "I'm functioning perfectly! How can I assist you?",
            "I'm here and ready to help!"
        ]
        return random.choice(responses)
        
    def thank_you(self, text: str = "") -> str:
        """Respond to thank you"""
        responses = [
            "You're welcome! Is there anything else I can help with?",
            "My pleasure! Happy to help.",
            "Anytime! That's what I'm here for.",
            "You're welcome! Let me know if you need anything else."
        ]
        return random.choice(responses)
        
    def get_name(self, text: str = "") -> str:
        """Respond to name question"""
        return f"My name is {self.assistant.name}. I'm your AI voice assistant, designed to help you with various tasks."