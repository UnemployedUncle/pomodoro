// Focus Time Timer JavaScript
class PomodoroTimer {
    constructor() {
        this.updateInterval = null;
        this.focusCirclesRemaining = 3;
        this.currentTemplate = 1;
        this.currentSession = 1;
        this.totalSessions = 4;
        this.isTestMode = true; // Set to false for production (25min/5min/15min)
        
        // Timer durations (in seconds for test mode)
        this.focusDuration = this.isTestMode ? 25 : 25 * 60; // 25 seconds or 25 minutes
        this.shortBreakDuration = this.isTestMode ? 5 : 5 * 60; // 5 seconds or 5 minutes
        this.longBreakDuration = this.isTestMode ? 15 : 15 * 60; // 15 seconds or 15 minutes
        
        this.quotes = [
            { quote: "It is not that we have a short time to live, but that we waste a lot of it.", speaker: "Seneca" },
            { quote: "Time is the most valuable thing that a man can spend.", speaker: "Theophrastus" },
            { quote: "Dost thou love life? Then do not squander time, for that's the stuff life is made of.", speaker: "Benjamin Franklin" },
            { quote: "Time is what we want most, but what we use worst.", speaker: "William Penn" },
            { quote: "Yesterday is gone. Tomorrow has not yet come. We have only today. Let us begin.", speaker: "Mother Teresa" }
        ];
        
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
        this.focusCircles = document.getElementById('focusCircles');
        this.circle1 = document.getElementById('circle1');
        this.circle2 = document.getElementById('circle2');
        this.circle3 = document.getElementById('circle3');
        this.currentQuote = document.getElementById('currentQuote');
        this.currentSpeaker = document.getElementById('currentSpeaker');
        this.timerContainer = document.getElementById('timerContainer');
    }

    setTemplateId(templateId) {
        this.currentTemplate = templateId;
        this.updateTemplate();
    }

    updateTemplate() {
        if (this.timerContainer) {
            this.timerContainer.className = `timer-container template-${this.currentTemplate}`;
        }
        this.updateQuote(this.currentTemplate - 1);
    }

    updateQuote(quoteIndex) {
        if (this.currentQuote && this.currentSpeaker) {
            const quote = this.quotes[quoteIndex % this.quotes.length];
            this.currentQuote.textContent = quote.quote;
            this.currentSpeaker.textContent = quote.speaker;
        }
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
        if (event.target.closest('button') || event.target.closest('a') || event.target.closest('.focus-circles-container')) {
            return;
        }

        // Only handle focus taps when timer is running
        if (this.updateInterval && this.focusCirclesRemaining > 0) {
            this.removeFocusCircle();
        }
    }

    showFocusCircles() {
        if (this.focusCircles) {
            this.focusCircles.style.display = 'flex';
        }
        this.updateFocusCircles(3);
        this.focusCirclesRemaining = 3;
    }

    removeFocusCircle() {
        this.focusCirclesRemaining--;
        this.updateFocusCircles(this.focusCirclesRemaining);
        
        if (this.focusCirclesRemaining === 0) {
            // All focus circles removed, reset to beginning
            this.resetToBeginning();
        }
    }

    updateFocusCircles(activeCount) {
        // Remove all active classes first
        if (this.circle1) this.circle1.classList.remove('disappearing');
        if (this.circle2) this.circle2.classList.remove('disappearing');
        if (this.circle3) this.circle3.classList.remove('disappearing');
        
        // Add disappearing class to inactive circles
        if (activeCount < 3 && this.circle1) this.circle1.classList.add('disappearing');
        if (activeCount < 2 && this.circle2) this.circle2.classList.add('disappearing');
        if (activeCount < 1 && this.circle3) this.circle3.classList.add('disappearing');
    }

    hideFocusCircles() {
        if (this.focusCircles) {
            this.focusCircles.style.display = 'none';
        }
        this.updateFocusCircles(0);
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
                if (this.packageReady) {
                    this.packageReady.style.display = 'block';
                    this.packageReady.classList.add('pulse');
                }
                // Earn template after 4 sessions
                this.earnTemplate();
            }
        } catch (error) {
            console.error('Error updating timer:', error);
        }
    }

    async earnTemplate() {
        try {
            const response = await fetch('/api/earn-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    template_id: this.currentTemplate
                })
            });
            const data = await response.json();
            if (data.success) {
                console.log(data.message);
            }
        } catch (error) {
            console.error('Error earning template:', error);
        }
    }

    updateUI(data) {
        // Update timer display
        if (this.timerDisplay) {
            this.timerDisplay.textContent = data.remaining_time;
        }
        
        // Update button states
        if (this.startBtn) {
            if (data.session_status === 'running') {
                this.startBtn.style.display = 'none';
            } else {
                this.startBtn.style.display = 'inline-block';
            }
        }
        
        // Update progress bars
        const sessionProgress = Math.min(100, Math.max(0, data.session_progress || 0));
        const cycleProgress = Math.min(100, Math.max(0, (data.completed_sessions / this.totalSessions) * 100));
        
        if (this.sessionProgress) {
            this.sessionProgress.style.width = `${sessionProgress}%`;
        }
        if (this.cycleProgress) {
            this.cycleProgress.style.width = `${cycleProgress}%`;
        }
    }
}

// Global timer instance
let timerInstance = null;

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', () => {
    timerInstance = new PomodoroTimer();
    window.timerInstance = timerInstance; // Make it globally accessible
});

// Request notification permission
if ('Notification' in window) {
    Notification.requestPermission();
}