"""
Accessibility Module
Handles accessibility features for users with disabilities
"""

import tkinter as tk
from tkinter import font
import json
from typing import Dict, Any

class AccessibilityManager:
    """Manage accessibility features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.font_size = config.get('font_size', 12)
        self.high_contrast = config.get('high_contrast', False)
        self.text_to_speech = config.get('text_to_speech_enabled', True)
        self.voice_feedback = config.get('voice_feedback_enabled', True)
        self.screen_reader = config.get('screen_reader_compatible', True)
        
        # Color schemes
        self.color_schemes = {
            'normal': {
                'bg': '#f5f5f5',
                'fg': '#333333',
                'button_bg': '#e0e0e0',
                'button_fg': '#000000',
                'highlight': '#4CAF50'
            },
            'high_contrast': {
                'bg': '#000000',
                'fg': '#FFFFFF',
                'button_bg': '#FFFFFF',
                'button_fg': '#000000',
                'highlight': '#FFFF00'
            }
        }
        
    def get_color_scheme(self) -> Dict[str, str]:
        """Get current color scheme"""
        if self.high_contrast:
            return self.color_schemes['high_contrast']
        return self.color_schemes['normal']
        
    def set_font_size(self, size: int):
        """Set font size"""
        self.font_size = max(8, min(30, size))
        self.config['font_size'] = self.font_size
        self.save_config()
        
    def set_high_contrast(self, enabled: bool):
        """Enable or disable high contrast mode"""
        self.high_contrast = enabled
        self.config['high_contrast'] = enabled
        self.save_config()
        
    def set_text_to_speech(self, enabled: bool):
        """Enable or disable text-to-speech"""
        self.text_to_speech = enabled
        self.config['text_to_speech_enabled'] = enabled
        self.save_config()
        
    def set_voice_feedback(self, enabled: bool):
        """Enable or disable voice feedback"""
        self.voice_feedback = enabled
        self.config['voice_feedback_enabled'] = enabled
        self.save_config()
        
    def save_config(self):
        """Save accessibility settings to config"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            config['accessibility'] = self.config
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving accessibility config: {e}")
            
    def apply_to_widget(self, widget: tk.Widget):
        """Apply accessibility settings to a widget"""
        if isinstance(widget, (tk.Label, tk.Button, tk.Text, tk.Entry)):
            # Apply font size
            if self.font_size:
                current_font = widget.cget('font')
                if isinstance(current_font, tuple):
                    widget.config(font=(current_font[0], self.font_size))
                else:
                    widget.config(font=("Arial", self.font_size))
                    
        # Apply color scheme
        if self.high_contrast:
            colors = self.color_schemes['high_contrast']
            widget.config(
                bg=colors['bg'],
                fg=colors['fg']
            )
            
    def get_font(self, family: str = "Arial", weight: str = "normal") -> tuple:
        """Get font with current size"""
        return (family, self.font_size, weight)
        
    def create_font_object(self, master, family: str = "Arial", weight: str = "normal") -> font.Font:
        """Create a font object with current size"""
        return font.Font(master, family=family, size=self.font_size, weight=weight)
        
    def is_screen_reader_ready(self) -> bool:
        """Check if screen reader compatibility is enabled"""
        return self.screen_reader
        
    def get_accessibility_status(self) -> Dict[str, Any]:
        """Get current accessibility status"""
        return {
            'font_size': self.font_size,
            'high_contrast': self.high_contrast,
            'text_to_speech': self.text_to_speech,
            'voice_feedback': self.voice_feedback,
            'screen_reader': self.screen_reader
        }