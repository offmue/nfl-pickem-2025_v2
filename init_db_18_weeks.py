#!/usr/bin/env python3
"""
NFL PickEm Database Initialization Script
Creates database with all 18 weeks of NFL games
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Team, Match, Pick, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def init_database():
    with app.app_context():
        # Remove existing database if it exists
        if os.path.exists('nfl_pickem.db'):
            os.remove('nfl_pickem.db')
            print("Removed existing database")
        
        # Create all tables
        db.create_all()
        print("Created all database tables")
        
        # Add users
        users_data = [
            {'username': 'Manuel', 'password': 'Manuel1', 'is_admin': True},
            {'username': 'Daniel', 'password': 'Daniel1', 'is_admin': False},
            {'username': 'Raff', 'password': 'Raff1', 'is_admin': False},
            {'username': 'Haunschi', 'password': 'Haunschi1', 'is_admin': False}
        ]
        
        for user_data in users_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(username=user_data['username'], is_admin=user_data['is_admin'])
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()
        print("Added users")
        
        # Add teams
        teams_data = [
            {'name': 'Arizona Cardinals', 'abbreviation': 'ARI', 'logo_url': '/static/logos/arizona-cardinals.png'},
            {'name': 'Atlanta Falcons', 'abbreviation': 'ATL', 'logo_url': '/static/logos/atlanta-falcons.png'},
            {'name': 'Baltimore Ravens', 'abbreviation': 'BAL', 'logo_url': '/static/logos/baltimore-ravens.png'},
            {'name': 'Buffalo Bills', 'abbreviation': 'BUF', 'logo_url': '/static/logos/buffalo-bills.png'},
            {'name': 'Carolina Panthers', 'abbreviation': 'CAR', 'logo_url': '/static/logos/carolina-panthers.png'},
            {'name': 'Chicago Bears', 'abbreviation': 'CHI', 'logo_url': '/static/logos/chicago-bears.png'},
            {'name': 'Cincinnati Bengals', 'abbreviation': 'CIN', 'logo_url': '/static/logos/cincinnati-bengals.png'},
            {'name': 'Cleveland Browns', 'abbreviation': 'CLE', 'logo_url': '/static/logos/cleveland-browns.png'},
            {'name': 'Dallas Cowboys', 'abbreviation': 'DAL', 'logo_url': '/static/logos/dallas-cowboys.png'},
            {'name': 'Denver Broncos', 'abbreviation': 'DEN', 'logo_url': '/static/logos/denver-broncos.png'},
            {'name': 'Detroit Lions', 'abbreviation': 'DET', 'logo_url': '/static/logos/detroit-lions.png'},
            {'name': 'Green Bay Packers', 'abbreviation': 'GB', 'logo_url': '/static/logos/green-bay-packers.png'},
            {'name': 'Houston Texans', 'abbreviation': 'HOU', 'logo_url': '/static/logos/houston-texans.png'},
            {'name': 'Indianapolis Colts', 'abbreviation': 'IND', 'logo_url': '/static/logos/indianapolis-colts.png'},
            {'name': 'Jacksonville Jaguars', 'abbreviation': 'JAX', 'logo_url': '/static/logos/jacksonville-jaguars.png'},
            {'name': 'Kansas City Chiefs', 'abbreviation': 'KC', 'logo_url': '/static/logos/kansas-city-chiefs.png'},
            {'name': 'Las Vegas Raiders', 'abbreviation': 'LV', 'logo_url': '/static/logos/las-vegas-raiders.png'},
            {'name': 'Los Angeles Chargers', 'abbreviation': 'LAC', 'logo_url': '/static/logos/los-angeles-chargers.png'},
            {'name': 'Los Angeles Rams', 'abbreviation': 'LAR', 'logo_url': '/static/logos/los-angeles-rams.png'},
            {'name': 'Miami Dolphins', 'abbreviation': 'MIA', 'logo_url': '/static/logos/miami-dolphins.png'},
            {'name': 'Minnesota Vikings', 'abbreviation': 'MIN', 'logo_url': '/static/logos/minnesota-vikings.png'},
            {'name': 'New England Patriots', 'abbreviation': 'NE', 'logo_url': '/static/logos/new-england-patriots.png'},
            {'name': 'New Orleans Saints', 'abbreviation': 'NO', 'logo_url': '/static/logos/new-orleans-saints.png'},
            {'name': 'New York Giants', 'abbreviation': 'NYG', 'logo_url': '/static/logos/new-york-giants.png'},
            {'name': 'New York Jets', 'abbreviation': 'NYJ', 'logo_url': '/static/logos/new-york-jets.png'},
            {'name': 'Philadelphia Eagles', 'abbreviation': 'PHI', 'logo_url': '/static/logos/philadelphia-eagles.png'},
            {'name': 'Pittsburgh Steelers', 'abbreviation': 'PIT', 'logo_url': '/static/logos/pittsburgh-steelers.png'},
            {'name': 'San Francisco 49ers', 'abbreviation': 'SF', 'logo_url': '/static/logos/san-francisco-49ers.png'},
            {'name': 'Seattle Seahawks', 'abbreviation': 'SEA', 'logo_url': '/static/logos/seattle-seahawks.png'},
            {'name': 'Tampa Bay Buccaneers', 'abbreviation': 'TB', 'logo_url': '/static/logos/tampa-bay-buccaneers.png'},
            {'name': 'Tennessee Titans', 'abbreviation': 'TEN', 'logo_url': '/static/logos/tennessee-titans.png'},
            {'name': 'Washington Commanders', 'abbreviation': 'WAS', 'logo_url': '/static/logos/washington-commanders.png'}
        ]
        
        for team_data in teams_data:
            team = Team(name=team_data['name'], abbreviation=team_data['abbreviation'], logo_url=team_data['logo_url'])
            db.session.add(team)
        
        db.session.commit()
        print("Added teams")
        
        # Create a dictionary for easy team lookup
        teams = {team.name: team for team in Team.query.all()}
        
        # Add all 18 weeks of matches
        add_all_weeks(teams)
        
        print("Database initialization complete!")
        print("Ready for Week 2 picks!")

def add_all_weeks(teams):
    """Add all 18 weeks of NFL matches"""
    
    # Week 1 (completed with results)
    week1_matches = [
        {'away': 'Green Bay Packers', 'home': 'Philadelphia Eagles', 'away_score': 34, 'home_score': 29, 'date': '2025-09-08'},
        {'away': 'Pittsburgh Steelers', 'home': 'Atlanta Falcons', 'away_score': 18, 'home_score': 10, 'date': '2025-09-08'},
        {'away': 'Arizona Cardinals', 'home': 'Buffalo Bills', 'away_score': 28, 'home_score': 34, 'date': '2025-09-08'},
        {'away': 'Tennessee Titans', 'home': 'Chicago Bears', 'away_score': 17, 'home_score': 24, 'date': '2025-09-08'},
        {'away': 'Miami Dolphins', 'home': 'Jacksonville Jaguars', 'away_score': 20, 'home_score': 17, 'date': '2025-09-08'},
        {'away': 'New England Patriots', 'home': 'Cincinnati Bengals', 'away_score': 16, 'home_score': 10, 'date': '2025-09-08'},
        {'away': 'Carolina Panthers', 'home': 'New Orleans Saints', 'away_score': 10, 'home_score': 47, 'date': '2025-09-08'},
        {'away': 'Minnesota Vikings', 'home': 'Tampa Bay Buccaneers', 'away_score': 20, 'home_score': 17, 'date': '2025-09-08'},
        {'away': 'Cleveland Browns', 'home': 'Dallas Cowboys', 'away_score': 33, 'home_score': 17, 'date': '2025-09-08'},
        {'away': 'Las Vegas Raiders', 'home': 'Los Angeles Chargers', 'away_score': 22, 'home_score': 10, 'date': '2025-09-08'},
        {'away': 'Washington Commanders', 'home': 'Tampa Bay Buccaneers', 'away_score': 37, 'home_score': 20, 'date': '2025-09-08'},
        {'away': 'Indianapolis Colts', 'home': 'Houston Texans', 'away_score': 29, 'home_score': 27, 'date': '2025-09-08'},
        {'away': 'New York Giants', 'home': 'Minnesota Vikings', 'away_score': 28, 'home_score': 6, 'date': '2025-09-08'},
        {'away': 'Denver Broncos', 'home': 'Seattle Seahawks', 'away_score': 26, 'home_score': 20, 'date': '2025-09-08'},
        {'away': 'Detroit Lions', 'home': 'Los Angeles Rams', 'away_score': 26, 'home_score': 20, 'date': '2025-09-08'},
        {'away': 'Kansas City Chiefs', 'home': 'Baltimore Ravens', 'away_score': 27, 'home_score': 20, 'date': '2025-09-09'}
    ]
    
    add_week_matches(1, week1_matches, teams, completed=True)
    
    # Week 2 (upcoming)
    week2_matches = [
        {'away': 'Jacksonville Jaguars', 'home': 'Cincinnati Bengals', 'date': '2025-09-15'},
        {'away': 'New York Giants', 'home': 'Dallas Cowboys', 'date': '2025-09-15'},
        {'away': 'Chicago Bears', 'home': 'Detroit Lions', 'date': '2025-09-15'},
        {'away': 'Los Angeles Rams', 'home': 'Tennessee Titans', 'date': '2025-09-15'},
        {'away': 'New England Patriots', 'home': 'Miami Dolphins', 'date': '2025-09-15'},
        {'away': 'San Francisco 49ers', 'home': 'New Orleans Saints', 'date': '2025-09-15'},
        {'away': 'Buffalo Bills', 'home': 'New York Jets', 'date': '2025-09-15'},
        {'away': 'Seattle Seahawks', 'home': 'Pittsburgh Steelers', 'date': '2025-09-15'},
        {'away': 'Cleveland Browns', 'home': 'Baltimore Ravens', 'date': '2025-09-15'},
        {'away': 'Denver Broncos', 'home': 'Indianapolis Colts', 'date': '2025-09-15'},
        {'away': 'Carolina Panthers', 'home': 'Arizona Cardinals', 'date': '2025-09-15'},
        {'away': 'Philadelphia Eagles', 'home': 'Kansas City Chiefs', 'date': '2025-09-15'},
        {'away': 'Atlanta Falcons', 'home': 'Minnesota Vikings', 'date': '2025-09-15'},
        {'away': 'Green Bay Packers', 'home': 'Washington Commanders', 'date': '2025-09-15'},
        {'away': 'Tampa Bay Buccaneers', 'home': 'Houston Texans', 'date': '2025-09-16'}
    ]
    
    add_week_matches(2, week2_matches, teams, completed=False)
    
    # Weeks 3-18 (future games)
    for week in range(3, 19):
        week_matches = generate_week_matches(week)
        add_week_matches(week, week_matches, teams, completed=False)

def generate_week_matches(week):
    """Generate realistic matches for a given week"""
    # This is a simplified version - in reality you'd use the actual NFL schedule
    base_date = datetime(2025, 9, 8) + timedelta(weeks=week-1)
    
    # Sample matchups (in reality, you'd use the actual NFL schedule)
    sample_matchups = [
        {'away': 'Arizona Cardinals', 'home': 'Seattle Seahawks'},
        {'away': 'Atlanta Falcons', 'home': 'Carolina Panthers'},
        {'away': 'Baltimore Ravens', 'home': 'Pittsburgh Steelers'},
        {'away': 'Buffalo Bills', 'home': 'Miami Dolphins'},
        {'away': 'Chicago Bears', 'home': 'Green Bay Packers'},
        {'away': 'Cincinnati Bengals', 'home': 'Cleveland Browns'},
        {'away': 'Dallas Cowboys', 'home': 'New York Giants'},
        {'away': 'Denver Broncos', 'home': 'Kansas City Chiefs'},
        {'away': 'Detroit Lions', 'home': 'Minnesota Vikings'},
        {'away': 'Houston Texans', 'home': 'Indianapolis Colts'},
        {'away': 'Jacksonville Jaguars', 'home': 'Tennessee Titans'},
        {'away': 'Las Vegas Raiders', 'home': 'Los Angeles Chargers'},
        {'away': 'Los Angeles Rams', 'home': 'San Francisco 49ers'},
        {'away': 'New England Patriots', 'home': 'New York Jets'},
        {'away': 'New Orleans Saints', 'home': 'Tampa Bay Buccaneers'},
        {'away': 'Philadelphia Eagles', 'home': 'Washington Commanders'}
    ]
    
    # Add date to each match
    for i, match in enumerate(sample_matchups):
        match['date'] = (base_date + timedelta(days=i % 3)).strftime('%Y-%m-%d')
    
    return sample_matchups

def add_week_matches(week, matches, teams, completed=False):
    """Add matches for a specific week"""
    for match_data in matches:
        away_team = teams[match_data['away']]
        home_team = teams[match_data['home']]
        
        match_date = datetime.strptime(match_data['date'], '%Y-%m-%d')
        
        match = Match(
            week=week,
            away_team_id=away_team.id,
            home_team_id=home_team.id,
            start_time=match_date,
            is_completed=completed
        )
        
        if completed and 'away_score' in match_data:
            match.away_score = match_data['away_score']
            match.home_score = match_data['home_score']
            # Determine winner
            if match_data['away_score'] > match_data['home_score']:
                match.winner_team_id = away_team.id
            else:
                match.winner_team_id = home_team.id
        
        db.session.add(match)
    
    db.session.commit()
    print(f"Added Week {week} matches")

if __name__ == '__main__':
    init_database()

