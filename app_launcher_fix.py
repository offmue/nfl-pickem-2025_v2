"""
NFL PickEm App Launcher

This script launches the NFL PickEm app with database backup and restoration.
It ensures data persistence even when the server restarts.
"""

import os
import sys
import time
import threading
import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename='app_launcher.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import db_backup functions
try:
    from db_backup import restore_from_backup, create_backup, check_db_exists, run_backup_service
    logging.info("Successfully imported db_backup functions")
except ImportError as e:
    logging.error(f"Error importing from db_backup: {str(e)}")
    
    # Define fallback functions
    def check_db_exists():
        """Check if the database exists."""
        db_path = 'instance/nfl_pickem.db'
        return os.path.exists(db_path)
    
    def create_backup():
        """Create a backup of the database."""
        logging.info("Using fallback create_backup function")
        try:
            if not os.path.exists('db_backups'):
                os.makedirs('db_backups')
            
            db_path = 'instance/nfl_pickem.db'
            if os.path.exists(db_path):
                import shutil
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join('db_backups', f'nfl_pickem_{timestamp}.db')
                shutil.copy2(db_path, backup_path)
                logging.info(f"Created backup at {backup_path}")
                return True
            return False
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            return False
    
    def restore_from_backup():
        """Restore the database from backup."""
        logging.info("Using fallback restore_from_backup function")
        try:
            if not os.path.exists('db_backups'):
                logging.warning("No backups directory found")
                return False
            
            backups = [f for f in os.listdir('db_backups') if f.endswith('.db')]
            if not backups:
                logging.warning("No backups found")
                return False
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: os.path.getctime(os.path.join('db_backups', x)), reverse=True)
            
            # Get the newest backup
            latest_backup = os.path.join('db_backups', backups[0])
            
            # Ensure instance directory exists
            if not os.path.exists('instance'):
                os.makedirs('instance')
            
            # Copy the backup to the database location
            import shutil
            shutil.copy2(latest_backup, 'instance/nfl_pickem.db')
            logging.info(f"Restored from backup: {latest_backup}")
            return True
        except Exception as e:
            logging.error(f"Restore failed: {str(e)}")
            return False
    
    def run_backup_service():
        """Run the backup service."""
        logging.info("Using fallback run_backup_service function")
        while True:
            try:
                if check_db_exists():
                    create_backup()
                time.sleep(300)  # 5 minutes
            except Exception as e:
                logging.error(f"Backup service error: {str(e)}")
                time.sleep(60)

def start_backup_service():
    """Start the backup service in a separate thread."""
    backup_thread = threading.Thread(target=run_backup_service)
    backup_thread.daemon = True
    backup_thread.start()
    logging.info("Backup service started in background")

def start_flask_app():
    """Start the Flask application."""
    try:
        # Run the Flask app
        subprocess.run([sys.executable, 'app.py'])
    except Exception as e:
        logging.error(f"Error starting Flask app: {str(e)}")

def main():
    """Main function to launch the app with database handling."""
    logging.info("Starting NFL PickEm App Launcher")
    
    # Check if database exists
    if not check_db_exists():
        logging.info("Database not found, attempting to restore from backup")
        restore_success = restore_from_backup()
        
        if not restore_success:
            logging.info("No backup found or restore failed, will create new database")
    else:
        # Create a backup of the existing database before starting
        create_backup()
    
    # Start the backup service
    start_backup_service()
    
    # Start the Flask app
    logging.info("Starting Flask application")
    start_flask_app()

if __name__ == "__main__":
    main()

