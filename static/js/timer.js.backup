// Pomodoro Timer JavaScript
class PomodoroTimer {
    constructor() {
        this.updateInterval = null;
        this.tapCount = 0;
        this.tapTimeout = null;
        this.initializeElements();
        this.bindEvents();
        this.updateTimer();
    }

    initializeElements() {
        this.timerDisplay = document.getElementById('timerDisplay');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.packageReady = document.getElementById('packageReady');
        this.cycleProgress = document.getElementById('cycleProgress');
        this.sessionProgress = document.getElementById('sessionProgress');
        this.tapCircles = document.getElementById('tapCircles');
        this.circle1 = document.getElementById('circle1');
        this.circle2 = document.getElementById('circle2');
        this.circle3 = document.getElementById('circle3');
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        
        // Add tap to pause functionality
        document.addEventListener('click', (e) => this.handleTap(e));
    }

    handleTap(event) {
        // Don't count taps on buttons or other interactive elements
        if (event.target.closest('button') || event.target.closest('a') || event.target.closest('.tap-circles')) {
            return;
        }

        // Only count taps when timer is running
        if (this.updateInterval) {
            this.tapCount++;
            this.updateTapCircles();
            
            // Clear existing timeout
            if (this.tapTimeout) {
                clearTimeout(this.tapTimeout);
            }
            
            // Set timeout to reset tap count
            this.tapTimeout = setTimeout(() => {
                this.resetTapCount();
            }, 2000); // 2 seconds to complete 3 taps
            
            // Check if 3 taps completed
            if (this.tapCount >= 3) {
                this.pauseTimer();
            }
        }
    }

    updateTapCircles() {
        this.tapCircles.style.display = 'flex';
        
        if (this.tapCount >= 1) this.circle1.classList.add('filled');
        if (this.tapCount >= 2) this.circle2.classList.add('filled');
        if (this.tapCount >= 3) this.circle3.classList.add('filled');
    }

    resetTapCount() {
        this.tapCount = 0;
        this.circle1.classList.remove('filled');
        this.circle2.classList.remove('filled');
        this.circle3.classList.remove('filled');
        this.tapCircles.style.display = 'none';
        
        if (this.tapTimeout) {
            clearTimeout(this.tapTimeout);
            this.tapTimeout = null;
        }
    }

    async startTimer() {
        try {
            const response = await fetch('/start');
            const data = await response.json();
            this.updateUI(data);
            this.startUpdateInterval();
            this.resetTapCount();
        } catch (error) {
            console.error('Error starting timer:', error);
        }
    }

    async pauseTimer() {
        try {
            const response = await fetch('/pause');
            const data = await response.json();
            this.updateUI(data);
            this.stopUpdateInterval();
            this.resetTapCount();
        } catch (error) {
            console.error('Error pausing timer:', error);
        }
    }

    async resetTimer() {
        try {
            const response = await fetch('/reset');
            const data = await response.json();
            this.updateUI(data);
            this.stopUpdateInterval();
            this.resetTapCount();
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
        
        // Update button states
        if (data.session_status === 'running') {
            this.startBtn.style.display = 'none';
            this.resetBtn.style.display = 'none';
        } else {
            this.startBtn.style.display = 'inline-block';
            this.resetBtn.style.display = 'inline-block';
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