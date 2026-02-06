from typing import List, Optional
from laganga_bot.domain.models import Deal
from laganga_bot.domain.templates import TWITTER_FLASH_DEAL_TEMPLATE

def filter_posted_deals(deals: List[Deal], posted_ids: set) -> List[Deal]:
    """Filters out deals whose IDs are in the posted_ids set."""
    return [d for d in deals if str(d.id) not in posted_ids]

def select_best_deal(deals: List[Deal]) -> Optional[Deal]:
    """Selects the best deal (highest discount)."""
    if not deals:
        return None
    # Sort by discount percent descending
    sorted_deals = sorted(deals, key=lambda x: x.discount_percent, reverse=True)
    return sorted_deals[0]

def format_deal_message(deal: Deal) -> str:
    """Formats the deal into a tweet message."""
    details_text = deal.details if deal.details else ""
    
    # Format price as integer to avoid unnecessary decimals (e.g., 19999.0 -> 19999)
    price_formatted = int(deal.current_price)
    
    # Format store name in uppercase and discount as integer
    source_formatted = deal.source.upper()
    discount_formatted = int(deal.discount_percent)
    
    def render_message(name_val: str, details_val: str) -> str:
        return TWITTER_FLASH_DEAL_TEMPLATE.format(
            source=source_formatted,
            discount_percent=discount_formatted,
            name=name_val,
            current_price=price_formatted,
            details=details_val,
            slug=deal.slug,
            image_url=""
        ).replace("{image_url}", "").strip()

    # Strategy 1: Full message
    formatted_message = render_message(deal.name, details_text)
    if len(formatted_message) <= 280:
        return formatted_message

    # Strategy 2: Truncate name to 3 words
    short_name = " ".join(deal.name.split()[:3])
    formatted_message = render_message(short_name, details_text)
    if len(formatted_message) <= 280:
        return formatted_message

    # Strategy 3: Truncate details to 3 words
    short_details = " ".join(details_text.split()[:3])
    formatted_message = render_message(short_name, short_details)
    if len(formatted_message) <= 280:
        return formatted_message

    # Strategy 4: Remove image_url (Already handled by passing empty string, 
    # but strictly following user priority list if we had content there)
    
    if len(formatted_message) > 280:
        raise ValueError(f"Message exceeds 280 character limit: {len(formatted_message)} chars")

    return formatted_message
