from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import os
import json
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

app = Flask(__name__, static_folder='static')
CORS(app)
app.secret_key = 'nfl_pickem_secret_key'

# Initialize database
DB_FILE = os.path.join(os.path.dirname(__file__), 'db.json')

def init_db():
    if not os.path.exists(DB_FILE):
        db = {
            'users': [
                {'id': 1, 'username': 'Manuel', 'password': generate_password_hash('Manuel1'), 'is_admin': True},
                {'id': 2, 'username': 'Daniel', 'password': generate_password_hash('Daniel1'), 'is_admin': False},
                {'id': 3, 'username': 'Raff', 'password': generate_password_hash('Raff1'), 'is_admin': False},
                {'id': 4, 'username': 'Haunschi', 'password': generate_password_hash('Haunschi1'), 'is_admin': False}
            ],
            'teams': [
                {'id': 1, 'name': 'Arizona Cardinals', 'abbreviation': 'ARI', 'logo_url': '/static/logos/arizona-cardinals.png'},
                {'id': 2, 'name': 'Atlanta Falcons', 'abbreviation': 'ATL', 'logo_url': '/static/logos/atlanta-falcons.png'},
                {'id': 3, 'name': 'Baltimore Ravens', 'abbreviation': 'BAL', 'logo_url': '/static/logos/baltimore-ravens.png'},
                {'id': 4, 'name': 'Buffalo Bills', 'abbreviation': 'BUF', 'logo_url': '/static/logos/buffalo-bills.png'},
                {'id': 5, 'name': 'Carolina Panthers', 'abbreviation': 'CAR', 'logo_url': '/static/logos/carolina-panthers.png'},
                {'id': 6, 'name': 'Chicago Bears', 'abbreviation': 'CHI', 'logo_url': '/static/logos/chicago-bears.png'},
                {'id': 7, 'name': 'Cincinnati Bengals', 'abbreviation': 'CIN', 'logo_url': '/static/logos/cincinnati-bengals.png'},
                {'id': 8, 'name': 'Cleveland Browns', 'abbreviation': 'CLE', 'logo_url': '/static/logos/cleveland-browns.png'},
                {'id': 9, 'name': 'Dallas Cowboys', 'abbreviation': 'DAL', 'logo_url': '/static/logos/dallas-cowboys.png'},
                {'id': 10, 'name': 'Denver Broncos', 'abbreviation': 'DEN', 'logo_url': '/static/logos/denver-broncos.png'},
                {'id': 11, 'name': 'Detroit Lions', 'abbreviation': 'DET', 'logo_url': '/static/logos/detroit-lions.png'},
                {'id': 12, 'name': 'Green Bay Packers', 'abbreviation': 'GB', 'logo_url': '/static/logos/green-bay-packers.png'},
                {'id': 13, 'name': 'Houston Texans', 'abbreviation': 'HOU', 'logo_url': '/static/logos/houston-texans.png'},
                {'id': 14, 'name': 'Indianapolis Colts', 'abbreviation': 'IND', 'logo_url': '/static/logos/indianapolis-colts.png'},
                {'id': 15, 'name': 'Jacksonville Jaguars', 'abbreviation': 'JAX', 'logo_url': '/static/logos/jacksonville-jaguars.png'},
                {'id': 16, 'name': 'Kansas City Chiefs', 'abbreviation': 'KC', 'logo_url': '/static/logos/kansas-city-chiefs.png'},
                {'id': 17, 'name': 'Las Vegas Raiders', 'abbreviation': 'LV', 'logo_url': '/static/logos/las-vegas-raiders.png'},
                {'id': 18, 'name': 'Los Angeles Chargers', 'abbreviation': 'LAC', 'logo_url': '/static/logos/los-angeles-chargers.png'},
                {'id': 19, 'name': 'Los Angeles Rams', 'abbreviation': 'LAR', 'logo_url': '/static/logos/los-angeles-rams.png'},
                {'id': 20, 'name': 'Miami Dolphins', 'abbreviation': 'MIA', 'logo_url': '/static/logos/miami-dolphins.png'},
                {'id': 21, 'name': 'Minnesota Vikings', 'abbreviation': 'MIN', 'logo_url': '/static/logos/minnesota-vikings.png'},
                {'id': 22, 'name': 'New England Patriots', 'abbreviation': 'NE', 'logo_url': '/static/logos/new-england-patriots.png'},
                {'id': 23, 'name': 'New Orleans Saints', 'abbreviation': 'NO', 'logo_url': '/static/logos/new-orleans-saints.png'},
                {'id': 24, 'name': 'New York Giants', 'abbreviation': 'NYG', 'logo_url': '/static/logos/new-york-giants.png'},
                {'id': 25, 'name': 'New York Jets', 'abbreviation': 'NYJ', 'logo_url': '/static/logos/new-york-jets.png'},
                {'id': 26, 'name': 'Philadelphia Eagles', 'abbreviation': 'PHI', 'logo_url': '/static/logos/philadelphia-eagles.png'},
                {'id': 27, 'name': 'Pittsburgh Steelers', 'abbreviation': 'PIT', 'logo_url': '/static/logos/pittsburgh-steelers.png'},
                {'id': 28, 'name': 'San Francisco 49ers', 'abbreviation': 'SF', 'logo_url': '/static/logos/san-francisco-49ers.png'},
                {'id': 29, 'name': 'Seattle Seahawks', 'abbreviation': 'SEA', 'logo_url': '/static/logos/seattle-seahawks.png'},
                {'id': 30, 'name': 'Tampa Bay Buccaneers', 'abbreviation': 'TB', 'logo_url': '/static/logos/tampa-bay-buccaneers.png'},
                {'id': 31, 'name': 'Tennessee Titans', 'abbreviation': 'TEN', 'logo_url': '/static/logos/tennessee-titans.png'},
                {'id': 32, 'name': 'Washington Commanders', 'abbreviation': 'WAS', 'logo_url': '/static/logos/washington-commanders.png'}
            ],
            'matches': [
                # Week 1 (already completed)
                {'id': 1, 'week': 1, 'home_team_id': 16, 'away_team_id': 3, 'start_time': '2025-09-04T20:20:00', 'is_completed': True, 'winner_team_id': 16},
                {'id': 2, 'week': 1, 'home_team_id': 8, 'away_team_id': 7, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 7},
                {'id': 3, 'week': 1, 'home_team_id': 30, 'away_team_id': 2, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 30},
                {'id': 4, 'week': 1, 'home_team_id': 24, 'away_team_id': 32, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 32},
                {'id': 5, 'week': 1, 'home_team_id': 14, 'away_team_id': 13, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 14},
                {'id': 6, 'week': 1, 'home_team_id': 20, 'away_team_id': 15, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 20},
                {'id': 7, 'week': 1, 'home_team_id': 23, 'away_team_id': 5, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 23},
                {'id': 8, 'week': 1, 'home_team_id': 31, 'away_team_id': 10, 'start_time': '2025-09-07T13:00:00', 'is_completed': True, 'winner_team_id': 10},
                {'id': 9, 'week': 1, 'home_team_id': 8, 'away_team_id': 9, 'start_time': '2025-09-07T16:25:00', 'is_completed': True, 'winner_team_id': 9},
                {'id': 10, 'week': 1, 'home_team_id': 29, 'away_team_id': 17, 'start_time': '2025-09-07T16:25:00', 'is_completed': True, 'winner_team_id': 29},
                {'id': 11, 'week': 1, 'home_team_id': 18, 'away_team_id': 17, 'start_time': '2025-09-07T16:25:00', 'is_completed': True, 'winner_team_id': 18},
                {'id': 12, 'week': 1, 'home_team_id': 21, 'away_team_id': 28, 'start_time': '2025-09-07T16:25:00', 'is_completed': True, 'winner_team_id': 28},
                {'id': 13, 'week': 1, 'home_team_id': 26, 'away_team_id': 12, 'start_time': '2025-09-07T20:20:00', 'is_completed': True, 'winner_team_id': 26},
                {'id': 14, 'week': 1, 'home_team_id': 25, 'away_team_id': 4, 'start_time': '2025-09-08T20:15:00', 'is_completed': True, 'winner_team_id': 4},
                {'id': 15, 'week': 1, 'home_team_id': 28, 'away_team_id': 19, 'start_time': '2025-09-08T20:15:00', 'is_completed': True, 'winner_team_id': 28},
                {'id': 16, 'week': 1, 'home_team_id': 24, 'away_team_id': 11, 'start_time': '2025-09-09T20:15:00', 'is_completed': True, 'winner_team_id': 11},
                
                # Week 2 (current week)
                {'id': 17, 'week': 2, 'home_team_id': 12, 'away_team_id': 32, 'start_time': '2025-09-12T20:15:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 18, 'week': 2, 'home_team_id': 7, 'away_team_id': 15, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 19, 'week': 2, 'home_team_id': 9, 'away_team_id': 24, 'start_time': '2025-09-14T16:25:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 20, 'week': 2, 'home_team_id': 11, 'away_team_id': 6, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 21, 'week': 2, 'home_team_id': 31, 'away_team_id': 19, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 22, 'week': 2, 'home_team_id': 20, 'away_team_id': 22, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 23, 'week': 2, 'home_team_id': 23, 'away_team_id': 28, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 24, 'week': 2, 'home_team_id': 25, 'away_team_id': 4, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 25, 'week': 2, 'home_team_id': 27, 'away_team_id': 29, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 26, 'week': 2, 'home_team_id': 14, 'away_team_id': 10, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 27, 'week': 2, 'home_team_id': 3, 'away_team_id': 8, 'start_time': '2025-09-14T13:00:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 28, 'week': 2, 'home_team_id': 1, 'away_team_id': 5, 'start_time': '2025-09-14T16:05:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 29, 'week': 2, 'home_team_id': 16, 'away_team_id': 26, 'start_time': '2025-09-14T16:25:00', 'is_completed': False, 'winner_team_id': None},
                {'id': 30, 'week': 2, 'home_team_id': 21, 'away_team_id': 2, 'start_time': '2025-09-14T16:25:00', 'is_completed': False, 'winner_team_id': None}
            ],
            'picks': [
                # Week 1 picks (already completed)
                {'id': 1, 'user_id': 1, 'match_id': 3, 'chosen_team_id': 2, 'is_correct': False},  # Manuel picked Falcons over Buccaneers (wrong)
                {'id': 2, 'user_id': 2, 'match_id': 8, 'chosen_team_id': 10, 'is_correct': True},  # Daniel picked Broncos over Titans (correct)
                {'id': 3, 'user_id': 3, 'match_id': 2, 'chosen_team_id': 7, 'is_correct': True},   # Raff picked Bengals over Browns (correct)
                {'id': 4, 'user_id': 4, 'match_id': 4, 'chosen_team_id': 32, 'is_correct': True}   # Haunschi picked Commanders over Giants (correct)
            ],
            'eliminated_teams': [
                # Teams that users have already picked as losers
                {'id': 1, 'user_id': 1, 'team_id': 30},  # Manuel eliminated Buccaneers
                {'id': 2, 'user_id': 2, 'team_id': 31},  # Daniel eliminated Titans
                {'id': 3, 'user_id': 3, 'team_id': 8},   # Raff eliminated Browns
                {'id': 4, 'user_id': 4, 'team_id': 24}   # Haunschi eliminated Giants
            ]
        }
        
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)

