from laganga_bot.publish.twitter import TwitterClient
from laganga_bot.settings import settings
import logging
import sys

# Configure basic logging to see everything
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

def run_test():
    try:
        settings.validate()
        logger.info("Credentials found, initializing TwitterClient...")
        client = TwitterClient()
        
        test_tweet = "Probando la conexión de texto simple a la API de Twitter. Si esto se publica, significa que el error 503 solo ocurre al subir imágenes o recursos multimedia. 🤖🔍"
        logger.info(f"Attempting to post text tweet: '{test_tweet}'")
        
        tweet_id = client.post_tweet(text=test_tweet, image_url=None, discount_percent=None)
        
        if tweet_id:
            logger.info("✅ SUCCESS: Text-only tweet was published without any 503 errors!")
            logger.info(f"Tweet ID: {tweet_id}")
        else:
            logger.error("❌ FAILED: The post_tweet function returned None.")
            
    except Exception as e:
        logger.error(f"❌ ERROR: Publishing test tweet failed: {e}", exc_info=True)

if __name__ == "__main__":
    run_test()
