from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'nfl-pickem-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfl_pickem.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app, supports_credentials=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'score': self.get_score()
        }
    
    def get_score(self):
        score = 0
        for pick in Pick.query.filter_by(user_id=self.id).all():
            if pick.is_correct:
                score += 1
        return score

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    abbreviation = db.Column(db.String(10), nullable=False)
    logo_url = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'logo_url': self.logo_url
        }

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    winner_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    
    # New fields for ESPN integration
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    winner_team = db.relationship('Team', foreign_keys=[winner_team_id])
    
    # Helper properties for ESPN integration
    @property
    def home_team_name(self):
        return self.home_team.name if self.home_team else None
    
    @property
    def away_team_name(self):
        return self.away_team.name if self.away_team else None
    
    @property
    def winner(self):
        return self.winner_team.name if self.winner_team else None
    
    @property
    def is_game_started(self):
        """Check if the game has started (in Vienna timezone)"""
        from datetime import datetime
        import pytz
        
        vienna_tz = pytz.timezone('Europe/Vienna')
        now_vienna = datetime.now(vienna_tz)
        
        # Convert start_time to Vienna timezone if it's not already
        if self.start_time.tzinfo is None:
            # Assume UTC if no timezone info
            utc_tz = pytz.UTC
            start_time_utc = utc_tz.localize(self.start_time)
        else:
            start_time_utc = self.start_time
            
        start_time_vienna = start_time_utc.astimezone(vienna_tz)
        
        return now_vienna >= start_time_vienna
    
    @property
    def start_time_vienna(self):
        """Get start time in Vienna timezone"""
        import pytz
        
        vienna_tz = pytz.timezone('Europe/Vienna')
        
        if self.start_time.tzinfo is None:
            # Assume UTC if no timezone info
            utc_tz = pytz.UTC
            start_time_utc = utc_tz.localize(self.start_time)
        else:
            start_time_utc = self.start_time
            
        return start_time_utc.astimezone(vienna_tz)
    
    @winner.setter
    def winner(self, team_name):
        if team_name:
            team = Team.query.filter_by(name=team_name).first()
            if team:
                self.winner_team_id = team.id
                self.is_completed = True
                self.status = 'completed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'week': self.week,
            'home_team': self.home_team.to_dict(),
            'away_team': self.away_team.to_dict(),
            'start_time': self.start_time.isoformat(),
            'start_time_vienna': self.start_time_vienna.isoformat(),
            'is_completed': self.is_completed,
            'is_game_started': self.is_game_started,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'status': self.status,
            'winner': self.winner,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'winner_team': self.winner_team.to_dict() if self.winner_team_id else None
        }

class Pick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    chosen_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    
    user = db.relationship('User')
    match = db.relationship('Match')
    chosen_team = db.relationship('Team')
    
    @property
    def is_correct(self):
        if not self.match.is_completed:
            return False
        return self.chosen_team_id == self.match.winner_team_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'match': self.match.to_dict(),
            'chosen_team': self.chosen_team.to_dict(),
            'is_correct': self.is_correct
        }

class EliminatedTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    
    user = db.relationship('User')
    team = db.relationship('Team')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'team': self.team.to_dict()
        }

class TeamWinnerUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    usage_count = db.Column(db.Integer, default=0)
    
    user = db.relationship('User')
    team = db.relationship('Team')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'team': self.team.to_dict(),
            'usage_count': self.usage_count
        }

