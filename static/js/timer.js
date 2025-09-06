// Pomodoro Timer JavaScript
class PomodoroTimer {
    constructor() {
        this.updateInterval = null;
        this.focusCirclesRemaining = 3;
        this.initializeElements();
        this.bindEvents();
        this.updateTimer();
    }

    initializeElements() {
        this.timerDisplay = document.getElementById('timerDisplay');
        this.startBtn = document.getElementById('startBtn');
        this.packageReady = document.getElementById('packageReady');
        this.cycleProgress = document.getElementById('cycleProgress');
        this.sessionProgress = document.getElementById('sessionProgress');
        this.tapCircles = document.getElementById('tapCircles');
        this.circle1 = document.getElementById('circle1');
        this.circle2 = document.getElementById('circle2');
        this.circle3 = document.getElementById('circle3');
    }

    bindEvents() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => {
                this.startTimer();
            });
        }
        
        // Add tap to focus functionality
        document.addEventListener('click', (e) => this.handleFocusTap(e));
    }

    handleFocusTap(event) {
        // Don't count taps on buttons or other interactive elements
        if (event.target.closest('button') || event.target.closest('a') || event.target.closest('.focus-circles')) {
            return;
        }

        // Only handle focus taps when timer is running
        if (this.updateInterval && this.focusCirclesRemaining > 0) {
            this.removeFocusCircle();
        }
    }

    showFocusCircles() {
        this.tapCircles.style.display = 'flex';
        this.circle1.style.display = 'block';
        this.circle2.style.display = 'block';
        this.circle3.style.display = 'block';
        this.focusCirclesRemaining = 3;
    }

    removeFocusCircle() {
        this.focusCirclesRemaining--;
        
        // Hide circles one by one
        if (this.focusCirclesRemaining === 2) {
            this.circle1.style.display = 'none';
        } else if (this.focusCirclesRemaining === 1) {
            this.circle2.style.display = 'none';
        } else if (this.focusCirclesRemaining === 0) {
            this.circle3.style.display = 'none';
            // All focus circles removed, reset to beginning
            this.resetToBeginning();
        }
    }

    hideFocusCircles() {
        this.tapCircles.style.display = 'none';
        this.circle1.style.display = 'block';
        this.circle2.style.display = 'block';
        this.circle3.style.display = 'block';
        this.focusCirclesRemaining = 3;
    }

    async startTimer() {
        try {
            const response = await fetch('/start');
            const data = await response.json();
            this.updateUI(data);
            this.startUpdateInterval();
            this.showFocusCircles();
        } catch (error) {
            console.error('Error starting timer:', error);
        }
    }

    async resetToBeginning() {
        try {
            const response = await fetch('/reset');
            const data = await response.json();
            this.updateUI(data);
            this.stopUpdateInterval();
            this.hideFocusCircles();
        } catch (error) {
            console.error('Error resetting timer:', error);
        }
    }

    startUpdateInterval() {
        this.updateInterval = setInterval(() => {
            this.updateTimer();
        }, 200);
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
            
            // Check if session completed naturally
            if (data.session_status === 'completed' || data.current_state === 'completed') {
                this.stopUpdateInterval();
                this.hideFocusCircles();
                // Auto-reset to beginning when session completes
                setTimeout(() => {
                    this.resetToBeginning();
                }, 1000);
            }
            
            if (data.package_ready) {
                this.packageReady.style.display = 'block';
                this.packageReady.classList.add('pulse');
            }
        } catch (error) {
            console.error('Error updating timer:', error);
        }
    }

    updateUI(data) {
        // Update timer display
        this.timerDisplay.textContent = data.remaining_time;
        
        // Update button states - always show start button when not running
        if (data.session_status === 'running') {
            this.startBtn.style.display = 'none';
        } else {
            this.startBtn.style.display = 'inline-block';
        }
        
        // Update progress bars
        const sessionProgress = Math.min(100, Math.max(0, data.session_progress || 0));
        const cycleProgress = Math.min(100, Math.max(0, (data.completed_sessions / data.total_sessions) * 100));
        
        this.sessionProgress.style.width = `${sessionProgress}%`;
        this.cycleProgress.style.width = `${cycleProgress}%`;
    }
}

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});

// Request notification permission
if ('Notification' in window) {
    Notification.requestPermission();
}
