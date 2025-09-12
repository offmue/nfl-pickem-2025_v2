// Global variables
let currentUser = null;
let currentWeek = 1;
const API_BASE = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupLoginModal();
    checkAuthStatus();
    getCurrentWeek();
});

// Setup navigation
function setupNavigation() {
    const dashboardLink = document.getElementById('dashboard-link');
    const picksLink = document.getElementById('picks-link');
    const leaderboardLink = document.getElementById('leaderboard-link');
    const allPicksLink = document.getElementById('all-picks-link');
    
    dashboardLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('dashboard');
    });
    
    picksLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('picks');
    });
    
    leaderboardLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('leaderboard');
    });
    
    allPicksLink.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('all-picks');
    });
}

// Show a specific section
function showSection(section) {
    const sections = ['dashboard', 'picks', 'leaderboard', 'all-picks'];
    const links = ['dashboard-link', 'picks-link', 'leaderboard-link', 'all-picks-link'];
    
    sections.forEach(s => {
        document.getElementById(`${s}-section`).style.display = s === section ? 'block' : 'none';
    });
    
    links.forEach(l => {
        document.getElementById(l).classList.toggle('active', l === `${section}-link`);
    });
    
    // Load data for the section
    switch (section) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'picks':
            loadPicksData();
            break;
        case 'leaderboard':
            loadLeaderboardData();
            break;
        case 'all-picks':
            loadAllPicksData();
            break;
    }
}

// Setup login modal
function setupLoginModal() {
    const loginButton = document.getElementById('login-button');
    const loginModal = document.getElementById('login-modal');
    const closeButton = loginModal.querySelector('.close');
    const loginSubmit = document.getElementById('login-submit');
    const logoutButton = document.getElementById('logout-button');
    
    loginButton.addEventListener('click', () => {
        loginModal.style.display = 'block';
    });
    
    closeButton.addEventListener('click', () => {
        loginModal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            loginModal.style.display = 'none';
        }
    });
    
    loginSubmit.addEventListener('click', login);
    
    logoutButton.addEventListener('click', logout);
}

// Check authentication status
async function checkAuthStatus() {
    try {
        // First check localStorage
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                currentUser = JSON.parse(storedUser);
                updateAuthUI();
                loadDashboardData();
                return;
            } catch (e) {
                console.error('Error parsing stored user:', e);
                localStorage.removeItem('user');
            }
        }
        
        // If no stored user or parsing failed, check with server
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            localStorage.setItem('user', JSON.stringify(currentUser));
            updateAuthUI();
            loadDashboardData();
        } else {
            currentUser = null;
            updateAuthUI();
            loadDashboardData();
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        showToast('error', 'Fehler beim Überprüfen des Anmeldestatus');
    }
}

// Update UI based on authentication status
function updateAuthUI() {
    const loginButton = document.getElementById('login-button');
    const userDetails = document.getElementById('user-details');
    const usernameElement = document.getElementById('username');
    
    if (currentUser) {
        loginButton.style.display = 'none';
        userDetails.style.display = 'flex';
        usernameElement.textContent = currentUser.username;
    } else {
        loginButton.style.display = 'block';
        userDetails.style.display = 'none';
        usernameElement.textContent = '';
    }
}

// Login function
async function login() {
    try {
        showLoading();
        
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;
        
        if (!username || !password) {
            hideLoading();
            showToast('error', 'Bitte gib Benutzername und Passwort ein');
            return;
        }
        
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok && data.message === 'Login successful') {
            currentUser = data.user;
            localStorage.setItem('user', JSON.stringify(currentUser));
            
            document.getElementById('login-modal').style.display = 'none';
            document.getElementById('username-input').value = '';
            document.getElementById('password-input').value = '';
            
            updateAuthUI();
            loadDashboardData();
            
            showToast('success', 'Login erfolgreich');
        } else {
            showToast('error', data.error || 'Login fehlgeschlagen');
        }
    } catch (error) {
        console.error('Error during login:', error);
        showToast('error', 'Fehler beim Login');
    } finally {
        hideLoading();
    }
}

