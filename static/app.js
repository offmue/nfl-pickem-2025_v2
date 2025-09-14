// API base URL
const API_BASE = '';

// Global variables
let currentUser = null;
let currentWeek = 2; // Default to week 2

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the app
async function initializeApp() {
    setupNavigation();
    setupModal();
    setupLoginForm();
    await checkAuthStatus();
    await getCurrentWeek();
    loadDashboardData();
}

// Set up navigation
function setupNavigation() {
    const dashboardLink = document.getElementById('dashboard-link');
    const picksLink = document.getElementById('picks-link');
    const leaderboardLink = document.getElementById('leaderboard-link');
    const allPicksLink = document.getElementById('all-picks-link');
    
    dashboardLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection('dashboard');
    });
    
    picksLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection('picks');
    });
    
    leaderboardLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection('leaderboard');
    });
    
    allPicksLink.addEventListener('click', function(e) {
        e.preventDefault();
        showSection('all-picks');
    });
}

// Show a specific section
function showSection(section) {
    // Hide all sections
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('picks-section').style.display = 'none';
    document.getElementById('leaderboard-section').style.display = 'none';
    document.getElementById('all-picks-section').style.display = 'none';
    
    // Remove active class from all links
    document.getElementById('dashboard-link').classList.remove('active');
    document.getElementById('picks-link').classList.remove('active');
    document.getElementById('leaderboard-link').classList.remove('active');
    document.getElementById('all-picks-link').classList.remove('active');
    
    // Show the selected section and mark link as active
    document.getElementById(`${section}-section`).style.display = 'block';
    document.getElementById(`${section}-link`).classList.add('active');
    
    // Load section-specific data
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

// Set up modal
function setupModal() {
    const modal = document.getElementById('login-modal');
    const closeBtn = modal.querySelector('.close');
    const loginBtn = document.getElementById('login-button');
    
    loginBtn.addEventListener('click', function() {
        modal.style.display = 'block';
    });
    
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Set up login form
function setupLoginForm() {
    const loginForm = document.getElementById('login-submit');
    
    loginForm.addEventListener('click', function() {
        const username = document.getElementById('username-input').value;
        const password = document.getElementById('password-input').value;
        
        login(username, password);
    });
    
    // Add event listener for Enter key
    document.getElementById('password-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const username = document.getElementById('username-input').value;
            const password = document.getElementById('password-input').value;
            
            login(username, password);
        }
    });
}

// Login function
async function login(username, password) {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.message === 'Login successful') {
            // Store user data
            currentUser = data.user;
            localStorage.setItem('user', JSON.stringify(currentUser));
            
            // Update UI
            updateAuthUI();
            
            // Hide modal
            document.getElementById('login-modal').style.display = 'none';
            
            // Show success message
            showToast('success', 'Login erfolgreich');
            
            // Reload data
            loadDashboardData();
        } else {
            showToast('error', data.error || 'Login fehlgeschlagen');
        }
    } catch (error) {
        console.error('Error during login:', error);
        showToast('error', 'Ein Fehler ist aufgetreten');
    } finally {
        hideLoading();
    }
}

// Logout function
async function logout() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Clear user data
            currentUser = null;
            localStorage.removeItem('user');
            
            // Update UI
            updateAuthUI();
            
            // Show success message
            showToast('success', 'Logout erfolgreich');
            
            // Go back to dashboard
            showSection('dashboard');
        } else {
            showToast('error', 'Logout fehlgeschlagen');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        showToast('error', 'Ein Fehler ist aufgetreten');
    } finally {
        hideLoading();
    }
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
                return;
            } catch (e) {
                console.error('Error parsing stored user:', e);
                localStorage.removeItem('user');
            }
        }
        
        // If no stored user or parsing failed, check with server
        const response = await fetch(`${API_BASE}/api/auth/me`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.user) {
                currentUser = data.user;
                localStorage.setItem('user', JSON.stringify(currentUser));
                updateAuthUI();
            }
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
    }
}

