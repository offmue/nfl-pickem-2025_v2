"""
Database Backup Module for NFL PickEm App

This module provides functions to backup and restore the SQLite database,
ensuring data persistence even when the server restarts.
"""

import os
import sqlite3
import shutil
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='db_backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
DB_PATH = 'instance/nfl_pickem.db'
BACKUP_DIR = 'db_backups'
BACKUP_INTERVAL = 300  # 5 minutes in seconds
BACKUP_COUNT = 5  # Keep 5 recent backups

def ensure_backup_dir():
    """Ensure the backup directory exists."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logging.info(f"Created backup directory: {BACKUP_DIR}")

def create_backup():
    """Create a backup of the SQLite database."""
    try:
        ensure_backup_dir()
        
        # Check if database exists
        if not os.path.exists(DB_PATH):
            logging.warning(f"Database not found at {DB_PATH}, skipping backup")
            return False
        
        # Create timestamp for backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f'nfl_pickem_{timestamp}.db')
        
        # Copy the database file
        shutil.copy2(DB_PATH, backup_path)
        logging.info(f"Database backup created: {backup_path}")
        
        # Create metadata file with timestamp
        metadata = {
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'db_size': os.path.getsize(backup_path)
        }
        
        with open(f"{backup_path}.meta", 'w') as f:
            json.dump(metadata, f)
        
        # Clean up old backups
        cleanup_old_backups()
        
        return True
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        return False

def cleanup_old_backups():
    """Keep only the most recent backups."""
    try:
        ensure_backup_dir()
        
        # Get all backup files
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)), reverse=True)
        
        # Remove old backups
        if len(backups) > BACKUP_COUNT:
            for old_backup in backups[BACKUP_COUNT:]:
                old_path = os.path.join(BACKUP_DIR, old_backup)
                os.remove(old_path)
                # Also remove metadata file if it exists
                meta_path = f"{old_path}.meta"
                if os.path.exists(meta_path):
                    os.remove(meta_path)
                logging.info(f"Removed old backup: {old_backup}")
    except Exception as e:
        logging.error(f"Cleanup failed: {str(e)}")

def get_latest_backup():
    """Get the path to the latest backup file."""
    try:
        ensure_backup_dir()
        
        # Get all backup files
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        
        if not backups:
            logging.warning("No backups found")
            return None
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)), reverse=True)
        
        # Return the newest backup
        return os.path.join(BACKUP_DIR, backups[0])
    except Exception as e:
        logging.error(f"Failed to get latest backup: {str(e)}")
        return None

def restore_from_backup():
    """Restore the database from the latest backup."""
    try:
        # Check if database directory exists
        if not os.path.exists('instance'):
            os.makedirs('instance')
            logging.info("Created instance directory")
        
        # Get the latest backup
        latest_backup = get_latest_backup()
        
        if not latest_backup:
            logging.warning("No backup found to restore from")
            return False
        
        # Copy the backup to the database location
        shutil.copy2(latest_backup, DB_PATH)
        logging.info(f"Database restored from backup: {latest_backup}")
        
        return True
    except Exception as e:
        logging.error(f"Restore failed: {str(e)}")
        return False

def check_db_exists():
    """Check if the database exists and is valid."""
    if not os.path.exists(DB_PATH):
        return False
    
    try:
        # Try to open the database to verify it's valid
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        return True
    except sqlite3.Error:
        return False

def run_backup_service():
    """Run the backup service in a loop."""
    logging.info("Starting database backup service")
    
    while True:
        try:
            # Check if database exists and create backup
            if check_db_exists():
                create_backup()
            
            # Sleep for the backup interval
            time.sleep(BACKUP_INTERVAL)
        except Exception as e:
            logging.error(f"Backup service error: {str(e)}")
            time.sleep(60)  # Sleep for a minute on error

if __name__ == "__main__":
    run_backup_service()

