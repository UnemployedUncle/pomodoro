import json
import time
from datetime import datetime, timedelta
from config import Config

class PomodoroTimer:
    """Manages Pomodoro timer state and session tracking"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset timer to initial state"""
        self.current_state = Config.TIMER_STATES['focus']
        self.session_status = Config.SESSION_STATUS['idle']
        self.completed_sessions = 0
        self.total_sessions = Config.SESSIONS_PER_CYCLE
        self.start_time = None
        self.pause_time = None
        self.remaining_seconds = Config.get_duration_seconds(self.current_state)
    
    def start(self):
        """Start the timer"""
        if self.session_status == Config.SESSION_STATUS['idle']:
            self.start_time = datetime.now()
            self.session_status = Config.SESSION_STATUS['running']
            self.pause_time = None
        elif self.session_status == Config.SESSION_STATUS['paused']:
            # Resume from pause
            if self.pause_time:
                pause_duration = (datetime.now() - self.pause_time).total_seconds()
                self.start_time += timedelta(seconds=pause_duration)
            self.session_status = Config.SESSION_STATUS['running']
            self.pause_time = None
    
    def pause(self):
        """Pause the timer"""
        if self.session_status == Config.SESSION_STATUS['running']:
            self.session_status = Config.SESSION_STATUS['paused']
            self.pause_time = datetime.now()
            self.update_remaining_time()
    
    def stop(self):
        """Stop the timer"""
        self.session_status = Config.SESSION_STATUS['idle']
        self.start_time = None
        self.pause_time = None
        self.remaining_seconds = Config.get_duration_seconds(self.current_state)
    
    def update_remaining_time(self):
        """Update remaining time based on elapsed time"""
        if self.session_status == Config.SESSION_STATUS['running'] and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            total_duration = Config.get_duration_seconds(self.current_state)
            self.remaining_seconds = max(0, total_duration - elapsed)
            
            # Check if session is complete
            if self.remaining_seconds <= 0:
                self.complete_session()
    
    def complete_session(self):
        """Complete current session and move to next state"""
        if self.current_state == Config.TIMER_STATES['focus']:
            self.completed_sessions += 1
            
            # Check if all sessions are complete
            if self.completed_sessions >= self.total_sessions:
                self.current_state = Config.TIMER_STATES['completed']
                self.session_status = Config.SESSION_STATUS['completed']
            else:
                # Move to short break or long break
                if self.completed_sessions % 4 == 0:
                    self.current_state = Config.TIMER_STATES['long_break']
                else:
                    self.current_state = Config.TIMER_STATES['short_break']
        else:
            # Break is complete, move to next focus session
            self.current_state = Config.TIMER_STATES['focus']
        
        # Reset timer for next session
        self.remaining_seconds = Config.get_duration_seconds(self.current_state)
        self.start_time = None
        self.pause_time = None
        self.session_status = Config.SESSION_STATUS['idle']
    
    def get_status(self):
        """Get current timer status for API responses"""
        self.update_remaining_time()
        
        return {
            'current_state': self.current_state,
            'session_status': self.session_status,
            'completed_sessions': self.completed_sessions,
            'total_sessions': self.total_sessions,
            'remaining_seconds': int(self.remaining_seconds),
            'remaining_time': Config.format_time(int(self.remaining_seconds)),
            'is_complete': self.current_state == Config.TIMER_STATES['completed']
        }
    
    def get_session_progress(self):
        """Get progress percentage for current session"""
        if self.session_status == Config.SESSION_STATUS['idle']:
            return 0
        
        total_duration = Config.get_duration_seconds(self.current_state)
        elapsed = total_duration - self.remaining_seconds
        return min(100, (elapsed / total_duration) * 100)
    
    def get_cycle_progress(self):
        """Get progress percentage for the entire cycle (4 sessions)"""
        return (self.completed_sessions / self.total_sessions) * 100 