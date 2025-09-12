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
from db_backup import restore_from_backup, create_backup, check_db_exists, run_backup_service

# Configure logging
logging.basicConfig(
    filename='app_launcher.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