// Logout function
async function logout() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            currentUser = null;
            localStorage.removeItem('user');
            updateAuthUI();
            showSection('dashboard');
            showToast('success', 'Logout erfolgreich');
        } else {
            showToast('error', 'Logout fehlgeschlagen');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        showToast('error', 'Fehler beim Logout');
    } finally {
        hideLoading();
    }
}

// Get current week
async function getCurrentWeek() {
    try {
        const response = await fetch(`${API_BASE}/api/current-week`);
        
        if (response.ok) {
            const data = await response.json();
            currentWeek = data.current_week;
            document.getElementById('current-week').textContent = currentWeek;
            console.log('Current week set to', currentWeek);
        } else {
            console.error('Error fetching current week');
        }
    } catch (error) {
        console.error('Error fetching current week:', error);
    }
}

// Load dashboard data
async function loadDashboardData() {
    if (!currentUser) {
        document.getElementById('user-score').textContent = '0';
        document.getElementById('opponent-scores').innerHTML = 'Bitte einloggen, um Punkte zu sehen';
        document.getElementById('recent-picks').innerHTML = 'Bitte einloggen, um Picks zu sehen';
        document.getElementById('player-count').textContent = '0';
        return;
    }
    
    try {
        // Load user score and opponent scores
        const scoreResponse = await fetch(`${API_BASE}/api/picks/score?user_id=${currentUser.id}`);
        
        if (scoreResponse.ok) {
            const scoreData = await scoreResponse.json();
            
            document.getElementById('user-score').textContent = scoreData.user.score;
            
            let opponentHtml = '';
            scoreData.opponents.forEach(opponent => {
                opponentHtml += `
                    <div class="opponent-score">
                        <span class="opponent-name">${opponent.username}</span>: 
                        <span class="opponent-points">${opponent.score} Punkte</span>
                    </div>
                `;
            });
            
            document.getElementById('opponent-scores').innerHTML = opponentHtml || 'Keine Gegenspieler gefunden';
            document.getElementById('player-count').textContent = 1 + scoreData.opponents.length;
        } else {
            document.getElementById('opponent-scores').innerHTML = 'Fehler beim Laden der Punkte';
        }
        
        // Load recent picks
        const picksResponse = await fetch(`${API_BASE}/api/picks/recent?user_id=${currentUser.id}`);
        
        if (picksResponse.ok) {
            const picksData = await picksResponse.json();
            
            if (picksData.picks && picksData.picks.length > 0) {
                let picksHtml = '';
                picksData.picks.forEach(pick => {
                    const statusClass = pick.is_completed ? 
                        (pick.is_correct ? 'pick-correct' : 'pick-wrong') : 
                        'pick-pending';
                    
                    const statusText = pick.is_completed ? 
                        (pick.is_correct ? 'richtig' : 'falsch') : 
                        'ausstehend';
                    
                    picksHtml += `
                        <div class="recent-pick ${statusClass}">
                            <div class="pick-week">Woche ${pick.week}</div>
                            <div class="pick-team">
                                <img src="${pick.team_logo}" alt="${pick.team}" class="pick-team-logo">
                                ${pick.team}
                            </div>
                            <div class="pick-status">${statusText}</div>
                        </div>
                    `;
                });
                
                document.getElementById('recent-picks').innerHTML = picksHtml;
            } else {
                document.getElementById('recent-picks').innerHTML = 'Noch keine Picks gemacht';
            }
        } else {
            document.getElementById('recent-picks').innerHTML = 'Fehler beim Laden der Picks';
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        document.getElementById('opponent-scores').innerHTML = 'Fehler beim Laden der Punkte';
        document.getElementById('recent-picks').innerHTML = 'Fehler beim Laden der Picks';
    }
}

// Load picks data
async function loadPicksData(week = null) {
    if (!currentUser) {
        showToast('warning', 'Bitte logge dich ein, um deine Picks zu sehen');
        return;
    }
    
    try {
        showLoading();
        
        // If no week specified, use current week
        if (!week) {
            week = currentWeek;
        }
        
        // Load weeks for selector
        const weeksResponse = await fetch(`${API_BASE}/api/matches`);
        
        if (weeksResponse.ok) {
            const weeksData = await weeksResponse.json();
            
            // Get unique weeks
            const weeks = [...new Set(weeksData.matches.map(match => match.week))].sort((a, b) => a - b);
            
            // Populate week selector
            const weekSelect = document.getElementById('week-select');
            weekSelect.innerHTML = '';
            
            weeks.forEach(w => {
                const option = document.createElement('option');
                option.value = w;
                option.textContent = `Woche ${w}`;
                option.selected = w === parseInt(week);
                weekSelect.appendChild(option);
            });
            
            // Add event listener to week selector
            weekSelect.addEventListener('change', () => {
                loadMatchesForWeek(weekSelect.value);
            });
            
            // Load matches for selected week
            loadMatchesForWeek(week);
        } else {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Wochen';
        }
    } catch (error) {
        console.error('Error loading picks data:', error);
        document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Picks';
    } finally {
        hideLoading();
    }
}

// Load matches for a specific week
async function loadMatchesForWeek(week) {
    try {
        showLoading();
        
        // Get matches for the week
        const matchesResponse = await fetch(`${API_BASE}/api/matches?week=${week}`);
        
        if (!matchesResponse.ok) {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Matches';
            hideLoading();
            return;
        }
        
        const matchesData = await matchesResponse.json();
        
        // Get user's picks for the week
        const picksResponse = await fetch(`${API_BASE}/api/picks?user_id=${currentUser.id}&week=${week}`);
        
        if (!picksResponse.ok) {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Picks';
            hideLoading();
            return;
        }
        
        const picksData = await picksResponse.json();
        
        // Get eliminated teams
        const eliminatedResponse = await fetch(`${API_BASE}/api/picks/eliminated?user_id=${currentUser.id}`);
        
        if (!eliminatedResponse.ok) {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der eliminierten Teams';
            hideLoading();
            return;
        }
        
        const eliminatedData = await eliminatedResponse.json();
        const eliminatedTeamIds = eliminatedData.eliminated_teams.map(team => team.id);
        
        // Create HTML for matches
        let matchesHtml = '';
        
        if (matchesData.matches.length === 0) {
            matchesHtml = '<p>Keine Matches für diese Woche gefunden</p>';
        } else {
            matchesData.matches.forEach(match => {
                // Check if user has a pick for this match
                const userPick = picksData.picks.find(pick => pick.match.id === match.id);
                const selectedTeamId = userPick ? userPick.chosen_team.id : null;
                
                // Format date and time
                const matchDate = new Date(match.start_time);
                const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                const timeOptions = { hour: '2-digit', minute: '2-digit' };
                
                const formattedDate = matchDate.toLocaleDateString('de-DE', dateOptions);
                const formattedTime = matchDate.toLocaleTimeString('de-DE', timeOptions);
                
                // Check if teams are eliminated
                const homeTeamEliminated = eliminatedTeamIds.includes(match.home_team.id);
                const awayTeamEliminated = eliminatedTeamIds.includes(match.away_team.id);
                
                matchesHtml += `
                    <div class="match-card" data-match-id="${match.id}">
                        <div class="match-header">
                            <div class="match-date">${formattedDate}</div>
                            <div class="match-time">${formattedTime}</div>
                        </div>
                        <div class="match-teams">
                            <div class="match-team ${homeTeamEliminated ? 'eliminated' : ''} ${selectedTeamId === match.home_team.id ? 'selected' : ''}"
                                 data-team-id="${match.home_team.id}"
                                 data-match-id="${match.id}"
                                 data-team-name="${match.home_team.name}"
                                 ${homeTeamEliminated ? 'title="Dieses Team wurde bereits eliminiert"' : ''}>
                                <img src="${match.home_team.logo_url}" alt="${match.home_team.name}" class="match-team-logo">
                                <div class="match-team-name">${match.home_team.name}</div>
                                ${selectedTeamId === match.home_team.id ? '<div class="pick-indicator"><i class="fas fa-check"></i></div>' : ''}
                                ${match.is_completed && match.winner_team.id === match.home_team.id ? '<div class="winner-indicator"><i class="fas fa-trophy"></i></div>' : ''}
                            </div>
                            
                            <div class="match-vs">VS</div>
                            
                            <div class="match-team ${awayTeamEliminated ? 'eliminated' : ''} ${selectedTeamId === match.away_team.id ? 'selected' : ''}"
                                 data-team-id="${match.away_team.id}"
                                 data-match-id="${match.id}"
                                 data-team-name="${match.away_team.name}"
                                 ${awayTeamEliminated ? 'title="Dieses Team wurde bereits eliminiert"' : ''}>
                                <img src="${match.away_team.logo_url}" alt="${match.away_team.name}" class="match-team-logo">
                                <div class="match-team-name">${match.away_team.name}</div>
                                ${selectedTeamId === match.away_team.id ? '<div class="pick-indicator"><i class="fas fa-check"></i></div>' : ''}
                                ${match.is_completed && match.winner_team.id === match.away_team.id ? '<div class="winner-indicator"><i class="fas fa-trophy"></i></div>' : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        document.getElementById('matches-container').innerHTML = matchesHtml;
        
        // Add click event listeners to team boxes
        addTeamClickListeners();
    } catch (error) {
        console.error('Error loading matches for week:', error);
        document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Matches';
    } finally {
        hideLoading();
    }
}

// Add click event listeners to team boxes
function addTeamClickListeners() {
    const teamBoxes = document.querySelectorAll('.match-team:not(.eliminated)');
    
    teamBoxes.forEach(box => {
        box.addEventListener('click', function() {
            const matchId = this.dataset.matchId;
            const teamId = this.dataset.teamId;
            const teamName = this.dataset.teamName;
            
            selectMatchWinner(matchId, teamId, teamName);
        });
    });
}

// Select a match winner
async function selectMatchWinner(matchId, teamId, teamName) {
    if (!currentUser) {
        showToast('warning', 'Bitte logge dich ein, um Picks zu machen');
        return;
    }
    
    try {
        if (!confirm(`${teamName} als Gewinner auswählen?`)) {
            return;
        }
        
        showLoading();
        
        const response = await fetch(`${API_BASE}/api/picks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                match_id: matchId,
                chosen_team_id: teamId
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('success', data.message);
            
            // Update UI to show selected team
            const matchCard = document.querySelector(`.match-card[data-match-id="${matchId}"]`);
            
            if (matchCard) {
                // Remove selected class and pick indicator from all teams in this match
                const teams = matchCard.querySelectorAll('.match-team');
                teams.forEach(team => {
                    team.classList.remove('selected');
                    const indicator = team.querySelector('.pick-indicator');
                    if (indicator) {
                        indicator.remove();
                    }
                });
                
                // Add selected class and pick indicator to chosen team
                const chosenTeam = matchCard.querySelector(`.match-team[data-team-id="${teamId}"]`);
                if (chosenTeam) {
                    chosenTeam.classList.add('selected');
                    
                    const indicator = document.createElement('div');
                    indicator.className = 'pick-indicator';
                    indicator.innerHTML = '<i class="fas fa-check"></i>';
                    chosenTeam.appendChild(indicator);
                }
            }
            
            // Reload dashboard data to update recent picks
            loadDashboardData();
        } else {
            showToast('error', data.error || 'Fehler beim Speichern des Picks');
        }
    } catch (error) {
        console.error('Error selecting match winner:', error);
        showToast('error', 'Fehler beim Speichern des Picks');
    } finally {
        hideLoading();
    }
}

// Load leaderboard data
async function loadLeaderboardData() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/api/leaderboard`);
        
        if (response.ok) {
            const data = await response.json();
            
            let leaderboardHtml = `
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rang</th>
                            <th>Spieler</th>
                            <th>Punkte</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.leaderboard.forEach((player, index) => {
                const emoji = player.emoji ? `<span class="leaderboard-emoji">${player.emoji}</span>` : '';
                
                leaderboardHtml += `
                    <tr>
                        <td class="leaderboard-rank">${index + 1}</td>
                        <td>${player.username} ${emoji}</td>
                        <td>${player.score}</td>
                    </tr>
                `;
            });
            
            leaderboardHtml += `
                    </tbody>
                </table>
            `;
            
            document.getElementById('leaderboard-container').innerHTML = leaderboardHtml;
        } else {
            document.getElementById('leaderboard-container').innerHTML = 'Fehler beim Laden des Leaderboards';
        }
    } catch (error) {
        console.error('Error loading leaderboard data:', error);
        document.getElementById('leaderboard-container').innerHTML = 'Fehler beim Laden des Leaderboards';
    } finally {
        hideLoading();
    }
}