def get_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

init_db()

# Helper functions
def get_user_by_id(user_id):
    db = get_db()
    for user in db['users']:
        if user['id'] == user_id:
            # Don't return the password hash
            return {k: v for k, v in user.items() if k != 'password'}
    return None

def get_user_by_username(username):
    db = get_db()
    for user in db['users']:
        if user['username'] == username:
            return user
    return None

def get_team_by_id(team_id):
    db = get_db()
    for team in db['teams']:
        if team['id'] == team_id:
            return team
    return None

def get_match_by_id(match_id):
    db = get_db()
    for match in db['matches']:
        if match['id'] == match_id:
            # Expand team references
            match_copy = match.copy()
            match_copy['home_team'] = get_team_by_id(match['home_team_id'])
            match_copy['away_team'] = get_team_by_id(match['away_team_id'])
            if match['winner_team_id']:
                match_copy['winner_team'] = get_team_by_id(match['winner_team_id'])
            else:
                match_copy['winner_team'] = None
            return match_copy
    return None

def get_matches_by_week(week):
    db = get_db()
    matches = []
    for match in db['matches']:
        if match['week'] == week:
            # Expand team references
            match_copy = match.copy()
            match_copy['home_team'] = get_team_by_id(match['home_team_id'])
            match_copy['away_team'] = get_team_by_id(match['away_team_id'])
            if match['winner_team_id']:
                match_copy['winner_team'] = get_team_by_id(match['winner_team_id'])
            else:
                match_copy['winner_team'] = None
            matches.append(match_copy)
    return matches

def get_picks_by_user_and_week(user_id, week):
    db = get_db()
    picks = []
    for pick in db['picks']:
        if pick['user_id'] == user_id:
            match = get_match_by_id(pick['match_id'])
            if match and match['week'] == week:
                # Expand references
                pick_copy = pick.copy()
                pick_copy['match'] = match
                pick_copy['chosen_team'] = get_team_by_id(pick['chosen_team_id'])
                picks.append(pick_copy)
    return picks

def get_picks_by_user(user_id):
    db = get_db()
    picks = []
    for pick in db['picks']:
        if pick['user_id'] == user_id:
            # Expand references
            pick_copy = pick.copy()
            pick_copy['match'] = get_match_by_id(pick['match_id'])
            pick_copy['chosen_team'] = get_team_by_id(pick['chosen_team_id'])
            picks.append(pick_copy)
    return picks

def get_eliminated_teams_by_user(user_id):
    db = get_db()
    eliminated_teams = []
    for eliminated in db['eliminated_teams']:
        if eliminated['user_id'] == user_id:
            eliminated_copy = eliminated.copy()
            eliminated_copy['team'] = get_team_by_id(eliminated['team_id'])
            eliminated_teams.append(eliminated_copy)
    return eliminated_teams

def get_user_score(user_id):
    picks = get_picks_by_user(user_id)
    return sum(1 for pick in picks if pick.get('is_correct', False))

