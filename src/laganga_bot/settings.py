import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API URLs
    FLASH_DEALS_API_URL = os.getenv("FLASH_DEALS_API_URL")

    # Twitter Credentials
    # Using Standard OAuth 1.0a naming which is required for v1.1 Media Upload
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")               # Consumer Key
    TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET") # Consumer Secret
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Optional - For v2 App only (not used for user posting with media currently)
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
    TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")

    # Other
    DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls):
        """
        Validates that necessary configuration is present.
        """
        if not cls.FLASH_DEALS_API_URL:
            raise ValueError("FLASH_DEALS_API_URL environment variable is not set")
        
        # We need these 4 for posting with images (Tweepy v1.1 + v2)
        if not all([cls.TWITTER_API_KEY, cls.TWITTER_API_KEY_SECRET, cls.TWITTER_ACCESS_TOKEN, cls.TWITTER_ACCESS_TOKEN_SECRET]):
             pass # Warn or handle downstream

settings = Settings()
