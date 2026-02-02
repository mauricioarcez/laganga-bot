import unittest
from unittest.mock import MagicMock, patch
from laganga_bot.domain.models import Deal
from laganga_bot.domain.logic import select_best_deal, filter_posted_deals, format_deal_message

class TestBotFlow(unittest.TestCase):
    
    def setUp(self):
        self.sample_deals = [
            Deal(
                id=1, name="Deal 1", current_price=100.0, original_price=200.0, 
                discount_percent=50, source="Source A", details="Details A", 
                image_url="http://img.com/1", slug="deal-1"
            ),
            Deal(
                id=2, name="Deal 2", current_price=50.0, original_price=100.0, 
                discount_percent=50, source="Source B", details=None, 
                image_url="http://img.com/2", slug="deal-2"
            ),
             Deal(
                id=3, name="Deal 3", current_price=10.0, original_price=100.0, 
                discount_percent=90, source="Source C", details="Details C", 
                image_url="http://img.com/3", slug="deal-3"
            )
        ]

    def test_select_best_deal(self):
        # Should pick Deal 3 (90% off)
        best = select_best_deal(self.sample_deals)
        self.assertEqual(best.id, 3)

    def test_filter_posted_deals(self):
        posted_ids = {"1", "3"}
        valid = filter_posted_deals(self.sample_deals, posted_ids)
        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0].id, 2)

    def test_select_best_deal_skips_posted(self):
        """Test that if the best deal is posted, it is filtered out and the next best is chosen."""
        # Deal 3 is 90% off (Best), Deal 1 is 50% off (Next Best)
        posted_ids = {"3"} # The best one is already posted
        
        valid_deals = filter_posted_deals(self.sample_deals, posted_ids)
        best_deal = select_best_deal(valid_deals)
        
        # Should skip Deal 3 and pick Deal 1
        self.assertEqual(best_deal.id, 1)
        self.assertEqual(best_deal.name, "Deal 1")

    def test_format_message_with_details(self):
        deal = self.sample_deals[0]
        msg = format_deal_message(deal)
        self.assertIn("Details A", msg)
        self.assertIn("Deal 1", msg)
        self.assertIn("50% OFF", msg)

    def test_format_message_without_details(self):
        deal = self.sample_deals[1]
        msg = format_deal_message(deal)
        self.assertNotIn("None", msg) # Ensure None isn't printed
        self.assertIn("Deal 2", msg)

    def test_format_message_exceeds_limit(self):
        """Test that formatting fails if the message exceeds 280 characters."""
        long_name = "A" * 300
        long_deal = Deal(
            id=4, name=long_name, current_price=10.0, original_price=100.0,
            discount_percent=10, source="Source D", details="Details",
            image_url="http://img.com", slug="deal-4"
        )
        
        with self.assertRaises(ValueError) as cm:
            format_deal_message(long_deal)
        
        self.assertIn("Message exceeds 280 character limit", str(cm.exception))

class TestTwitterPublishing(unittest.TestCase):
    
    @patch('laganga_bot.publish.twitter.tweepy.Client')
    @patch('laganga_bot.publish.twitter.tweepy.OAuth1UserHandler')
    @patch('laganga_bot.publish.twitter.tweepy.API')
    @patch('laganga_bot.publish.twitter.requests.get')
    @patch('laganga_bot.publish.twitter.os.remove') # Prevent actual file removal
    @patch('laganga_bot.publish.twitter.tempfile.NamedTemporaryFile')
    def test_post_tweet_with_image_rendering(self, mock_temptool, mock_remove, mock_get, mock_api, mock_auth, mock_client):
        """Test that the image is downloaded and uploaded correctly (rendered)."""
        from laganga_bot.publish.twitter import TwitterClient
        
        # Setup mocks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response

        # Mock temp file
        mock_temp_file = MagicMock()
        mock_temp_file.name = "/tmp/fake_image.jpg"
        mock_temptool.return_value.__enter__.return_value = mock_temp_file
        
        # Mock API media upload
        mock_api_instance = mock_api.return_value
        mock_media = MagicMock()
        mock_media.media_id = "123456"
        mock_api_instance.media_upload.return_value = mock_media

        # Mock Client create_tweet
        mock_client_instance = mock_client.return_value
        mock_tweet_resp = MagicMock()
        mock_tweet_resp.data = {'id': 'tweet_123'}
        mock_client_instance.create_tweet.return_value = mock_tweet_resp

        # Init client (env vars assumed mocked or present, but init might fail if not set in env)
        # We need to mock settings to avoid Init error
        with patch('laganga_bot.publish.twitter.settings') as mock_settings:
            mock_settings.TWITTER_API_KEY = "key"
            mock_settings.TWITTER_API_KEY_SECRET = "secret"
            mock_settings.TWITTER_ACCESS_TOKEN = "token"
            mock_settings.TWITTER_ACCESS_TOKEN_SECRET = "token_secret"
            
            client = TwitterClient()
            client.api = mock_api_instance # Force API mock injection if init created a new one
            
            tweet_id = client.post_tweet("Hello World", image_url="http://example.com/image.jpg")
            
            # 1. Verify Image Download (Rendering check)
            mock_get.assert_called_with("http://example.com/image.jpg", stream=True)
            
            # 2. Verify Temp File Write
            mock_temp_file.write.assert_called_with(b'fake_image_data')
            
            # 3. Verify Media Upload
            mock_api_instance.media_upload.assert_called()
            
            # 4. Verify Tweet Post with Media ID
            mock_client_instance.create_tweet.assert_called_with(
                text="Hello World", 
                media_ids=["123456"]
            )
            self.assertEqual(tweet_id, 'tweet_123')

if __name__ == '__main__':
    unittest.main()
