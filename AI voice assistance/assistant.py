"""
Voice Assistant Core Module
Handles speech recognition and text-to-speech
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional

class VoiceAssistant:
    """Core voice assistant functionality"""
    
    def __init__(self, config: dict):
        self.config = config
        self.name = config.get('name', 'AI Voice Assistant')
        self.language = config.get('language', 'en-US')
        self.wake_word = config.get('wake_word', 'assistant')
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        
        # Audio queue for async processing
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        
        # Adjust for ambient noise
        self.adjust_for_ambient_noise()
        
    def setup_voice(self):
        """Configure text-to-speech voice settings"""
        voices = self.tts_engine.getProperty('voices')
        
        # Select voice based on gender preference
        gender = self.config.get('voice_gender', 'female')
        for voice in voices:
            if gender.lower() in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
                
        # Set speech rate and volume
        rate = self.config.get('speech_rate', 180)
        volume = self.config.get('volume', 1.0)
        
        self.tts_engine.setProperty('rate', rate)
        self.tts_engine.setProperty('volume', volume)
        
    def adjust_for_ambient_noise(self):
        """Adjust microphone for ambient noise"""
        try:
            with self.microphone as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ambient noise adjustment complete")
        except Exception as e:
            print(f"Error adjusting for ambient noise: {e}")
            
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text
        
        Args:
            timeout: Maximum time to listen (seconds)
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            with self.microphone as source:
                print("Listening...")
                # Listen with timeout if specified
                if timeout:
                    audio = self.recognizer.listen(source, timeout=timeout)
                else:
                    audio = self.recognizer.listen(source)
                    
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"Recognized: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            print(f"Error in listen: {e}")
            return None
            
    def speak(self, text: str, async_mode: bool = True):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            async_mode: If True, speak asynchronously
        """
        if not text:
            return
            
        # Queue for async speaking
        if async_mode:
            threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
        else:
            self._speak_sync(text)
            
    def _speak_sync(self, text: str):
        """Synchronous speech synthesis"""
        try:
            self.is_speaking = True
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            self.is_speaking = False
            
    def speak_queue(self):
        """Process queued speech"""
        while True:
            try:
                text = self.audio_queue.get(timeout=1)
                self._speak_sync(text)
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in speak queue: {e}")
                
    def stop_speaking(self):
        """Stop current speech"""
        try:
            self.tts_engine.stop()
            self.is_speaking = False
        except:
            pass
            
    def is_available(self) -> bool:
        """Check if assistant is available"""
        return not self.is_speaking
        
    def set_voice_rate(self, rate: int):
        """Set speech rate"""
        self.tts_engine.setProperty('rate', rate)
        
    def set_voice_volume(self, volume: float):
        """Set speech volume"""
        self.tts_engine.setProperty('volume', max(0, min(1, volume)))
        
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        return self.tts_engine.getProperty('voices')