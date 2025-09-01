import os
from datetime import timedelta

class Config:
    """Configuration settings for the Pomodoro app"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # Timer settings (in minutes) - Testing with shorter durations
    FOCUS_DURATION = 0.417  # 25 seconds
    SHORT_BREAK_DURATION = 0.083  # 5 seconds
    LONG_BREAK_DURATION = 0.25  # 15 seconds
    SESSIONS_PER_CYCLE = 4
    
    # File paths
    DATA_DIR = 'data'
    PHOTOS_DIR = os.path.join(DATA_DIR, 'photos')
    QUOTES_DIR = os.path.join(DATA_DIR, 'quotes')
    USER_DATA_FILE = os.path.join(DATA_DIR, 'user_data.json')
    
    # Timer states
    TIMER_STATES = {
        'focus': 'focus',
        'short_break': 'short_break',
        'long_break': 'long_break',
        'completed': 'completed'
    }
    
    # Session status
    SESSION_STATUS = {
        'idle': 'idle',
        'running': 'running',
        'paused': 'paused',
        'completed': 'completed'
    }
    
    @staticmethod
    def get_duration_minutes(state):
        """Get duration in minutes for a given timer state"""
        durations = {
            Config.TIMER_STATES['focus']: Config.FOCUS_DURATION,
            Config.TIMER_STATES['short_break']: Config.SHORT_BREAK_DURATION,
            Config.TIMER_STATES['long_break']: Config.LONG_BREAK_DURATION
        }
        return durations.get(state, 0)
    
    @staticmethod
    def get_duration_seconds(state):
        """Get duration in seconds for a given timer state"""
        return Config.get_duration_minutes(state) * 60
    
    @staticmethod
    def format_time(seconds):
        """Format seconds into MM:SS format"""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    @staticmethod
    def ensure_directories():
        """Ensure all required directories exist"""
        directories = [Config.DATA_DIR, Config.PHOTOS_DIR, Config.QUOTES_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True) 