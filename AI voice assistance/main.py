"""
AI Voice Assistant for People with Disabilities
Main entry point for the application
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from tkinter import messagebox

# Import custom modules
from assistant import VoiceAssistant
from accessibility import AccessibilityManager
from commands import CommandProcessor

class VoiceAssistantGUI:
    """Main GUI application for the voice assistant"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Voice Assistant - Accessibility Edition")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize components
        self.accessibility = AccessibilityManager(self.config.get('accessibility', {}))
        self.assistant = VoiceAssistant(self.config.get('assistant', {}))
        self.command_processor = CommandProcessor(self.assistant)
        
        # Set up the GUI
        self.setup_ui()
        self.apply_accessibility_settings()
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Status variables
        self.is_listening = False
        self.listening_thread = None
        
        # Display welcome message
        self.add_to_chat("System", "🤖 AI Voice Assistant initialized successfully!")
        self.add_to_chat("System", "🎤 Click 'Start Listening' or press Ctrl+Space to begin.")
        self.add_to_chat("System", "📢 Say 'help' to see available commands.")
        
        # Start assistant in background
        self.assistant.speak("Hello! I'm your AI voice assistant. Click the start button or say 'start listening' to begin.")
        
    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "assistant": {
                    "name": "AI Voice Assistant",
                    "wake_word": "assistant",
                    "language": "en-US",
                    "voice_gender": "female",
                    "speech_rate": 180,
                    "volume": 1.0
                },
                "accessibility": {
                    "high_contrast": False,
                    "font_size": 12,
                    "text_to_speech_enabled": True,
                    "voice_feedback_enabled": True,
                    "screen_reader_compatible": True
                },
                "commands": {
                    "time": "time",
                    "date": "date",
                    "weather": "weather",
                    "joke": "joke",
                    "search": "search",
                    "open": "open",
                    "help": "help",
                    "stop": "stop",
                    "exit": "exit"
                }
            }
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
            
    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.setup_header()
        
        # Chat display
        self.setup_chat_display()
        
        # Status bar
        self.setup_status_bar()
        
        # Control buttons
        self.setup_controls()
        
        # Quick commands
        self.setup_quick_commands()
        
        # Accessibility controls
        self.setup_accessibility_controls()
        
    def setup_header(self):
        """Set up the header section"""
        header_frame = tk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🤖 AI Voice Assistant",
            font=("Arial", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_indicator = tk.Label(
            header_frame,
            text="● Ready",
            font=("Arial", 12),
            fg="green"
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Time display
        self.time_label = tk.Label(
            header_frame,
            font=("Arial", 12),
            fg="gray"
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.update_time()
        
    def setup_chat_display(self):
        """Set up the chat display area"""
        chat_frame = tk.Frame(self.main_container)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat text area
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=15,
            bg="#f5f5f5",
            fg="#333333"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
    def setup_status_bar(self):
        """Set up the status bar"""
        status_frame = tk.Frame(self.main_container)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status text
        self.status_text = tk.Label(
            status_frame,
            text="Ready to help",
            font=("Arial", 10),
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5
        )
        self.status_text.pack(fill=tk.X)
        
    def setup_controls(self):
        """Set up control buttons"""
        control_frame = tk.Frame(self.main_container)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start button
        self.start_btn = tk.Button(
            control_frame,
            text="🎤 Start Listening",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            command=self.toggle_listening
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️ Stop",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10,
            command=self.stop_listening,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear chat button
        clear_btn = tk.Button(
            control_frame,
            text="🗑️ Clear Chat",
            font=("Arial", 10),
            bg="#ff9800",
            fg="white",
            padx=15,
            pady=10,
            command=self.clear_chat
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_btn = tk.Button(
            control_frame,
            text="❓ Help",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=10,
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_quick_commands(self):
        """Set up quick command buttons"""
        quick_frame = tk.LabelFrame(self.main_container, text="Quick Commands", font=("Arial", 10, "bold"))
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        commands = [
            ("⏰ Time", "time"),
            ("📅 Date", "date"),
            ("🌤️ Weather", "weather"),
            ("😂 Joke", "joke"),
            ("🔍 Search", "search"),
            ("🌐 Open Web", "open"),
            ("❓ Help", "help"),
            ("🗑️ Clear", "clear")
        ]
        
        # Create buttons in a grid
        for i, (label, command) in enumerate(commands):
            row = i // 4
            col = i % 4
            btn = tk.Button(
                quick_frame,
                text=label,
                font=("Arial", 10),
                padx=10,
                pady=5,
                command=lambda cmd=command: self.execute_quick_command(cmd)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
        # Make grid columns expand equally
        for col in range(4):
            quick_frame.grid_columnconfigure(col, weight=1)
            
    def setup_accessibility_controls(self):
        """Set up accessibility controls"""
        access_frame = tk.LabelFrame(self.main_container, text="Accessibility Controls", font=("Arial", 10, "bold"))
        access_frame.pack(fill=tk.X)
        
        # Font size controls
        font_frame = tk.Frame(access_frame)
        font_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
        
        self.font_size_var = tk.IntVar(value=self.config['accessibility']['font_size'])
        font_spinbox = tk.Spinbox(
            font_frame,
            from_=8,
            to=30,
            width=5,
            textvariable=self.font_size_var,
            command=self.update_font_size
        )
        font_spinbox.pack(side=tk.LEFT, padx=5)
        
        # High contrast toggle
        self.high_contrast_var = tk.BooleanVar(value=self.config['accessibility']['high_contrast'])
        high_contrast_check = tk.Checkbutton(
            access_frame,
            text="👁️ High Contrast",
            variable=self.high_contrast_var,
            command=self.toggle_high_contrast
        )
        high_contrast_check.pack(side=tk.LEFT, padx=10)
        
        # TTS toggle
        self.tts_var = tk.BooleanVar(value=self.config['accessibility']['text_to_speech_enabled'])
        tts_check = tk.Checkbutton(
            access_frame,
            text="🔊 Text-to-Speech",
            variable=self.tts_var,
            command=self.toggle_tts
        )
        tts_check.pack(side=tk.LEFT, padx=10)
        
        # Read aloud button
        read_btn = tk.Button(
            access_frame,
            text="📢 Read Aloud",
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            padx=10,
            pady=5,
            command=self.read_aloud
        )
        read_btn.pack(side=tk.LEFT, padx=10)
        
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<Control-space>', lambda e: self.toggle_listening())
        self.root.bind('<Escape>', lambda e: self.stop_listening())
        self.root.bind('<Control-h>', lambda e: self.show_help())
        self.root.bind('<Control-c>', lambda e: self.clear_chat())
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def toggle_listening(self):
        """Toggle listening state"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Start listening for voice commands"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.start_btn.config(text="⏹️ Stop Listening", bg="#f44336")
        self.stop_btn.config(state=tk.NORMAL)
        self.status_indicator.config(text="● Listening", fg="red")
        self.status_text.config(text="🎤 Listening... Speak now")
        
        self.add_to_chat("System", "🎤 Started listening...")
        
        # Start listening in a separate thread
        self.listening_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listening_thread.start()
        
    def listen_loop(self):
        """Loop for continuous listening"""
        while self.is_listening:
            try:
                # Listen for voice input
                command = self.assistant.listen()
                
                if command:
                    # Update GUI in main thread
                    self.root.after(0, lambda: self.process_voice_command(command))
                    
            except Exception as e:
                print(f"Listening error: {e}")
                self.root.after(0, lambda: self.add_to_chat("System", f"⚠️ Error: {str(e)}"))
                
            # Small delay to prevent CPU overuse
            time.sleep(0.1)
            
    def process_voice_command(self, command):
        """Process a voice command"""
        # Display in chat
        self.add_to_chat("You", f"🎤 {command}")
        
        # Process command
        try:
            response = self.command_processor.process_command(command)
            
            # Display response
            self.add_to_chat("Assistant", f"🤖 {response}")
            
            # Speak response if enabled
            if self.tts_var.get():
                self.assistant.speak(response)
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            self.add_to_chat("System", f"⚠️ {error_msg}")
            self.assistant.speak("Sorry, I encountered an error processing your command.")
            
    def execute_quick_command(self, command):
        """Execute a quick command from buttons"""
        if command == "clear":
            self.clear_chat()
            return
            
        self.add_to_chat("You", f"📌 {command}")
        
        try:
            response = self.command_processor.process_command(command)
            self.add_to_chat("Assistant", f"🤖 {response}")
            
            if self.tts_var.get():
                self.assistant.speak(response)
                
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self.add_to_chat("System", f"⚠️ {error_msg}")
            
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.start_btn.config(text="🎤 Start Listening", bg="#4CAF50")
        self.stop_btn.config(state=tk.DISABLED)
        self.status_indicator.config(text="● Ready", fg="green")
        self.status_text.config(text="Ready to help")
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=1)
            
        self.add_to_chat("System", "⏹️ Stopped listening")
        
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.add_to_chat("System", "🗑️ Chat cleared")
        
    def add_to_chat(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        
        # Format message
        if sender == "System":
            self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n", "system")
        elif sender == "You":
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n", "user")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n", "assistant")
            
        # Configure tags for colors
        self.chat_display.tag_config("system", foreground="gray")
        self.chat_display.tag_config("user", foreground="blue")
        self.chat_display.tag_config("assistant", foreground="green")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def show_help(self):
        """Show help information"""
        help_text = """
        🤖 AI Voice Assistant - Help
        
        Voice Commands:
        • "time" or "what time" - Get current time
        • "date" or "what date" - Get today's date
        • "weather" - Get weather information
        • "joke" or "tell joke" - Hear a funny joke
        • "search [query]" - Search the web
        • "open [website]" - Open a website
        • "help" - Show this help
        • "stop" - Stop listening
        • "exit" or "goodbye" - Exit the assistant
        
        Quick Commands:
        Use the buttons above for instant access
        
        Keyboard Shortcuts:
        • Ctrl+Space - Toggle listening
        • Escape - Stop listening
        • Ctrl+H - Show help
        • Ctrl+C - Clear chat
        
        Accessibility Features:
        • Font size adjustment
        • High contrast mode
        • Text-to-speech
        • Read aloud button
        """
        
        messagebox.showinfo("Help - Voice Assistant", help_text)
        self.add_to_chat("System", "❓ Help displayed")
        
    def read_aloud(self):
        """Read the chat content aloud"""
        # Get the last assistant response
        content = self.chat_display.get(1.0, tk.END).strip()
        if content:
            # Extract last assistant message
            lines = content.split('\n')
            for line in reversed(lines):
                if 'Assistant:' in line:
                    message = line.split('Assistant:', 1)[1].strip()
                    self.assistant.speak(message)
                    break
                    
    def update_font_size(self):
        """Update the font size"""
        size = self.font_size_var.get()
        self.accessibility.set_font_size(size)
        
        # Update chat font
        self.chat_display.config(font=("Arial", size))
        
        self.add_to_chat("System", f"🔤 Font size set to {size}")
        
    def toggle_high_contrast(self):
        """Toggle high contrast mode"""
        enabled = self.high_contrast_var.get()
        self.accessibility.set_high_contrast(enabled)
        
        if enabled:
            # Apply high contrast colors
            self.root.configure(bg="black")
            self.chat_display.configure(bg="black", fg="white")
            self.status_text.configure(bg="black", fg="white")
            self.add_to_chat("System", "👁️ High contrast mode enabled")
        else:
            # Revert to normal colors
            self.root.configure(bg="SystemButtonFace")
            self.chat_display.configure(bg="#f5f5f5", fg="#333333")
            self.status_text.configure(bg="SystemButtonFace", fg="black")
            self.add_to_chat("System", "👁️ High contrast mode disabled")
            
    def toggle_tts(self):
        """Toggle text-to-speech"""
        enabled = self.tts_var.get()
        self.accessibility.set_text_to_speech(enabled)
        status = "enabled" if enabled else "disabled"
        self.add_to_chat("System", f"🔊 Text-to-speech {status}")
        
    def apply_accessibility_settings(self):
        """Apply accessibility settings on startup"""
        # Apply font size
        size = self.config['accessibility']['font_size']
        self.font_size_var.set(size)
        self.chat_display.config(font=("Arial", size))
        
        # Apply high contrast
        if self.config['accessibility']['high_contrast']:
            self.high_contrast_var.set(True)
            self.toggle_high_contrast()
            
        # Apply TTS
        if not self.config['accessibility']['text_to_speech_enabled']:
            self.tts_var.set(False)
            
    def on_closing(self):
        """Handle application closing"""
        self.stop_listening()
        self.root.destroy()
        
def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set application icon
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    app = VoiceAssistantGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()