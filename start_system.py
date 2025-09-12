#!/usr/bin/env python3
"""
NFL PickEm System Startup Script
Starts both the Flask web application and the automated scheduler
"""

import subprocess
import time
import logging
import sys
import os
import signal
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/nfl-pickem-updated/system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NFLPickEmSystem:
    def __init__(self):
        self.flask_process = None
        self.scheduler_process = None
        self.is_running = False
        
    def start_flask_app(self):
        """Start the Flask web application"""
        logger.info("🚀 Starting Flask web application...")
        
        try:
            self.flask_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd='/home/ubuntu/nfl-pickem-updated',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give Flask a moment to start
            time.sleep(3)
            
            if self.flask_process.poll() is None:
                logger.info("✅ Flask application started successfully")
                return True
            else:
                logger.error("❌ Flask application failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Flask app: {e}")
            return False
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        logger.info("⏰ Starting automated scheduler...")
        
        try:
            self.scheduler_process = subprocess.Popen(
                [sys.executable, 'scheduler.py'],
                cwd='/home/ubuntu/nfl-pickem-updated',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give scheduler a moment to start
            time.sleep(2)
            
            if self.scheduler_process.poll() is None:
                logger.info("✅ Scheduler started successfully")
                return True
            else:
                logger.error("❌ Scheduler failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            return False
    
    def test_system(self):
        """Test system components before starting"""
        logger.info("🧪 Testing system components...")
        
        # Test ESPN integration
        try:
            from espn_integration import ESPNIntegration
            espn = ESPNIntegration()
            
            if espn.test_espn_connection():
                logger.info("✅ ESPN integration test passed")
            else:
                logger.error("❌ ESPN integration test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ ESPN integration test error: {e}")
            return False
        
        # Test database connection
        try:
            from app import app, db, User
            with app.app_context():
                user_count = User.query.count()
                logger.info(f"✅ Database connection test passed ({user_count} users)")
                
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
        
        return True
    
    def start_system(self):
        """Start the complete NFL PickEm system"""
        logger.info("🏈 Starting NFL PickEm Automated System...")
        
        # Test components first
        if not self.test_system():
            logger.error("❌ System tests failed. Aborting startup.")
            return False
        
        # Start Flask app
        if not self.start_flask_app():
            logger.error("❌ Failed to start Flask app. Aborting.")
            return False
        
        # Start scheduler
        if not self.start_scheduler():
            logger.error("❌ Failed to start scheduler. Stopping Flask app.")
            self.stop_system()
            return False
        
        self.is_running = True
        logger.info("🎉 NFL PickEm system started successfully!")
        logger.info("📱 Web app: http://localhost:5000")
        logger.info("⏰ Scheduler: Running (updates every Tuesday)")
        
        return True
    
    def stop_system(self):
        """Stop the complete system"""
        logger.info("🛑 Stopping NFL PickEm system...")
        
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=10)
                logger.info("✅ Flask app stopped")
            except Exception as e:
                logger.error(f"Error stopping Flask app: {e}")
                self.flask_process.kill()
        
        if self.scheduler_process:
            try:
                self.scheduler_process.terminate()
                self.scheduler_process.wait(timeout=10)
                logger.info("✅ Scheduler stopped")
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
                self.scheduler_process.kill()
        
        self.is_running = False
        logger.info("✅ System stopped successfully")
    
    def monitor_system(self):
        """Monitor system health"""
        logger.info("👁️ Starting system monitoring...")
        
        while self.is_running:
            try:
                # Check Flask app
                if self.flask_process and self.flask_process.poll() is not None:
                    logger.error("❌ Flask app crashed! Attempting restart...")
                    self.start_flask_app()
                
                # Check scheduler
                if self.scheduler_process and self.scheduler_process.poll() is not None:
                    logger.error("❌ Scheduler crashed! Attempting restart...")
                    self.start_scheduler()
                
                # Log status every hour
                if time.time() % 3600 < 60:  # Every hour
                    logger.info("💚 System health check: All components running")
                
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(60)
    
    def run(self):
        """Main run method"""
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            self.stop_system()
            sys.exit(0)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the system
        if self.start_system():
            try:
                self.monitor_system()
            except KeyboardInterrupt:
                pass
            finally:
                self.stop_system()
        else:
            logger.error("❌ Failed to start system")
            sys.exit(1)

def main():
    """Main function"""
    system = NFLPickEmSystem()
    system.run()

if __name__ == "__main__":
    main()