// Load all picks data
async function loadAllPicksData() {
    try {
        showLoading();
        
        // Get all users
        const usersResponse = await fetch(`${API_BASE}/api/leaderboard`);
        
        if (!usersResponse.ok) {
            document.getElementById('all-picks-container').innerHTML = 'Fehler beim Laden der Benutzer';
            hideLoading();
            return;
        }
        
        const usersData = await usersResponse.json();
        const users = usersData.leaderboard;
        
        // Get all matches
        const matchesResponse = await fetch(`${API_BASE}/api/matches`);
        
        if (!matchesResponse.ok) {
            document.getElementById('all-picks-container').innerHTML = 'Fehler beim Laden der Matches';
            hideLoading();
            return;
        }
        
        const matchesData = await matchesResponse.json();
        
        // Group matches by week
        const matchesByWeek = {};
        matchesData.matches.forEach(match => {
            if (!matchesByWeek[match.week]) {
                matchesByWeek[match.week] = [];
            }
            matchesByWeek[match.week].push(match);
        });
        
        // Get picks for all users
        const allPicks = {};
        
        for (const user of users) {
            const picksResponse = await fetch(`${API_BASE}/api/picks?user_id=${user.id}`);
            
            if (picksResponse.ok) {
                const picksData = await picksResponse.json();
                allPicks[user.id] = picksData.picks;
            }
        }
        
        // Create HTML for all picks
        let allPicksHtml = '<div class="all-picks-container">';
        
        // Sort weeks in descending order (most recent first)
        const weeks = Object.keys(matchesByWeek).sort((a, b) => b - a);
        
        for (const week of weeks) {
            allPicksHtml += `
                <div class="all-picks-week">
                    <h2>Woche ${week}</h2>
                    <table class="all-picks-table">
                        <thead>
                            <tr>
                                <th>Spieler</th>
                                <th>Pick</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            for (const user of users) {
                const userPicks = allPicks[user.id] || [];
                const weekPicks = userPicks.filter(pick => pick.match.week === parseInt(week));
                
                if (weekPicks.length > 0) {
                    for (const pick of weekPicks) {
                        const statusClass = pick.match.is_completed ? 
                            (pick.is_correct ? 'pick-correct' : 'pick-wrong') : 
                            'pick-pending';
                        
                        const statusText = pick.match.is_completed ? 
                            (pick.is_correct ? 'richtig' : 'falsch') : 
                            'ausstehend';
                        
                        allPicksHtml += `
                            <tr>
                                <td>${user.username}</td>
                                <td>
                                    <img src="${pick.chosen_team.logo_url}" alt="${pick.chosen_team.name}" class="all-picks-logo">
                                    ${pick.chosen_team.name}
                                </td>
                                <td class="${statusClass}">${statusText}</td>
                            </tr>
                        `;
                    }
                } else {
                    allPicksHtml += `
                        <tr>
                            <td>${user.username}</td>
                            <td colspan="2">Kein Pick</td>
                        </tr>
                    `;
                }
            }
            
            allPicksHtml += `
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        allPicksHtml += '</div>';
        
        document.getElementById('all-picks-container').innerHTML = allPicksHtml;
    } catch (error) {
        console.error('Error loading all picks data:', error);
        document.getElementById('all-picks-container').innerHTML = 'Fehler beim Laden der Picks';
    } finally {
        hideLoading();
    }
}

// Show loading spinner
function showLoading() {
    document.getElementById('loading-spinner').style.display = 'flex';
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loading-spinner').style.display = 'none';
}

// Show toast message
function showToast(type, message) {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle toast-icon"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle toast-icon"></i>';
            break;
        case 'info':
            icon = '<i class="fas fa-info-circle toast-icon"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle toast-icon"></i>';
            break;
    }
    
    toast.innerHTML = `
        ${icon}
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