def get_current_week():
    # In a real app, this would be determined by the current date
    # For now, we'll hardcode it to week 2
    return 2

def convert_to_vienna_time(utc_time_str):
    # Parse the UTC time string
    utc_time = datetime.datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
    
    # Define Vienna timezone
    vienna_tz = pytz.timezone('Europe/Vienna')
    
    # Convert UTC time to Vienna time
    vienna_time = utc_time.astimezone(vienna_tz)
    
    return vienna_time

def get_user_rank(user_id):
    db = get_db()
    users = db['users']
    
    # Calculate scores for all users
    scores = []
    for user in users:
        score = get_user_score(user['id'])
        scores.append({'user_id': user['id'], 'score': score})
    
    # Sort by score in descending order
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Find the rank of the specified user
    rank = 1
    prev_score = None
    for i, score_entry in enumerate(scores):
        if i > 0 and score_entry['score'] < prev_score:
            rank = i + 1
        
        if score_entry['user_id'] == user_id:
            return rank, len(users)
        
        prev_score = score_entry['score']
    
    return None, len(users)

# Routes
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = get_user_by_username(username)
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'is_admin': user.get('is_admin', False)
            }
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/auth/me')
def me():
    user_id = session.get('user_id')
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({'user': user})
    
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/teams')
def teams():
    db = get_db()
    return jsonify({'teams': db['teams']})

@app.route('/api/matches')
def matches():
    db = get_db()
    week = request.args.get('week')
    
    if week:
        try:
            week = int(week)
            matches = get_matches_by_week(week)
            
            # Convert match times to Vienna time
            for match in matches:
                vienna_time = convert_to_vienna_time(match['start_time'])
                match['start_time'] = vienna_time.isoformat()
            
            return jsonify({'matches': matches})
        except ValueError:
            return jsonify({'error': 'Invalid week parameter'}), 400
    
    # If no week specified, return all matches
    all_matches = []
    for match in db['matches']:
        match_copy = match.copy()
        match_copy['home_team'] = get_team_by_id(match['home_team_id'])
        match_copy['away_team'] = get_team_by_id(match['away_team_id'])
        if match['winner_team_id']:
            match_copy['winner_team'] = get_team_by_id(match['winner_team_id'])
        else:
            match_copy['winner_team'] = None
        
        # Convert match time to Vienna time
        vienna_time = convert_to_vienna_time(match['start_time'])
        match_copy['start_time'] = vienna_time.isoformat()
        
        all_matches.append(match_copy)
    
    return jsonify({'matches': all_matches})

