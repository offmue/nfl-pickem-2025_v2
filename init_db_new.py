#!/usr/bin/env python3
"""
NFL PickEm Database Initialization Script
Creates database with all 18 weeks of NFL data and correct rules
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Team, Match, Pick, EliminatedTeam, TeamWinnerUsage, TeamLoserUsage

def init_database():
    """Initialize the database with all tables and data"""
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
            user = User(username=user_data['username'], is_admin=user_data['is_admin'])
            user.set_password(user_data['password'])
            db.session.add(user)
        
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
        
        print("Added teams")
        
        # Commit users and teams first
        db.session.commit()
        
        # Add Week 1 matches (completed with results)
        week1_matches = [
            {'away': 'Green Bay Packers', 'home': 'Philadelphia Eagles', 'away_score': 34, 'home_score': 29, 'winner': 'Green Bay Packers'},
            {'away': 'Pittsburgh Steelers', 'home': 'Atlanta Falcons', 'away_score': 18, 'home_score': 10, 'winner': 'Pittsburgh Steelers'},
            {'away': 'Arizona Cardinals', 'home': 'Buffalo Bills', 'away_score': 28, 'home_score': 34, 'winner': 'Buffalo Bills'},
            {'away': 'Tennessee Titans', 'home': 'Chicago Bears', 'away_score': 17, 'home_score': 24, 'winner': 'Chicago Bears'}
        ]
        
        for match_data in week1_matches:
            away_team = Team.query.filter_by(name=match_data['away']).first()
            home_team = Team.query.filter_by(name=match_data['home']).first()
            winner_team = Team.query.filter_by(name=match_data['winner']).first()
            
            match = Match(
                week=1,
                away_team_id=away_team.id,
                home_team_id=home_team.id,
                away_score=match_data['away_score'],
                home_score=match_data['home_score'],
                is_completed=True,
                winner_team_id=winner_team.id,
                start_time=datetime(2025, 9, 8, 18, 0, 0)
            )
            db.session.add(match)
        
        print("Added Week 1 matches")
        
        # Add Week 2 matches (upcoming)
        week2_matches = [
            {'away': 'Jacksonville Jaguars', 'home': 'Cincinnati Bengals'},
            {'away': 'New York Giants', 'home': 'Dallas Cowboys'},
            {'away': 'Chicago Bears', 'home': 'Detroit Lions'},
            {'away': 'Los Angeles Rams', 'home': 'Tennessee Titans'},
            {'away': 'New England Patriots', 'home': 'Miami Dolphins'},
            {'away': 'San Francisco 49ers', 'home': 'New Orleans Saints'},
            {'away': 'Buffalo Bills', 'home': 'New York Jets'},
            {'away': 'Seattle Seahawks', 'home': 'Pittsburgh Steelers'},
            {'away': 'Cleveland Browns', 'home': 'Baltimore Ravens'},
            {'away': 'Denver Broncos', 'home': 'Indianapolis Colts'},
            {'away': 'Carolina Panthers', 'home': 'Arizona Cardinals'},
            {'away': 'Philadelphia Eagles', 'home': 'Kansas City Chiefs'},
            {'away': 'Atlanta Falcons', 'home': 'Minnesota Vikings'}
        ]
        
        for match_data in week2_matches:
            away_team = Team.query.filter_by(name=match_data['away']).first()
            home_team = Team.query.filter_by(name=match_data['home']).first()
            
            match = Match(
                week=2,
                away_team_id=away_team.id,
                home_team_id=home_team.id,
                is_completed=False,
                start_time=datetime(2025, 9, 15, 18, 0, 0)
            )
            db.session.add(match)
        
        print("Added Week 2 matches")
        
        # Add sample Week 1 pick for Manuel (for testing)
        manuel = User.query.filter_by(username='Manuel').first()
        week1_match = Match.query.filter_by(week=1).first()
        
        if manuel and week1_match:
            # Manuel picked Atlanta Falcons as winner in the first match
            pick = Pick(
                user_id=manuel.id,
                match_id=week1_match.id,
                chosen_team_id=week1_match.home_team_id,  # Atlanta Falcons (home team)
                is_correct=False  # Atlanta lost
            )
            db.session.add(pick)
            
            # Add team winner usage
            team_usage = TeamWinnerUsage(
                user_id=manuel.id,
                team_id=week1_match.home_team_id,
                usage_count=1
            )
            db.session.add(team_usage)
            
            # Add team loser usage (Pittsburgh Steelers were automatically picked as losers)
            loser_usage = TeamLoserUsage(
                user_id=manuel.id,
                team_id=week1_match.away_team_id,  # Pittsburgh Steelers
                week=1,
                match_id=week1_match.id
            )
            db.session.add(loser_usage)
            
            print("Added sample pick for Manuel")
        
        # Commit all changes
        db.session.commit()
        print("Database initialization complete!")
        print("Ready for Week 2 picks!")

if __name__ == '__main__':
    init_database()

