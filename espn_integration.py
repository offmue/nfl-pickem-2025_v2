#!/usr/bin/env python3
"""
ESPN NFL Integration Module
Automatically fetches NFL game results and updates the PickEm database
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import logging
from app import app, db, Match, Pick, User
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ESPNIntegration:
    def __init__(self):
        self.base_url = "https://www.espn.com/nfl/schedule"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_week_schedule(self, week=None):
        """Get NFL schedule for a specific week from ESPN"""
        try:
            url = self.base_url
            if week:
                url += f"/_/week/{week}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"Error fetching ESPN schedule: {e}")
            return None
    
    def parse_game_results(self, soup, week):
        """Parse completed games from ESPN schedule page"""
        completed_games = []
        
        try:
            # Look for completed games with "Final" status
            game_elements = soup.find_all('a', href=re.compile(r'/nfl/game/'))
            
            for element in game_elements:
                text = element.get_text(strip=True)
                
                # Check if this is a final score (format: "TEAM1 XX, TEAM2 YY" or "XXX XX, YYY YY")
                score_pattern = r'([A-Z]{2,4})\s+(\d+),\s+([A-Z]{2,4})\s+(\d+)'
                match = re.search(score_pattern, text)
                
                if match:
                    away_team_abbr = match.group(1)
                    away_score = int(match.group(2))
                    home_team_abbr = match.group(3)
                    home_score = int(match.group(4))
                    
                    # Determine winner
                    if home_score > away_score:
                        winner_abbr = home_team_abbr
                    elif away_score > home_score:
                        winner_abbr = away_team_abbr
                    else:
                        winner_abbr = None  # Tie (rare in NFL)
                    
                    completed_games.append({
                        'week': week,
                        'away_team': away_team_abbr,
                        'home_team': home_team_abbr,
                        'away_score': away_score,
                        'home_score': home_score,
                        'winner': winner_abbr,
                        'status': 'completed'
                    })
            
            logger.info(f"Found {len(completed_games)} completed games for week {week}")
            return completed_games
            
        except Exception as e:
            logger.error(f"Error parsing game results: {e}")
            return []
    
    def map_espn_to_db_teams(self, espn_abbr):
        """Map ESPN team abbreviations to our database team names"""
        espn_to_db_mapping = {
            'PHI': 'Philadelphia Eagles',
            'DAL': 'Dallas Cowboys',
            'LAC': 'Los Angeles Chargers',
            'KC': 'Kansas City Chiefs',
            'TB': 'Tampa Bay Buccaneers',
            'ATL': 'Atlanta Falcons',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'IND': 'Indianapolis Colts',
            'MIA': 'Miami Dolphins',
            'LV': 'Las Vegas Raiders',
            'NE': 'New England Patriots',
            'ARI': 'Arizona Cardinals',
            'NO': 'New Orleans Saints',
            'PIT': 'Pittsburgh Steelers',
            'NYJ': 'New York Jets',
            'WSH': 'Washington Commanders',
            'NYG': 'New York Giants',
            'CAR': 'Carolina Panthers',
            'DEN': 'Denver Broncos',
            'BUF': 'Buffalo Bills',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'LAR': 'Los Angeles Rams',
            'MIN': 'Minnesota Vikings',
            'GB': 'Green Bay Packers',
            'DET': 'Detroit Lions',
            'CHI': 'Chicago Bears',
            'TEN': 'Tennessee Titans',
            'HOU': 'Houston Texans',
            'JAX': 'Jacksonville Jaguars',
            'BAL': 'Baltimore Ravens'
        }
        
        return espn_to_db_mapping.get(espn_abbr, espn_abbr)
    
    def update_match_results(self, completed_games):
        """Update match results in the database"""
        updated_matches = 0
        
        with app.app_context():
            for game in completed_games:
                try:
                    # Map ESPN abbreviations to full team names
                    away_team_name = self.map_espn_to_db_teams(game['away_team'])
                    home_team_name = self.map_espn_to_db_teams(game['home_team'])
                    winner_name = self.map_espn_to_db_teams(game['winner']) if game['winner'] else None
                    
                    # Find the match in our database
                    match = Match.query.filter_by(
                        week=game['week'],
                        away_team=away_team_name,
                        home_team=home_team_name
                    ).first()
                    
                    if match:
                        # Update match with results
                        match.away_score = game['away_score']
                        match.home_score = game['home_score']
                        match.winner = winner_name
                        match.status = 'completed'
                        match.updated_at = datetime.utcnow()
                        
                        db.session.commit()
                        updated_matches += 1
                        
                        logger.info(f"Updated match: {away_team_name} @ {home_team_name} - {game['away_score']}-{game['home_score']}")
                    else:
                        logger.warning(f"Match not found in database: {away_team_name} @ {home_team_name}")
                        
                except Exception as e:
                    logger.error(f"Error updating match {game}: {e}")
                    db.session.rollback()
        
        return updated_matches
    
    def calculate_user_scores(self, week):
        """Recalculate user scores after updating match results"""
        with app.app_context():
            users = User.query.all()
            
            for user in users:
                # Get all picks for this user up to the specified week
                picks = Pick.query.join(Match).filter(
                    Pick.user_id == user.id,
                    Match.week <= week,
                    Match.status == 'completed'
                ).all()
                
                correct_picks = 0
                for pick in picks:
                    if pick.match.winner == pick.chosen_team:
                        correct_picks += 1
                
                # Update user score (assuming we add a score field to User model)
                # For now, we'll calculate it dynamically via the existing get_score method
                logger.info(f"User {user.username}: {correct_picks} correct picks through week {week}")
    
    def check_week_completion(self, week):
        """Check if all games in a week are completed"""
        try:
            soup = self.get_week_schedule(week)
            if not soup:
                return False
            
            completed_games = self.parse_game_results(soup, week)
            
            # Check if we have results for all expected games in the week
            # NFL typically has 16 games per week (32 teams / 2)
            expected_games = 16
            
            if len(completed_games) >= expected_games:
                logger.info(f"Week {week} appears to be completed with {len(completed_games)} games")
                return True
            else:
                logger.info(f"Week {week} not yet completed: {len(completed_games)}/{expected_games} games finished")
                return False
                
        except Exception as e:
            logger.error(f"Error checking week completion: {e}")
            return False
    
    def process_weekly_update(self, week):
        """Main function to process weekly updates"""
        logger.info(f"Starting weekly update process for week {week}")
        
        try:
            # Check if week is completed
            if not self.check_week_completion(week):
                logger.info(f"Week {week} not yet completed, skipping update")
                return False
            
            # Get completed games
            soup = self.get_week_schedule(week)
            if not soup:
                logger.error("Failed to fetch ESPN schedule")
                return False
            
            completed_games = self.parse_game_results(soup, week)
            if not completed_games:
                logger.warning("No completed games found")
                return False
            
            # Update match results in database
            updated_matches = self.update_match_results(completed_games)
            
            # Recalculate user scores
            self.calculate_user_scores(week)
            
            logger.info(f"Weekly update completed: {updated_matches} matches updated for week {week}")
            return True
            
        except Exception as e:
            logger.error(f"Error in weekly update process: {e}")
            return False

    def test_espn_connection(self):
        """Test ESPN connection and parsing"""
        logger.info("🧪 Testing ESPN connection...")
        
        try:
            # Test with Week 1 (should be completed)
            soup = self.get_week_schedule(1)
            if soup:
                completed_games = self.parse_game_results(soup, 1)
                logger.info(f"✅ ESPN connection successful! Found {len(completed_games)} completed games in Week 1")
                return True
            else:
                logger.error("❌ Failed to connect to ESPN")
                return False
        except Exception as e:
            logger.error(f"❌ ESPN connection test failed: {e}")
            return False

def main():
    """Main function for testing"""
    espn = ESPNIntegration()
    
    # Test with Week 1 (should be completed)
    result = espn.process_weekly_update(1)
    print(f"Week 1 update result: {result}")

if __name__ == "__main__":
    main()