// Update authentication UI
function updateAuthUI() {
    const userDetails = document.getElementById('user-details');
    const loginButton = document.getElementById('login-button');
    const usernameElement = document.getElementById('username');
    const logoutButton = document.getElementById('logout-button');
    
    if (currentUser) {
        userDetails.style.display = 'flex';
        loginButton.style.display = 'none';
        usernameElement.textContent = currentUser.username;
        
        // Add logout event listener
        logoutButton.addEventListener('click', logout);
    } else {
        userDetails.style.display = 'none';
        loginButton.style.display = 'block';
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
        }
    } catch (error) {
        console.error('Error getting current week:', error);
    }
}

// Load dashboard data
async function loadDashboardData() {
    if (!currentUser) {
        document.getElementById('user-score').textContent = '0';
        document.getElementById('user-rank').textContent = '-';
        document.getElementById('opponent-scores').innerHTML = 'Bitte einloggen';
        document.getElementById('recent-picks').innerHTML = 'Bitte einloggen';
        document.getElementById('eliminated-teams').innerHTML = 'Bitte einloggen';
        return;
    }
    
    try {
        // Get user score
        const scoreResponse = await fetch(`${API_BASE}/api/picks/score?user_id=${currentUser.id}`);
        
        if (scoreResponse.ok) {
            const scoreData = await scoreResponse.json();
            
            // Update user score
            document.getElementById('user-score').textContent = scoreData.user.score;
            
            // Update opponent scores
            let opponentHtml = '';
            
            if (scoreData.opponents.length > 0) {
                scoreData.opponents.forEach(opponent => {
                    opponentHtml += `
                        <div class="opponent-score">
                            <span class="opponent-name">${opponent.username}:</span>
                            <span class="opponent-points">${opponent.score} Punkte</span>
                        </div>
                    `;
                });
            } else {
                opponentHtml = 'Keine Gegenspieler gefunden';
            }
            
            document.getElementById('opponent-scores').innerHTML = opponentHtml;
        } else {
            document.getElementById('opponent-scores').innerHTML = 'Fehler beim Laden der Punkte';
        }
        
        // Get user rank
        const rankResponse = await fetch(`${API_BASE}/api/user/rank?user_id=${currentUser.id}`);
        
        if (rankResponse.ok) {
            const rankData = await rankResponse.json();
            document.getElementById('user-rank').textContent = `Du bist aktuell auf Platz ${rankData.rank}`;
        } else {
            document.getElementById('user-rank').textContent = '-';
        }
        
        // Get recent picks
        const picksResponse = await fetch(`${API_BASE}/api/picks/recent?user_id=${currentUser.id}`);
        
        if (picksResponse.ok) {
            const picksData = await picksResponse.json();
            
            if (picksData.picks && picksData.picks.length > 0) {
                let picksHtml = '';
                
                picksData.picks.forEach(pick => {
                    let resultText = 'Ausstehend';
                    let resultClass = 'pending';
                    
                    if (pick.is_completed) {
                        if (pick.is_correct) {
                            resultText = 'Richtig';
                            resultClass = 'correct';
                        } else {
                            resultText = 'Falsch';
                            resultClass = 'incorrect';
                        }
                    }
                    
                    picksHtml += `
                        <div class="recent-pick">
                            <img src="${pick.team_logo}" alt="${pick.team}" class="team-logo-small">
                            <div class="recent-pick-info">
                                <div class="recent-pick-week">Woche ${pick.week}</div>
                                <div class="recent-pick-team">${pick.team}</div>
                            </div>
                            <div class="recent-pick-result ${resultClass}">${resultText}</div>
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
        
        // Get eliminated teams
        const eliminatedResponse = await fetch(`${API_BASE}/api/picks/eliminated?user_id=${currentUser.id}`);
        
        if (eliminatedResponse.ok) {
            const eliminatedData = await eliminatedResponse.json();
            
            if (eliminatedData.eliminated_teams && eliminatedData.eliminated_teams.length > 0) {
                let eliminatedHtml = '';
                
                eliminatedData.eliminated_teams.forEach(team => {
                    eliminatedHtml += `
                        <div class="eliminated-team">
                            <img src="${team.logo_url}" alt="${team.name}" class="eliminated-team-logo team-logo-small">
                            <div class="eliminated-team-name">${team.name}</div>
                        </div>
                    `;
                });
                
                document.getElementById('eliminated-teams').innerHTML = eliminatedHtml;
            } else {
                document.getElementById('eliminated-teams').innerHTML = 'Keine eliminierten Teams';
            }
        } else {
            document.getElementById('eliminated-teams').innerHTML = 'Fehler beim Laden der eliminierten Teams';
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        document.getElementById('opponent-scores').innerHTML = 'Fehler beim Laden der Punkte';
        document.getElementById('recent-picks').innerHTML = 'Fehler beim Laden der Picks';
        document.getElementById('eliminated-teams').innerHTML = 'Fehler beim Laden der eliminierten Teams';
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
        
        // NEW RULE: Check if user already has a pick for this week (only one pick per week allowed)
        const hasWeekPick = picksData.picks.length > 0;
        const weekPickMatch = hasWeekPick ? picksData.picks[0].match : null;
        
        // Get eliminated teams
        const eliminatedResponse = await fetch(`${API_BASE}/api/picks/eliminated?user_id=${currentUser.id}`);
        
        if (!eliminatedResponse.ok) {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der eliminierten Teams';
            hideLoading();
            return;
        }
        
        const eliminatedData = await eliminatedResponse.json();
        const eliminatedTeamIds = eliminatedData.eliminated_teams.map(team => team.id);
        
        // Get team winner usage
        const teamUsageResponse = await fetch(`${API_BASE}/api/picks/team-usage?user_id=${currentUser.id}`);
        
        if (!teamUsageResponse.ok) {
            document.getElementById('matches-container').innerHTML = 'Fehler beim Laden der Team-Nutzung';
            hideLoading();
            return;
        }
        
        const teamUsageData = await teamUsageResponse.json();
        const teamUsageMap = {};
        teamUsageData.team_usage.forEach(usage => {
            teamUsageMap[usage.team.id] = usage;
        });
        
        // Get team loser usage (NEW)
        const loserUsageResponse = await fetch(`${API_BASE}/api/picks/loser-usage?user_id=${currentUser.id}`);
        let loserUsageTeamIds = [];
        if (loserUsageResponse.ok) {
            const loserUsageData = await loserUsageResponse.json();
            loserUsageTeamIds = loserUsageData.loser_teams.map(team => team.id);
        }
        
        // Create HTML for matches
        let matchesHtml = '';
        
        if (matchesData.matches.length === 0) {
            matchesHtml = '<p>Keine Matches für diese Woche gefunden</p>';
        } else {
            // NEW RULE: Show info about one pick per week
            if (hasWeekPick) {
                matchesHtml += `
                    <div class="week-pick-info">
                        <h3>Dein Pick für Woche ${week}</h3>
                        <p>Du kannst deinen Pick zwischen allen noch nicht gestarteten Spielen wechseln.</p>
                    </div>
                `;
            } else {
                matchesHtml += `
                    <div class="week-pick-info">
                        <h3>Wähle EINEN Pick für Woche ${week}</h3>
                        <p>Du kannst nur ein Spiel pro Woche tippen. Wähle weise!</p>
                    </div>
                `;
            }
            
            matchesData.matches.forEach(match => {
                // Check if user has a pick for this match
                const userPick = picksData.picks.find(pick => pick.match.id === match.id);
                const selectedTeamId = userPick ? userPick.chosen_team.id : null;
                const isThisMatchPicked = selectedTeamId !== null;
                
                // NEW RULE: Only disable if game has started, allow pick changes between non-started games
                const isMatchDisabled = false; // Allow pick changes between all non-started games
                
                // NEW: Check if game has started (Backend provides this info)
                const isGameStarted = match.is_game_started;
                
                // Format date and time in Vienna timezone
                const matchDate = new Date(match.start_time_vienna);
                const dateOptions = { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    timeZone: 'Europe/Vienna'
                };
                
                const formattedDate = matchDate.toLocaleDateString('de-DE', dateOptions);
                
                // Check if teams are eliminated
                const homeTeamEliminated = eliminatedTeamIds.includes(match.home_team.id);
                const awayTeamEliminated = eliminatedTeamIds.includes(match.away_team.id);
                
                // NEW RULE: Check if teams have been used as losers
                const homeTeamUsedAsLoser = loserUsageTeamIds.includes(match.home_team.id);
                const awayTeamUsedAsLoser = loserUsageTeamIds.includes(match.away_team.id);
                
                // Get team usage status
                const awayTeamUsage = teamUsageMap[match.away_team.id];
                const homeTeamUsage = teamUsageMap[match.home_team.id];
                
                // Determine team status classes and titles
                const getTeamStatusInfo = (team, teamUsage, teamEliminated, teamUsedAsLoser, isOpposingTeam = false) => {
                    if (teamEliminated) {
                        return { class: 'eliminated', title: 'Dieses Team wurde bereits eliminiert', disabled: true };
                    }
                    if (teamUsage && teamUsage.usage_count >= 2) {
                        return { class: 'max-used', title: 'Dieses Team wurde bereits 2x als Gewinner gewählt (Maximum erreicht)', disabled: true };
                    }
                    // NEW RULE: If this team would be the loser (opposing team) and has been used as loser before
                    if (isOpposingTeam && teamUsedAsLoser) {
                        return { class: 'used-as-loser', title: 'Dieses Team wurde bereits als Verlierer getippt und kann nicht mehr als Verlierer gewählt werden', disabled: true };
                    }
                    // FIXED: Only show usage count for completed games
                    if (match.is_completed && teamUsage && teamUsage.usage_count === 1) {
                        return { class: 'used-once', title: 'Dieses Team wurde bereits 1x als Gewinner gewählt', disabled: false };
                    }
                    return { class: '', title: '', disabled: false };
                };
                
                // For away team selection, home team would be the loser
                const awayTeamStatus = getTeamStatusInfo(match.away_team, awayTeamUsage, awayTeamEliminated, awayTeamUsedAsLoser);
                const awayTeamOpposingStatus = getTeamStatusInfo(match.home_team, homeTeamUsage, homeTeamEliminated, homeTeamUsedAsLoser, true);
                
                // For home team selection, away team would be the loser  
                const homeTeamStatus = getTeamStatusInfo(match.home_team, homeTeamUsage, homeTeamEliminated, homeTeamUsedAsLoser);
                const homeTeamOpposingStatus = getTeamStatusInfo(match.away_team, awayTeamUsage, awayTeamEliminated, awayTeamUsedAsLoser, true);
                
                // Determine if teams can be selected
                const awayTeamDisabled = isMatchDisabled || awayTeamStatus.disabled || awayTeamOpposingStatus.disabled || isGameStarted;
                const homeTeamDisabled = isMatchDisabled || homeTeamStatus.disabled || homeTeamOpposingStatus.disabled || isGameStarted;
                
                matchesHtml += `
                    <div class="match-card ${isMatchDisabled ? 'match-disabled' : ''} ${isGameStarted ? 'game-started' : ''}" data-match-id="${match.id}">
                        <div class="match-header">
                            <div class="match-date">${formattedDate}</div>
                            ${isGameStarted ? '<div class="game-started-info">Spiel bereits gestartet</div>' : ''}
                        </div>
                        <div class="match-teams">
                            <div class="match-team ${awayTeamStatus.class} ${selectedTeamId === match.away_team.id ? 'selected' : ''} ${awayTeamDisabled ? 'disabled' : ''}"
                                 data-team-id="${match.away_team.id}"
                                 data-match-id="${match.id}"
                                 data-team-name="${match.away_team.name}"
                                 data-disabled="${awayTeamDisabled}"
                                 ${awayTeamStatus.title || awayTeamOpposingStatus.title ? `title="${awayTeamStatus.title || awayTeamOpposingStatus.title}"` : ''}>
                                <img src="${match.away_team.logo_url}" alt="${match.away_team.name}" class="match-team-logo team-logo-large">
                                <div class="match-team-name">${match.away_team.name}</div>
                                ${awayTeamUsedAsLoser ? '<div class="loser-indicator">L</div>' : ''}
                                ${selectedTeamId === match.away_team.id ? '<div class="pick-indicator"><i class="fas fa-check"></i></div>' : ''}
                                ${match.is_completed && match.winner_team && match.winner_team.id === match.away_team.id ? '<div class="winner-indicator"><i class="fas fa-trophy"></i></div>' : ''}
                                ${match.is_completed && awayTeamUsage && awayTeamUsage.usage_count > 0 ? `<div class="usage-indicator">${awayTeamUsage.usage_count}x</div>` : ''}
                            </div>
                            
                            <div class="match-vs">
                                @
                            </div>
                            
                            <div class="match-team ${homeTeamStatus.class} ${selectedTeamId === match.home_team.id ? 'selected' : ''} ${homeTeamDisabled ? 'disabled' : ''}"
                                 data-team-id="${match.home_team.id}"
                                 data-match-id="${match.id}"
                                 data-team-name="${match.home_team.name}"
                                 data-disabled="${homeTeamDisabled}"
                                 ${homeTeamStatus.title || homeTeamOpposingStatus.title ? `title="${homeTeamStatus.title || homeTeamOpposingStatus.title}"` : ''}>
                                <img src="${match.home_team.logo_url}" alt="${match.home_team.name}" class="match-team-logo team-logo-large">
                                <div class="match-team-name">${match.home_team.name}</div>
                                ${homeTeamUsedAsLoser ? '<div class="loser-indicator">L</div>' : ''}
                                ${selectedTeamId === match.home_team.id ? '<div class="pick-indicator"><i class="fas fa-check"></i></div>' : ''}
                                ${match.is_completed && match.winner_team && match.winner_team.id === match.home_team.id ? '<div class="winner-indicator"><i class="fas fa-trophy"></i></div>' : ''}
                                ${match.is_completed && homeTeamUsage && homeTeamUsage.usage_count > 0 ? `<div class="usage-indicator">${homeTeamUsage.usage_count}x</div>` : ''}
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
    const teamBoxes = document.querySelectorAll('.match-team');
    
    teamBoxes.forEach(box => {
        box.addEventListener('click', function() {
            // NEW RULE: Check if team is disabled
            const isDisabled = this.dataset.disabled === 'true' || this.classList.contains('disabled');
            
            if (isDisabled) {
                // Show tooltip or warning for disabled teams
                const title = this.getAttribute('title');
                if (title) {
                    showToast('warning', title);
                }
                return;
            }
            
            const matchId = this.dataset.matchId;
            const teamId = this.dataset.teamId;
            const teamName = this.dataset.teamName;
            
            selectMatchWinner(matchId, teamId, teamName);
        });
    });
}

// Select match winner
async function selectMatchWinner(matchId, teamId, teamName) {
    if (!currentUser) {
        showToast('warning', 'Bitte logge dich ein, um Picks zu machen');
        return;
    }
    
    if (confirm(`${teamName} als Gewinner auswählen?`)) {
        try {
            showLoading();
            
            const response = await fetch(`${API_BASE}/api/picks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    match_id: parseInt(matchId),
                    chosen_team_id: parseInt(teamId)
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast('success', 'Pick gespeichert');
                
                // Reload matches to update UI
                const weekSelect = document.getElementById('week-select');
                loadMatchesForWeek(weekSelect.value);
                
                // Reload dashboard data
                loadDashboardData();
            } else {
                showToast('error', data.error || 'Fehler beim Speichern des Picks');
            }
        } catch (error) {
            console.error('Error selecting match winner:', error);
            showToast('error', 'Ein Fehler ist aufgetreten');
        } finally {
            hideLoading();
        }
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
            
            // Calculate proper rankings with ties
            let currentRank = 1;
            let previousScore = null;
            
            data.leaderboard.forEach((player, index) => {
                // If this player has a different score than the previous, update rank
                if (previousScore !== null && player.score !== previousScore) {
                    currentRank = index + 1;
                }
                
                leaderboardHtml += `
                    <tr>
                        <td class="leaderboard-rank">${currentRank}</td>
                        <td>${player.username} ${player.emoji ? `<span class="leaderboard-emoji">${player.emoji}</span>` : ''}</td>
                        <td>${player.score}</td>
                    </tr>
                `;
                
                previousScore = player.score;
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
            document.getElementById('all-picks-container').innerHTML = 'Fehler beim Laden der Spieler';
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
        let allPicksHtml = '';
        
        // Check privacy setting
        const hideCurrentPicks = document.getElementById('hide-current-picks').checked;
        const currentWeek = 2; // Current active week
        
        // Sort weeks in descending order
        const weeks = Object.keys(matchesByWeek).sort((a, b) => b - a);
        
        for (const week of weeks) {
            const weekNum = parseInt(week);
            const isCurrentWeek = weekNum === currentWeek;
            const weekCompleted = matchesByWeek[week].every(match => match.is_completed);
            
            // Skip current week if privacy is enabled and week is not completed
            if (hideCurrentPicks && isCurrentWeek && !weekCompleted) {
                allPicksHtml += `
                    <div class="all-picks-week">
                        <h3>Woche ${week}</h3>
                        <div class="privacy-notice">
                            <i class="fas fa-eye-slash"></i>
                            Picks werden erst nach Abschluss der Woche angezeigt
                        </div>
                    </div>
                `;
                continue;
            }
            
            allPicksHtml += `
                <div class="all-picks-week">
                    <h3>Woche ${week}</h3>
                    <table class="all-picks-table">
                        <thead>
                            <tr>
                                <th>Spieler</th>
                                <th>Pick</th>
                                <th>Ergebnis</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            for (const user of users) {
                const userPicks = allPicks[user.id] || [];
                const weekPicks = userPicks.filter(pick => pick.match.week === parseInt(week));
                
                if (weekPicks.length > 0) {
                    const pick = weekPicks[0];
                    let resultText = 'Ausstehend';
                    let resultClass = 'pending';
                    
                    if (pick.match.is_completed) {
                        if (pick.is_correct) {
                            resultText = 'Richtig';
                            resultClass = 'correct';
                        } else {
                            resultText = 'Falsch';
                            resultClass = 'incorrect';
                        }
                    }
                    
                    allPicksHtml += `
                        <tr>
                            <td>${user.username}</td>
                            <td>
                                <img src="${pick.chosen_team.logo_url}" alt="${pick.chosen_team.name}" class="all-picks-logo team-logo-small">
                                ${pick.chosen_team.name}
                            </td>
                            <td class="${resultClass}">${resultText}</td>
                        </tr>
                    `;
                } else {
                    allPicksHtml += `
                        <tr>
                            <td>${user.username}</td>
                            <td>Kein Pick</td>
                            <td>-</td>
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
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle toast-icon"></i>';
            break;
        case 'info':
            icon = '<i class="fas fa-info-circle toast-icon"></i>';
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

// Add event listener for privacy toggle
document.addEventListener('DOMContentLoaded', function() {
    const hideCurrentPicksToggle = document.getElementById('hide-current-picks');
    if (hideCurrentPicksToggle) {
        hideCurrentPicksToggle.addEventListener('change', function() {
            // Reload all picks when toggle changes
            if (document.getElementById('all-picks-section').style.display !== 'none') {
                loadAllPicksData();
            }
        });
    }
});

