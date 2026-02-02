import requests
import logging
from typing import List

from laganga_bot.settings import settings
from laganga_bot.domain.models import Deal

logger = logging.getLogger(__name__)

def fetch_flash_deals(limit: int = 20) -> List[Deal]:
    try:
        settings.validate() 
        
        response = requests.get(settings.FLASH_DEALS_API_URL, params={"limit": limit})
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
        logger.error(f"Error fetching flash deals: {e}")
        return []