class TeamLoserUsage(db.Model):
    """Tracks teams that have been picked as losers (automatically when picking a winner)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)  # Track which week this happened
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)  # Track the specific match
    
    user = db.relationship('User')
    team = db.relationship('Team')
    match = db.relationship('Match')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'team': self.team.to_dict(),
            'week': self.week,
            'match': self.match.to_dict()
        }

# API Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error in login: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def logout():
    try:
        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        teams = Team.query.all()
        return jsonify({
            'teams': [team.to_dict() for team in teams]
        }), 200
    except Exception as e:
        print(f"Error in get_teams: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        week = request.args.get('week', type=int)
        
        if week:
            matches = Match.query.filter_by(week=week).all()
        else:
            matches = Match.query.all()
            
        return jsonify({
            'matches': [match.to_dict() for match in matches]
        }), 200
    except Exception as e:
        print(f"Error in get_matches: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/current-week', methods=['GET'])
def get_current_week():
    try:
        # For simplicity, we'll return week 2 as the current week
        return jsonify({
            'current_week': 2
        }), 200
    except Exception as e:
        print(f"Error in get_current_week: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks', methods=['GET', 'POST'])
def handle_picks():
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id', type=int)
            week = request.args.get('week', type=int)
            
            if not user_id:
                return jsonify({'error': 'User ID required'}), 400
                
            query = Pick.query.filter_by(user_id=user_id)
            
            if week:
                # Join with Match to filter by week
                picks = query.join(Match).filter(Match.week == week).all()
            else:
                picks = query.all()
                
            return jsonify({
                'picks': [pick.to_dict() for pick in picks]
            }), 200
        
        elif request.method == 'POST':
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Not authenticated'}), 401
                
            data = request.get_json()
            match_id = data.get('match_id')
            chosen_team_id = data.get('chosen_team_id')
            
            if not match_id or not chosen_team_id:
                return jsonify({'error': 'Match ID and chosen team ID required'}), 400
                
            # Check if match exists
            match = Match.query.get(match_id)
            if not match:
                return jsonify({'error': 'Match not found'}), 404
            
            # Check if game has already started (Backend validation)
            if match.is_game_started:
                return jsonify({'error': 'Game has already started. Picks are no longer allowed.'}), 400
                
            # Check if team exists
            team = Team.query.get(chosen_team_id)
            if not team:
                return jsonify({'error': 'Team not found'}), 404
                
            # Check if match is completed
            if match.is_completed:
                return jsonify({'error': 'Cannot pick for completed match'}), 400
                
            # Check if team is part of the match
            if team.id != match.home_team_id and team.id != match.away_team_id:
                return jsonify({'error': 'Team is not part of this match'}), 400
                
            # NEW RULE: Check if user already has a pick for this WEEK (only one pick per week allowed)
            existing_week_pick = Pick.query.join(Match).filter(
                Pick.user_id == user_id,
                Match.week == match.week
            ).first()
            
            if existing_week_pick and existing_week_pick.match_id != match_id:
                return jsonify({'error': f'You already have a pick for week {match.week}. Only one pick per week is allowed.'}), 400
                
            # Check if chosen team is eliminated for this user
            eliminated = EliminatedTeam.query.filter_by(user_id=user_id, team_id=team.id).first()
            if eliminated:
                return jsonify({'error': 'Team is already eliminated for this user'}), 400
                
            # Check team winner usage limit (max 2 times per season)
            team_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=team.id).first()
            if team_usage and team_usage.usage_count >= 2:
                return jsonify({'error': 'Team has already been picked as winner 2 times this season'}), 400
                
            # NEW RULE: Check if the opposing team has been picked as loser before
            opposing_team_id = match.away_team_id if team.id == match.home_team_id else match.home_team_id
            loser_usage = TeamLoserUsage.query.filter_by(user_id=user_id, team_id=opposing_team_id).first()
            if loser_usage:
                opposing_team = Team.query.get(opposing_team_id)
                return jsonify({'error': f'{opposing_team.name} has already been picked as loser this season and cannot be picked as loser again'}), 400
            if team.id != match.home_team_id and team.id != match.away_team_id:
                return jsonify({'error': 'Team is not part of this match'}), 400
                
            # Check if user already has a pick for this match (for updates)
            existing_pick = Pick.query.filter_by(user_id=user_id, match_id=match_id).first()
            
            if existing_pick:
                # Update existing pick
                old_team_id = existing_pick.chosen_team_id
                old_opposing_team_id = match.away_team_id if old_team_id == match.home_team_id else match.home_team_id
                
                # If changing pick, we need to update usage counts
                if old_team_id != chosen_team_id:
                    # Remove old winner usage
                    old_team_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=old_team_id).first()
                    if old_team_usage and old_team_usage.usage_count > 0:
                        old_team_usage.usage_count -= 1
                        if old_team_usage.usage_count == 0:
                            db.session.delete(old_team_usage)
                    
                    # Remove old loser usage
                    old_loser_usage = TeamLoserUsage.query.filter_by(user_id=user_id, team_id=old_opposing_team_id, match_id=match_id).first()
                    if old_loser_usage:
                        db.session.delete(old_loser_usage)
                        
                        # Remove old elimination (if it was only from this loser usage)
                        remaining_loser_usage = TeamLoserUsage.query.filter_by(user_id=user_id, team_id=old_opposing_team_id).count()
                        if remaining_loser_usage == 0:  # No other loser usages
                            old_elimination = EliminatedTeam.query.filter_by(user_id=user_id, team_id=old_opposing_team_id).first()
                            if old_elimination:
                                db.session.delete(old_elimination)
                    
                    # Add new winner usage
                    new_team_usage = TeamWinnerUsage.query.filter_by(user_id=user_id, team_id=chosen_team_id).first()
                    if new_team_usage:
                        new_team_usage.usage_count += 1
                    else:
                        new_team_usage = TeamWinnerUsage(user_id=user_id, team_id=chosen_team_id, usage_count=1)
                        db.session.add(new_team_usage)
                    
                    # Add new loser usage (automatically when picking winner)
                    new_opposing_team_id = match.away_team_id if chosen_team_id == match.home_team_id else match.home_team_id
                    new_loser_usage = TeamLoserUsage(
                        user_id=user_id, 
                        team_id=new_opposing_team_id, 
                        week=match.week,
                        match_id=match_id
                    )
                    db.session.add(new_loser_usage)
                    
                    # ELIMINATE NEW OPPOSING TEAM: New opposing team is eliminated (1x as loser)
                    existing_new_elimination = EliminatedTeam.query.filter_by(user_id=user_id, team_id=new_opposing_team_id).first()
                    if not existing_new_elimination:
                        new_elimination = EliminatedTeam(user_id=user_id, team_id=new_opposing_team_id)
                        db.session.add(new_elimination)
                    
                    # Check if new chosen team should be eliminated (2x as winner)
                    if new_team_usage and new_team_usage.usage_count >= 2:
                        existing_chosen_elimination = EliminatedTeam.query.filter_by(user_id=user_id, team_id=chosen_team_id).first()
                        if not existing_chosen_elimination:
                            chosen_elimination = EliminatedTeam(user_id=user_id, team_id=chosen_team_id)
                            db.session.add(chosen_elimination)
                
                # Update existing pick
                existing_pick.chosen_team_id = chosen_team_id
                db.session.commit()
                return jsonify({
                    'message': 'Pick updated successfully',
                    'pick': existing_pick.to_dict()
                }), 200
            else:
                # Create new pick
                pick = Pick(user_id=user_id, match_id=match_id, chosen_team_id=chosen_team_id)
                db.session.add(pick)
                
                # Update team winner usage count
                if team_usage:
                    team_usage.usage_count += 1
                else:
                    team_usage = TeamWinnerUsage(user_id=user_id, team_id=chosen_team_id, usage_count=1)
                    db.session.add(team_usage)
                
                # NEW RULE: Automatically add loser usage for opposing team
                opposing_team_id = match.away_team_id if chosen_team_id == match.home_team_id else match.home_team_id
                loser_usage = TeamLoserUsage(
                    user_id=user_id, 
                    team_id=opposing_team_id, 
                    week=match.week,
                    match_id=match_id
                )
                db.session.add(loser_usage)
                
                # ELIMINATE TEAM: Opposing team is eliminated (1x as loser)
                existing_elimination = EliminatedTeam.query.filter_by(user_id=user_id, team_id=opposing_team_id).first()
                if not existing_elimination:
                    elimination = EliminatedTeam(user_id=user_id, team_id=opposing_team_id)
                    db.session.add(elimination)
                
                # Check if chosen team should be eliminated (2x as winner)
                if team_usage and team_usage.usage_count >= 2:
                    existing_chosen_elimination = EliminatedTeam.query.filter_by(user_id=user_id, team_id=chosen_team_id).first()
                    if not existing_chosen_elimination:
                        chosen_elimination = EliminatedTeam(user_id=user_id, team_id=chosen_team_id)
                        db.session.add(chosen_elimination)
                
                db.session.commit()
                return jsonify({
                    'message': 'Pick created successfully',
                    'pick': pick.to_dict()
                }), 201
    except Exception as e:
        print(f"Error in handle_picks: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks/score', methods=['GET'])
def get_user_scores():
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
            
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get all other users
        other_users = User.query.filter(User.id != user_id).all()
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'score': user.get_score()
            },
            'opponents': [
                {
                    'id': other_user.id,
                    'username': other_user.username,
                    'score': other_user.get_score()
                }
                for other_user in other_users
            ]
        }), 200
    except Exception as e:
        print(f"Error in get_user_scores: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks/recent', methods=['GET'])
def get_recent_picks():
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
            
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get recent picks (last 2 weeks)
        recent_picks = []
        
        # Get current week
        current_week = 2  # Hardcoded for simplicity
        
        # Get picks for current week and previous week
        for week in range(current_week, 0, -1):
            picks = Pick.query.join(Match).filter(
                Pick.user_id == user_id,
                Match.week == week
            ).all()
            
            for pick in picks:
                recent_picks.append({
                    'week': pick.match.week,
                    'team': pick.chosen_team.name,
                    'team_logo': pick.chosen_team.logo_url,
                    'is_completed': pick.match.is_completed,
                    'is_correct': pick.is_correct
                })
        
        return jsonify({
            'picks': recent_picks
        }), 200
    except Exception as e:
        print(f"Error in get_recent_picks: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks/eliminated', methods=['GET'])
def get_eliminated_teams():
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
            
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get eliminated teams
        eliminated_teams = EliminatedTeam.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'eliminated_teams': [team.team.to_dict() for team in eliminated_teams]
        }), 200
    except Exception as e:
        print(f"Error in get_eliminated_teams: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks/team-usage', methods=['GET'])
def get_team_winner_usage():
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
            
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get team winner usage
        team_usage = TeamWinnerUsage.query.filter_by(user_id=user_id).all()
        
        # Create a dictionary for easy lookup
        usage_dict = {}
        for usage in team_usage:
            usage_dict[usage.team_id] = usage.usage_count
            
        # Get all teams and add usage count
        all_teams = Team.query.all()
        team_status = []
        
        for team in all_teams:
            usage_count = usage_dict.get(team.id, 0)
            status = 'available'
            
            if usage_count >= 2:
                status = 'max_used'
            elif usage_count == 1:
                status = 'used_once'
                
            team_status.append({
                'team': team.to_dict(),
                'usage_count': usage_count,
                'status': status
            })
        
        return jsonify({
            'team_usage': team_status
        }), 200
    except Exception as e:
        print(f"Error in get_team_winner_usage: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/picks/loser-usage', methods=['GET'])
def get_team_loser_usage():
    """Get teams that have been used as losers by a user"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
            
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get teams used as losers
        loser_usage = TeamLoserUsage.query.filter_by(user_id=user_id).all()
        
        loser_teams = []
        for usage in loser_usage:
            loser_teams.append(usage.team.to_dict())
        
        return jsonify({
            'loser_teams': loser_teams
        }), 200
    except Exception as e:
        print(f"Error in get_team_loser_usage: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        users = User.query.all()
        
        # Calculate scores and sort by score (descending)
        leaderboard = []
        for user in users:
            score = user.get_score()
            leaderboard.append({
                'id': user.id,
                'username': user.username,
                'score': score
            })
            
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Add emojis for first and last place (if not tied)
        if len(leaderboard) > 1:
            # Check if first place is not tied
            if leaderboard[0]['score'] > leaderboard[1]['score']:
                leaderboard[0]['emoji'] = '💪'
                
            # Check if last place is not tied
            if leaderboard[-1]['score'] < leaderboard[-2]['score']:
                leaderboard[-1]['emoji'] = '💩'
        
        return jsonify({
            'leaderboard': leaderboard
        }), 200
    except Exception as e:
        print(f"Error in get_leaderboard: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Get user rank
@app.route('/api/user/rank', methods=['GET'])
def get_user_rank():
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
            
        # Get all users and calculate scores
        users = User.query.all()
        
        # Calculate scores and sort by score (descending)
        leaderboard = []
        for user in users:
            score = user.get_score()
            leaderboard.append({
                'id': user.id,
                'username': user.username,
                'score': score
            })
            
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Find the user's rank (handle ties correctly)
        user_rank = None
        current_rank = 1
        for i, user in enumerate(leaderboard):
            # If this user has a lower score than the previous user, update rank
            if i > 0 and leaderboard[i]['score'] < leaderboard[i-1]['score']:
                current_rank = i + 1
            
            if user['id'] == int(user_id):
                user_rank = current_rank
                break
                
        if user_rank is None:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'rank': user_rank
        }), 200
    except Exception as e:
        print(f"Error in get_user_rank: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Scheduler API endpoints
@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get current scheduler status"""
    try:
        # Get current week info
        current_week = 2  # This could be dynamic
        
        # Get completed matches count
        completed_matches = Match.query.filter_by(status='completed').count()
        total_matches = Match.query.count()
        
        return jsonify({
            'status': 'running',
            'current_week': current_week,
            'completed_matches': completed_matches,
            'total_matches': total_matches,
            'last_update': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Error in get_scheduler_status: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/scheduler/manual-update', methods=['POST'])
def manual_update():
    """Manually trigger an update for a specific week"""
    try:
        data = request.get_json()
        week = data.get('week', 2)
        
        # Import and run the ESPN integration
        from espn_integration import ESPNIntegration
        espn = ESPNIntegration()
        
        success = espn.process_weekly_update(week)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Week {week} updated successfully',
                'week': week
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Week {week} update failed or not completed',
                'week': week
            }), 400
            
    except Exception as e:
        print(f"Error in manual_update: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/matches/results', methods=['GET'])
def get_match_results():
    """Get match results with scores"""
    try:
        week = request.args.get('week', type=int)
        
        query = Match.query
        if week:
            query = query.filter_by(week=week)
        
        matches = query.filter_by(status='completed').all()
        
        return jsonify({
            'matches': [match.to_dict() for match in matches]
        }), 200
    except Exception as e:
        print(f"Error in get_match_results: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Serve static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == '' or path == 'index.html':
        return send_from_directory('static', 'index.html')
    return send_from_directory('static', path)

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
