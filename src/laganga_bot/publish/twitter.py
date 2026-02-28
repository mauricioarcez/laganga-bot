
import mimetypes
import tweepy
import logging
import os
import requests
import tempfile
import time
from typing import Optional

from laganga_bot.settings import settings
from laganga_bot.publish.image_processor import process_deal_image

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

    def post_tweet(self, text: str, image_url: str = None, discount_percent: int = None) -> Optional[str]:
        """
        Posts a tweet. If image_url is provided, uploads the image first.
        If discount_percent is provided, overlays it on the image.
        Returns the tweet ID.
        """
        try:
            media_ids = []
            if image_url:
                # Download image to temp file with retry logic
                from laganga_bot.fetch.endpoint import get_retrying_session
                session = get_retrying_session()
                
                response = session.get(image_url, stream=True, timeout=30)
                if response.status_code == 200:
                    # Guess extension based on content type
                    content_type = response.headers.get('content-type')
                    extension = mimetypes.guess_extension(content_type)
                    if not extension:
                        # Fallback to .jpg if unknown
                        extension = ".jpg"

                    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_img:
                        temp_img.write(response.content)
                        temp_path = temp_img.name
                    
                    try:
                        # Process image (add overlay) if we have the needed info
                        if discount_percent is not None:
                            process_deal_image(temp_path, discount_percent)

                        # Upload media
                        # We also wrap the media upload in retry logic occasionally, but main issue was tweet creation
                        max_upload_retries = 3
                        for attempt in range(max_upload_retries):
                            try:
                                media = self.api.media_upload(filename=temp_path)
                                media_ids.append(media.media_id)
                                break
                            except tweepy.errors.TwitterServerError as e:
                                if attempt < max_upload_retries - 1:
                                    wait_time = (2 ** attempt) * 5
                                    logger.warning(f"Twitter server error on image upload ({e}), retrying in {wait_time}s...")
                                    time.sleep(wait_time)
                                else:
                                    raise
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    logger.warning(f"Failed to download image from {image_url}")

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
                    logger.info(f"Tweet posted successfully. ID: {response.data['id']}")
                    return response.data['id']
                except tweepy.errors.TwitterServerError as e:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5
                        logger.warning(f"Twitter server error on tweet creation ({e}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
                except tweepy.errors.TooManyRequests as e:
                    if attempt < max_retries - 1:
                        wait_time = 30
                        logger.warning(f"Rate limited by Twitter, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise
