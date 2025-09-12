#!/usr/bin/env python3
"""
NFL PickEm Scheduler
Automatically runs weekly updates every Tuesday after Monday Night Football
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from espn_integration import ESPNIntegration
import threading
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/nfl-pickem-updated/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NFLPickEmScheduler:
    def __init__(self):
        self.espn = ESPNIntegration()
        self.current_week = 2  # Start with Week 2
        self.max_week = 18     # Regular season ends at Week 18
        self.is_running = False
        
    def weekly_update_job(self):
        """Job that runs every Tuesday to check for completed weeks"""
        logger.info("=== WEEKLY UPDATE JOB STARTED ===")
        
        try:
            # Check if current week is completed
            if self.current_week <= self.max_week:
                logger.info(f"Checking Week {self.current_week} for completion...")
                
                success = self.espn.process_weekly_update(self.current_week)
                
                if success:
                    logger.info(f"✅ Week {self.current_week} successfully updated!")
                    self.current_week += 1
                    logger.info(f"📅 Moving to Week {self.current_week} for next update")
                    
                    # Send notification (placeholder for now)
                    self.send_update_notification(self.current_week - 1)
                else:
                    logger.info(f"⏳ Week {self.current_week} not yet completed, will check again next week")
            else:
                logger.info("🏁 Regular season completed! No more updates needed.")
                
        except Exception as e:
            logger.error(f"❌ Error in weekly update job: {e}")
        
        logger.info("=== WEEKLY UPDATE JOB COMPLETED ===\n")
    
    def send_update_notification(self, completed_week):
        """Send notification about completed week (placeholder)"""
        logger.info(f"📧 NOTIFICATION: Week {completed_week} results have been updated!")
        logger.info(f"🏈 All picks for Week {completed_week} have been scored")
        logger.info(f"🏆 Leaderboard has been updated with new rankings")
        
        # In a real implementation, this could send emails, push notifications, etc.
        # For now, we'll just log the notification
    
    def manual_update(self, week):
        """Manually trigger an update for a specific week"""
        logger.info(f"🔧 Manual update triggered for Week {week}")
        
        try:
            success = self.espn.process_weekly_update(week)
            if success:
                logger.info(f"✅ Manual update for Week {week} completed successfully")
                return True
            else:
                logger.warning(f"⚠️ Manual update for Week {week} failed or week not completed")
                return False
        except Exception as e:
            logger.error(f"❌ Error in manual update: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler daemon"""
        if self.is_running:
            logger.warning("Scheduler is already running!")
            return
        
        logger.info("🚀 Starting NFL PickEm Scheduler...")
        logger.info(f"📅 Current week: {self.current_week}")
        logger.info("⏰ Scheduled to run every Tuesday at 10:00 AM")
        
        # Schedule the job for every Tuesday at 10:00 AM
        schedule.every().tuesday.at("10:00").do(self.weekly_update_job)
        
        # Also schedule a backup check on Wednesday at 2:00 PM
        schedule.every().wednesday.at("14:00").do(self.weekly_update_job)
        
        self.is_running = True
        
        # Run the scheduler in a separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Scheduler started successfully!")
        return scheduler_thread
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping NFL PickEm Scheduler...")
        self.is_running = False
        schedule.clear()
        logger.info("✅ Scheduler stopped")
    
    def get_status(self):
        """Get current scheduler status"""
        status = {
            'is_running': self.is_running,
            'current_week': self.current_week,
            'max_week': self.max_week,
            'next_jobs': [str(job) for job in schedule.jobs],
            'last_run': datetime.now().isoformat()
        }
        return status
    
    def test_espn_connection(self):
        """Test ESPN connection and parsing"""
        logger.info("🧪 Testing ESPN connection...")
        
        try:
            # Test with Week 1 (should be completed)
            soup = self.espn.get_week_schedule(1)
            if soup:
                completed_games = self.espn.parse_game_results(soup, 1)
                logger.info(f"✅ ESPN connection successful! Found {len(completed_games)} completed games in Week 1")
                return True
            else:
                logger.error("❌ Failed to connect to ESPN")
                return False
        except Exception as e:
            logger.error(f"❌ ESPN connection test failed: {e}")
            return False

def main():
    """Main function for running the scheduler"""
    scheduler = NFLPickEmScheduler()
    
    # Test ESPN connection first
    if not scheduler.test_espn_connection():
        logger.error("ESPN connection test failed. Exiting.")
        return
    
    # Start the scheduler
    scheduler_thread = scheduler.start_scheduler()
    
    try:
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(10)
            
            # Print status every 10 minutes
            if datetime.now().minute % 10 == 0:
                status = scheduler.get_status()
                logger.info(f"📊 Status: Week {status['current_week']}, Running: {status['is_running']}")
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        scheduler.stop_scheduler()
        logger.info("Scheduler stopped. Goodbye!")

if __name__ == "__main__":
    main()

