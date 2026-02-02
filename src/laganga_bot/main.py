import argparse
import sys
import logging

from laganga_bot.logging import setup_logging
from laganga_bot.state.sqlite_store import SQLiteStore
from laganga_bot.fetch.endpoint import fetch_flash_deals
from laganga_bot.domain.logic import select_best_deal, format_deal_message
from laganga_bot.publish.twitter import TwitterClient
from laganga_bot.settings import settings

# Setup logging first
logger = setup_logging()

def main():
    parser = argparse.ArgumentParser(description="La Ganga Bot")
    parser.add_argument("--clear-db", action="store_true", help="Clear the posted deals database")
    args = parser.parse_args()

    try:
        # Initialize components
        store = SQLiteStore()
        
        if args.clear_db:
            logger.info("Clearing database as requested...")
            store.clear_history()
            return

        # 1. Fetch
        logger.info("Fetching flash deals...")
        deals = fetch_flash_deals()
        if not deals:
            logger.info("No flash deals found.")
            return

        # 2. Filter
        # We need a way to check efficiently. 
        # Logic module says `filter_posted_deals(deals, posted_ids)`.
        # But Store only provides `is_posted(id)`.
        # We can iterate and filter.
        # Ideally, we should modify Logic to accept the store or valid deals.
        # Let's simple iterate here or update logic to use store. 
        # For now, let's keep logic simple:
        
        target_deal = None
        
        # Sort first to prioritize best deals before checking DB (optimization)? 
        # No, check DB first to avoid processing things we did.
        # Better: Select best from ALL, then check if posted? 
        # If best is posted, pick second best? Yes.
        
        # Sort all deals
        # Using domain logic to select best from a list
        # But we need to exclude posted ones.
        
        valid_deals = []
        for deal in deals:
            if not store.is_posted(deal.id):
                valid_deals.append(deal)
        
        if not valid_deals:
            logger.info("No new deals to post.")
            return
            
        target_deal = select_best_deal(valid_deals)
        
        if not target_deal:
             logger.info("No target deal selected.")
             return

        logger.info(f"Selected deal: {target_deal.name} ({target_deal.discount_percent}% OFF)")
        
        # 3. Format
        message = format_deal_message(target_deal)
        
        if settings.DRY_RUN:
            logger.info(f"[DRY RUN] Would post deal: {target_deal.name}")
            logger.info(f"[DRY RUN] Message:\n{message}")
            logger.info("[DRY RUN] Skipping Twitter post and DB update.")
            return

        # 4. Post
        twitter = TwitterClient()
        twitter.post_tweet(
            message, 
            image_url=target_deal.image_url, 
            discount_percent=target_deal.discount_percent
        )
        
        # 5. Persist
        store.mark_as_posted(target_deal.id)
        
    except Exception as e:
        logger.error(f"Bot failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
