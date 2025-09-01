// Pomodoro Timer JavaScript
class PomodoroTimer {
    constructor() {
        this.updateInterval = null;
        this.lockdownEnabled = false;
        this.initializeElements();
        this.bindEvents();
        this.updateTimer();
    }

    initializeElements() {
        this.timerDisplay = document.getElementById('timerDisplay');
        this.sessionType = document.getElementById('sessionType');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.packageReady = document.getElementById('packageReady');
        this.cycleProgress = document.getElementById('cycleProgress');
        this.sessionProgress = document.getElementById('sessionProgress');
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startTimer());
        this.pauseBtn.addEventListener('click', () => this.pauseTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
    }

    async startTimer() {
        try {
            const response = await fetch('/start');
            const data = await response.json();
            this.updateUI(data);
            this.startUpdateInterval();
        } catch (error) {
            console.error('Error starting timer:', error);
            this.showStatus('Error starting timer', 'error');
        }
    }

    async pauseTimer() {
        try {
            const response = await fetch('/pause');
            const data = await response.json();
            this.updateUI(data);
            this.stopUpdateInterval();
        } catch (error) {
            console.error('Error pausing timer:', error);
            this.showStatus('Error pausing timer', 'error');
        }
    }

    async resetTimer() {
        try {
            const response = await fetch('/reset');
            const data = await response.json();
            this.updateUI(data);
            this.stopUpdateInterval();
        } catch (error) {
            console.error('Error resetting timer:', error);
            this.showStatus('Error resetting timer', 'error');
        }
    }

    startUpdateInterval() {
        this.updateInterval = setInterval(() => {
            this.updateTimer();
        }, 200); // Update every 200ms for smoother progress
    }

    stopUpdateInterval() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateTimer() {
        try {
            const response = await fetch('/api/timer-status');
            const data = await response.json();
            this.updateUI(data);
            
            // Check if package is ready
            if (data.package_ready) {
                this.showPackageReady();
            }
        } catch (error) {
            console.error('Error updating timer:', error);
        }
    }

    async updateProgress() {
        try {
            const response = await fetch('/api/session-progress');
            const data = await response.json();
            this.updateProgressBars(data);
        } catch (error) {
            console.error('Error updating progress:', error);
        }
    }

    updateUI(data) {
        // Update timer display
        this.timerDisplay.textContent = data.remaining_time;
        
        // Update session type
        this.sessionType.textContent = this.getSessionTypeText(data.current_state);
        this.sessionType.className = 'text-white mb-0'; // Always keep white color
        
        // Update button states
        this.updateButtonStates(data.session_status);
        
        // Update progress using server data with smoother calculations
        const sessionProgress = data.session_progress || 0;
        const cycleProgress = (data.completed_sessions / data.total_sessions) * 100;
        
        this.updateProgressBars({
            session_progress: sessionProgress,
            cycle_progress: cycleProgress
        });
    }

    updateButtonStates(sessionStatus) {
        if (sessionStatus === 'running') {
            this.startBtn.style.display = 'none';
            this.pauseBtn.style.display = 'inline-block';
        } else {
            this.startBtn.style.display = 'inline-block';
            this.pauseBtn.style.display = 'none';
        }
    }

    updateProgressBars(data) {
        // Smooth progress bar updates with gradual transitions
        const sessionProgress = Math.min(100, Math.max(0, data.session_progress || 0));
        const cycleProgress = Math.min(100, Math.max(0, data.cycle_progress || 0));
        
        this.sessionProgress.style.width = `${sessionProgress}%`;
        this.cycleProgress.style.width = `${cycleProgress}%`;
    }

    getSessionTypeText(state) {
        const sessionTypes = {
            'focus': 'Timer',
            'short_break': 'Break',
            'long_break': 'Long Break',
            'completed': 'Complete!'
        };
        return sessionTypes[state] || 'Timer';
    }

    getSessionTypeClass(state) {
        const classes = {
            'focus': 'text-danger',
            'short_break': 'text-success',
            'long_break': 'text-info',
            'completed': 'text-warning'
        };
        return classes[state] || 'text-muted';
    }

    showPackageReady() {
        this.packageReady.style.display = 'block';
        this.packageReady.classList.add('pulse');
    }

    isTimerRunning() {
        return this.pauseBtn.style.display === 'inline-block';
    }
}

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});

// Add some utility functions
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    }
}

// Request notification permission
if ('Notification' in window) {
    Notification.requestPermission();
} 