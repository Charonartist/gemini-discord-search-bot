#!/usr/bin/env python3
"""
Gemini Discord Search Bot Runner
Starts the Discord bot with proper error handling and logging
"""

import sys
import logging
import asyncio
from config import Config
from discord_bot import setup_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Setup and run the bot
        bot = setup_bot()
        logger.info("Starting Gemini Discord Search Bot...")
        
        # Run the bot
        bot.run(Config.DISCORD_TOKEN)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()