@app.route('/api/picks', methods=['GET', 'POST'])
def picks():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        week = request.args.get('week')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        try:
            user_id = int(user_id)
            
            if week:
                try:
                    week = int(week)
                    picks = get_picks_by_user_and_week(user_id, week)
                    return jsonify({'picks': picks})
                except ValueError:
                    return jsonify({'error': 'Invalid week parameter'}), 400
            else:
                picks = get_picks_by_user(user_id)
                return jsonify({'picks': picks})
        except ValueError:
            return jsonify({'error': 'Invalid user ID'}), 400
    
    elif request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.json
        match_id = data.get('match_id')
        chosen_team_id = data.get('chosen_team_id')
        
        if not match_id or not chosen_team_id:
            return jsonify({'error': 'Match ID and chosen team ID are required'}), 400
        
        # Get the match
        match = get_match_by_id(match_id)
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        
        # Check if the match has already started
        match_time = datetime.datetime.fromisoformat(match['start_time'].replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        
        if match_time < now:
            return jsonify({'error': 'Cannot pick for a match that has already started'}), 400
        
        # Check if the chosen team is valid for this match
        if chosen_team_id != match['home_team']['id'] and chosen_team_id != match['away_team']['id']:
            return jsonify({'error': 'Chosen team is not playing in this match'}), 400
        
        # Check if the user has already picked for this match
        db = get_db()
        for pick in db['picks']:
            if pick['user_id'] == user_id and pick['match_id'] == match_id:
                # Update the existing pick
                pick['chosen_team_id'] = chosen_team_id
                save_db(db)
                return jsonify({'message': 'Pick updated successfully'})
        
        # Create a new pick
        new_pick = {
            'id': len(db['picks']) + 1,
            'user_id': user_id,
            'match_id': match_id,
            'chosen_team_id': chosen_team_id,
            'is_correct': None  # Will be determined when the match is completed
        }
        
        db['picks'].append(new_pick)
        save_db(db)
        
        return jsonify({'message': 'Pick created successfully'})

@app.route('/api/picks/score')
def picks_score():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        user_id = int(user_id)
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get the user's score
        score = get_user_score(user_id)
        
        # Get all other users' scores
        db = get_db()
        opponents = []
        
        for other_user in db['users']:
            if other_user['id'] != user_id:
                other_score = get_user_score(other_user['id'])
                opponents.append({
                    'id': other_user['id'],
                    'username': other_user['username'],
                    'score': other_score
                })
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'score': score
            },
            'opponents': opponents
        })
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

@app.route('/api/picks/recent')
def picks_recent():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        user_id = int(user_id)
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all picks for the user
        picks = get_picks_by_user(user_id)
        
        # Sort by week in descending order
        picks.sort(key=lambda x: x['match']['week'], reverse=True)
        
        # Format picks for response
        formatted_picks = []
        
        for pick in picks:
            formatted_pick = {
                'week': pick['match']['week'],
                'team': pick['chosen_team']['name'],
                'team_logo': pick['chosen_team']['logo_url'],
                'is_completed': pick['match']['is_completed'],
                'is_correct': pick.get('is_correct')
            }
            
            formatted_picks.append(formatted_pick)
        
        return jsonify({'picks': formatted_picks})
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

@app.route('/api/picks/eliminated')
def picks_eliminated():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        user_id = int(user_id)
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get eliminated teams for the user
        eliminated_teams = get_eliminated_teams_by_user(user_id)
        
        # Format eliminated teams for response
        formatted_teams = []
        
        for eliminated in eliminated_teams:
            formatted_team = {
                'id': eliminated['team']['id'],
                'name': eliminated['team']['name'],
                'logo_url': eliminated['team']['logo_url']
            }
            
            formatted_teams.append(formatted_team)
        
        return jsonify({'eliminated_teams': formatted_teams})
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

@app.route('/api/leaderboard')
def leaderboard():
    db = get_db()
    users = db['users']
    
    leaderboard = []
    
    for user in users:
        score = get_user_score(user['id'])
        leaderboard.append({
            'id': user['id'],
            'username': user['username'],
            'score': score,
            'emoji': None
        })
    
    # Sort by score in descending order
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    if len(leaderboard) > 1:
        # Check if first place is not tied
        if leaderboard[0]['score'] > leaderboard[1]['score']:
            leaderboard[0]['emoji'] = '💪'
        
        # Check if last place is not tied
        last_place = leaderboard[-1]
        second_last = leaderboard[-2]
        if last_place['score'] < second_last['score']:
            last_place['emoji'] = '💩'
    
    return jsonify({'leaderboard': leaderboard})

@app.route('/api/current-week')
def current_week():
    return jsonify({'current_week': get_current_week()})

@app.route('/api/user/rank')
def user_rank():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        user_id = int(user_id)
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        rank, total_users = get_user_rank(user_id)
        
        if rank is None:
            return jsonify({'error': 'User rank not found'}), 404
        
        return jsonify({
            'rank': rank,
            'total_users': total_users
        })
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400

# Catch-all route for SPA
@app.route('/<path:path>')
def catch_all(path):
    if path.startswith('api'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

