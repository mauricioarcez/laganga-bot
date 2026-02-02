import tweepy
import logging
import os
import requests
import tempfile
from typing import Optional

from laganga_bot.settings import settings

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        # OAuth 1.0a User Context (Required for Media Upload v1.1)
        consumer_key = settings.TWITTER_API_KEY
        consumer_secret = settings.TWITTER_API_KEY_SECRET
        access_token = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Missing Twitter API credentials (API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET) in settings.")

        # Client for v2 endpoints (Posting tweets)
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # API for v1.1 endpoints (Media Upload)
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)

    def post_tweet(self, text: str, image_url: str = None) -> Optional[str]:
        """
        Posts a tweet. If image_url is provided, uploads the image first.
        Returns the tweet ID.
        """
        try:
            media_ids = []
            if image_url:
                # Download image to temp file
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_img:
                        temp_img.write(response.content)
                        temp_path = temp_img.name
                    
                    try:
                        # Upload media
                        media = self.api.media_upload(filename=temp_path)
                        media_ids.append(media.media_id)
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    logger.warning(f"Failed to download image from {image_url}")

            response = self.client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
            logger.info(f"Tweet posted successfully. ID: {response.data['id']}")
            return response.data['id']
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise
