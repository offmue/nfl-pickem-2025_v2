#!/usr/bin/env python3
"""
Keep-Alive System for NFL PickEm App
Pings the server every 5 minutes to prevent it from going to sleep
"""

import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/nfl-pickem-updated/keep_alive.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
PING_INTERVAL = 300  # 5 minutes in seconds
LOCAL_URL = "http://localhost:5000"
PUBLIC_URL = "https://5000-iriksqohk24xste1mbo4u-5a092e06.manusvm.computer"

def ping_server():
    """Ping the server to keep it alive"""
    try:
        # Try local ping first
        response = requests.get(LOCAL_URL, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Local ping successful - Server is alive (Status: {response.status_code})")
            return True
    except Exception as e:
        logger.warning(f"⚠️ Local ping failed: {e}")
    
    try:
        # Try public URL ping
        response = requests.get(PUBLIC_URL, timeout=15)
        if response.status_code == 200:
            logger.info(f"✅ Public ping successful - Server is alive (Status: {response.status_code})")
            return True
    except Exception as e:
        logger.error(f"❌ Public ping failed: {e}")
    
    logger.error("❌ Both ping attempts failed - Server may be down!")
    return False

def main():
    """Main keep-alive loop"""
    logger.info("🚀 NFL PickEm Keep-Alive System started")
    logger.info(f"📡 Pinging every {PING_INTERVAL} seconds ({PING_INTERVAL//60} minutes)")
    
    ping_count = 0
    
    while True:
        try:
            ping_count += 1
            logger.info(f"🔄 Ping #{ping_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            success = ping_server()
            
            if success:
                logger.info(f"✅ Keep-alive ping #{ping_count} successful")
            else:
                logger.error(f"❌ Keep-alive ping #{ping_count} failed")
            
            # Wait for next ping
            time.sleep(PING_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("🛑 Keep-alive system stopped by user")
            break
        except Exception as e:
            logger.error(f"💥 Unexpected error in keep-alive loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()

