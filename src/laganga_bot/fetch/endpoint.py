import requests
import logging
from typing import List
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from laganga_bot.settings import settings
from laganga_bot.domain.models import Deal

logger = logging.getLogger(__name__)

def get_retrying_session() -> requests.Session:
    """Configures a session with retry logic for transient errors."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,  # Waits: 2s, 4s, 8s...
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def fetch_flash_deals(limit: int = 20) -> List[Deal]:
    try:
        settings.validate() 
        
        session = get_retrying_session()
        response = session.get(
            settings.FLASH_DEALS_API_URL, 
            params={"limit": limit},
            timeout=30 # Increased timeout for cold starts
        )
        response.raise_for_status()
        data = response.json()
        
        deals = []
        for item in data.get("items", []):
            try:
                deal = Deal(
                    id=item["id"],
                    name=item["name"],
                    current_price=item["current_price"],
                    original_price=item["original_price"],
                    discount_percent=item["discount_percent"],
                    source=item["source"],
                    details=item.get("details"),
                    image_url=item["image_url"],
                    slug=item["slug"]
                )
                deals.append(deal)
            except KeyError as e:
                logger.warning(f"Skipping deal due to missing key: {e}. Item: {item}")
                
        return deals
    except Exception as e:
        logger.error(f"Error fetching flash deals after retries: {e}")
        return []
