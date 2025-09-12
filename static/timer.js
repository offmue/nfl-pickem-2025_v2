// Football Sunday Timer
class FootballSundayTimer {
    constructor() {
        this.timerElement = null;
        this.interval = null;
        this.init();
    }

    init() {
        this.createTimerElement();
        this.startTimer();
    }

    createTimerElement() {
        // Create timer container
        const timerContainer = document.createElement('div');
        timerContainer.className = 'football-timer-container';
        timerContainer.innerHTML = `
            <div class="football-timer">
                <div class="timer-header">
                    <span class="fire-emoji">🔥</span>
                    <span class="timer-title">Football-Sunday</span>
                    <span class="fire-emoji">🔥</span>
                </div>
                <div class="timer-display">
                    <div class="time-unit">
                        <div class="time-value" id="days">00</div>
                        <div class="time-label">Days</div>
                    </div>
                    <div class="time-unit">
                        <div class="time-value" id="hours">00</div>
                        <div class="time-label">Hours</div>
                    </div>
                    <div class="time-unit">
                        <div class="time-value" id="minutes">00</div>
                        <div class="time-label">Minutes</div>
                    </div>
                    <div class="time-unit">
                        <div class="time-value" id="seconds">00</div>
                        <div class="time-label">Seconds</div>
                    </div>
                </div>
            </div>
        `;

        // Insert timer at the top of the main content
        const mainContent = document.querySelector('.container') || document.body;
        if (mainContent.firstChild) {
            mainContent.insertBefore(timerContainer, mainContent.firstChild);
        } else {
            mainContent.appendChild(timerContainer);
        }

        this.timerElement = timerContainer;
    }

    getNextFootballSunday() {
        const now = new Date();
        const vienna = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Vienna"}));
        
        // Find next Sunday at 19:00 Vienna time
        const nextSunday = new Date(vienna);
        const daysUntilSunday = (7 - vienna.getDay()) % 7;
        
        if (daysUntilSunday === 0) {
            // It's Sunday - check if it's before 19:00
            if (vienna.getHours() < 19) {
                // Same day at 19:00
                nextSunday.setHours(19, 0, 0, 0);
            } else {
                // Next Sunday at 19:00
                nextSunday.setDate(vienna.getDate() + 7);
                nextSunday.setHours(19, 0, 0, 0);
            }
        } else {
            // Next Sunday at 19:00
            nextSunday.setDate(vienna.getDate() + daysUntilSunday);
            nextSunday.setHours(19, 0, 0, 0);
        }

        return nextSunday;
    }

    updateTimer() {
        const now = new Date();
        const vienna = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Vienna"}));
        const target = this.getNextFootballSunday();
        
        const diff = target - vienna;

        if (diff <= 0) {
            // Football Sunday has started!
            this.showFootballSundayStarted();
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        // Update display
        document.getElementById('days').textContent = String(days).padStart(2, '0');
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
        document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');
    }

    showFootballSundayStarted() {
        const timerDisplay = this.timerElement.querySelector('.timer-display');
        timerDisplay.innerHTML = `
            <div class="football-started">
                <div class="started-message">Football-Sunday has started!</div>
                <div class="started-emoji">🏈🔥🏈</div>
            </div>
        `;
        
        // Stop the timer
        if (this.interval) {
            clearInterval(this.interval);
        }
    }

    startTimer() {
        // Update immediately
        this.updateTimer();
        
        // Update every second
        this.interval = setInterval(() => {
            this.updateTimer();
        }, 1000);
    }

    destroy() {
        if (this.interval) {
            clearInterval(this.interval);
        }
        if (this.timerElement) {
            this.timerElement.remove();
        }
    }
}

// Initialize timer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only show timer on dashboard and picks pages
    const currentPage = window.location.pathname;
    if (currentPage === '/' || currentPage.includes('picks')) {
        new FootballSundayTimer();
    }
});

