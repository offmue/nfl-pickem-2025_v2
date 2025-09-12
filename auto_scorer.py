#!/usr/bin/env python3
"""
NFL PickEm Auto Scorer
Safely updates scores without interfering with existing functionality
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import time
import schedule
import threading
from app import app, db, Match, Pick, User, Team

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/nfl-pickem-updated/auto_scorer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SafeAutoScorer:
    def __init__(self):
        self.base_url = "https://www.espn.com/nfl/schedule"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.current_week = 2  # Start with Week 2
        
    def get_espn_results(self, week):
        """Safely get NFL results from ESPN"""
        try:
            url = f"{self.base_url}/_/week/{week}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for completed games with final scores
            completed_games = []
            game_elements = soup.find_all('a', href=re.compile(r'/nfl/game/'))
            
            for element in game_elements:
                text = element.get_text(strip=True)
                
                # Match pattern: "TEAM1 XX, TEAM2 YY"
                score_pattern = r'([A-Z]{2,4})\s+(\d+),\s+([A-Z]{2,4})\s+(\d+)'
                match = re.search(score_pattern, text)
                
                if match:
                    away_abbr = match.group(1)
                    away_score = int(match.group(2))
                    home_abbr = match.group(3)
                    home_score = int(match.group(4))
                    
                    # Determine winner
                    if home_score > away_score:
                        winner_abbr = home_abbr
                    elif away_score > home_score:
                        winner_abbr = away_abbr
                    else:
                        winner_abbr = None  # Tie
                    
                    completed_games.append({
                        'away_team_abbr': away_abbr,
                        'home_team_abbr': home_abbr,
                        'away_score': away_score,
                        'home_score': home_score,
                        'winner_abbr': winner_abbr
                    })
            
            logger.info(f"Found {len(completed_games)} completed games for Week {week}")
            return completed_games
            
        except Exception as e:
            logger.error(f"Error getting ESPN results: {e}")
            return []
    
    def map_espn_to_team_name(self, espn_abbr):
        """Map ESPN abbreviations to our team names"""
        mapping = {
            'ATL': 'Atlanta Falcons',
            'TB': 'Tampa Bay Buccaneers',
            'DEN': 'Denver Broncos',
            'TEN': 'Tennessee Titans',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'WSH': 'Washington Commanders',
            'NYG': 'New York Giants',
            'KC': 'Kansas City Chiefs',
            'LAC': 'Los Angeles Chargers',
            'PHI': 'Philadelphia Eagles',
            'DAL': 'Dallas Cowboys',
            'BUF': 'Buffalo Bills',
            'MIA': 'Miami Dolphins',
            'NE': 'New England Patriots',
            'NYJ': 'New York Jets',
            'PIT': 'Pittsburgh Steelers',
            'BAL': 'Baltimore Ravens',
            'IND': 'Indianapolis Colts',
            'HOU': 'Houston Texans',
            'JAX': 'Jacksonville Jaguars',
            'LV': 'Las Vegas Raiders',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'LAR': 'Los Angeles Rams',
            'ARI': 'Arizona Cardinals',
            'NO': 'New Orleans Saints',
            'CAR': 'Carolina Panthers',
            'GB': 'Green Bay Packers',
            'MIN': 'Minnesota Vikings',
            'CHI': 'Chicago Bears',
            'DET': 'Detroit Lions'
        }
        return mapping.get(espn_abbr, espn_abbr)
    
    def update_week_results(self, week):
        """Safely update results for a specific week"""
        logger.info(f"Starting safe update for Week {week}")
        
        try:
            # Get ESPN results
            espn_results = self.get_espn_results(week)
            if not espn_results:
                logger.warning(f"No ESPN results found for Week {week}")
                return False
            
            # Check if we have enough games (NFL typically has 16 games per week)
            if len(espn_results) < 14:  # Allow some flexibility
                logger.info(f"Week {week} not complete yet ({len(espn_results)} games)")
                return False
            
            updated_count = 0
            
            with app.app_context():
                for game in espn_results:
                    try:
                        # Map team names
                        away_team_name = self.map_espn_to_team_name(game['away_team_abbr'])
                        home_team_name = self.map_espn_to_team_name(game['home_team_abbr'])
                        winner_name = self.map_espn_to_team_name(game['winner_abbr']) if game['winner_abbr'] else None
                        
                        # Find the match in our database
                        match = Match.query.filter_by(
                            week=week,
                            away_team_id=Team.query.filter_by(name=away_team_name).first().id if Team.query.filter_by(name=away_team_name).first() else None,
                            home_team_id=Team.query.filter_by(name=home_team_name).first().id if Team.query.filter_by(name=home_team_name).first() else None
                        ).first()
                        
                        if match and not match.is_completed:
                            # Update match results
                            if winner_name:
                                winner_team = Team.query.filter_by(name=winner_name).first()
                                if winner_team:
                                    match.winner_team_id = winner_team.id
                                    match.is_completed = True
                                    
                                    db.session.commit()
                                    updated_count += 1
                                    
                                    logger.info(f"Updated: {away_team_name} @ {home_team_name} - Winner: {winner_name}")
                        
                    except Exception as e:
                        logger.error(f"Error updating match {game}: {e}")
                        db.session.rollback()
            
            logger.info(f"Successfully updated {updated_count} matches for Week {week}")
            return updated_count > 0
            
        except Exception as e:
            logger.error(f"Error in update_week_results: {e}")
            return False
    
    def weekly_update_job(self):
        """Job that runs weekly to update scores"""
        logger.info("=== WEEKLY AUTO-SCORER JOB STARTED ===")
        
        try:
            success = self.update_week_results(self.current_week)
            
            if success:
                logger.info(f"✅ Week {self.current_week} successfully updated!")
                self.current_week += 1
                logger.info(f"📅 Moving to Week {self.current_week} for next update")
            else:
                logger.info(f"⏳ Week {self.current_week} not ready for update")
                
        except Exception as e:
            logger.error(f"❌ Error in weekly update job: {e}")
        
        logger.info("=== WEEKLY AUTO-SCORER JOB COMPLETED ===\n")
    
    def start_scheduler(self):
        """Start the weekly scheduler"""
        logger.info("🚀 Starting NFL PickEm Auto-Scorer...")
        logger.info(f"📅 Current week: {self.current_week}")
        logger.info("⏰ Scheduled to run every Tuesday at 10:00 AM")
        
        # Schedule for every Tuesday at 10:00 AM
        schedule.every().tuesday.at("10:00").do(self.weekly_update_job)
        
        # Also schedule a backup check on Wednesday
        schedule.every().wednesday.at("14:00").do(self.weekly_update_job)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Auto-Scorer started successfully!")
        return scheduler_thread
    
    def test_connection(self):
        """Test ESPN connection"""
        logger.info("🧪 Testing ESPN connection...")
        
        try:
            results = self.get_espn_results(1)  # Test with Week 1
            if results:
                logger.info(f"✅ ESPN connection successful! Found {len(results)} games")
                return True
            else:
                logger.error("❌ No results from ESPN")
                return False
        except Exception as e:
            logger.error(f"❌ ESPN test failed: {e}")
            return False

def main():
    """Main function to start the auto-scorer"""
    scorer = SafeAutoScorer()
    
    # Test connection first
    if not scorer.test_connection():
        logger.error("ESPN connection test failed. Exiting.")
        return
    
    # Start the scheduler
    scorer.start_scheduler()
    
    try:
        logger.info("Auto-Scorer is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Auto-Scorer stopped.")

if __name__ == "__main__":
    main()

