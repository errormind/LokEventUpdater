"""
Collects the data from LOK Kulturzentrum and stores it as a local copy for easier use of the media.
The webiste to crawl through is https://www.lok-jever.de/programm
The data is stored in a subfolder next to the run.bat script.
"""

import requests
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventCrawler:
    """Web crawler for LOK Kulturzentrum events."""
    
    BASE_URL = "https://www.lok-jever.de/programm"
    API_URL_TEMPLATE = "https://www.lok-jever.de/gutesio/operator/showcase_child_list_data/{offset}"
    API_MODULE_ID = 70
    API_PAGE_SIZE = 30
    OUTPUT_DIR = Path(__file__).parent.parent / "data"
    
    def __init__(self):
        """Initialize the crawler."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self._setup_output_dir()
    
    def _setup_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.OUTPUT_DIR}")
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def fetch_event_items(self, offset: int = 0) -> List[Dict]:
        """
        Fetch one page of event items from the site's async API.

        Args:
            offset: Numeric offset for pagination.

        Returns:
            List of raw event objects.
        """
        url = self.API_URL_TEMPLATE.format(offset=offset)
        try:
            logger.info(f"Fetching events API page: {url}")
            response = self.session.get(
                url,
                params={"moduleId": self.API_MODULE_ID},
                timeout=10
            )
            response.raise_for_status()
            items = response.json()
            if isinstance(items, list):
                logger.info(f"Fetched {len(items)} events from offset {offset}")
                return items
            logger.error("Unexpected JSON structure from event API")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch event API page {offset}: {e}")
        except ValueError as e:
            logger.error(f"Failed to parse JSON from event API page {offset}: {e}")
        return []

    def fetch_all_event_items(self) -> List[Dict]:
        """
        Fetch all event items from the paginated async API.

        Returns:
            List of raw event objects.
        """
        offset = 0
        all_items = []
        while True:
            items = self.fetch_event_items(offset)
            if not items:
                break
            all_items.extend(items)
            if len(items) < self.API_PAGE_SIZE:
                break
            offset += self.API_PAGE_SIZE
        logger.info(f"Total API events fetched: {len(all_items)}")
        return all_items

    def parse_events(self) -> List[Dict]:
        """
        Parse event data from the site's async API.

        Returns:
            List of event dictionaries
        """
        events = []
        raw_items = self.fetch_all_event_items()
        for item in raw_items:
            try:
                event = {
                    'title': item.get('name'),
                    'date': item.get('beginDateDisplay') or None,
                    'time': item.get('beginTimeDisplay') or None,
                    'location': item.get('locationElementName') or item.get('locationCity'),
                    'description': item.get('shortDescription') or None,
                    'url': item.get('childLink') or item.get('foreignLink') or item.get('elementLink'),
                    'ticket_url': item.get('foreignLink') or None,
                    'type': item.get('typeName') or item.get('type'),
                    'price': item.get('eventPrice') or None,
                    'fetched_at': datetime.now().isoformat(),
                    'raw': item,
                }
                events.append(event)
            except Exception as e:
                logger.error(f"Error converting API item to event: {e}")
        logger.info(f"Parsed {len(events)} events from API")
        return events
    
    def save_event(self, event: Dict, do_update: bool) -> bool:
        """
        Save a single event to a JSON file in a folder named after the event date and title.
        
        Args:
            event: Event dictionary
            do_update: Whether to update existing events or overwrite them
        Returns:
            True if successful, False otherwise
        """
        try:
            date_str = event['date'] or "undated"
            # Try to cenvert date to YYYY-MM-DD format for better sorting, if possible
            try:
                date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                date_str = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
            title_str = event['title'] or "untitled"
            safe_title = "".join(c for c in title_str if c.isalnum() or c in (' ', '_')).rstrip()
            folder_name = f"{date_str}_{safe_title}"
            folder_path = self.OUTPUT_DIR / folder_name
            # Create folder for the event
            # If the folder already exists and do_update is False, skip saving this event
            if folder_path.exists() and not do_update:
                logger.info(f"Skipping existing event (do_update=False): {event['title']}")
                return True
            folder_path.mkdir(parents=True, exist_ok=True)

            data_filepath = folder_path / "data.json"
            with open(data_filepath, 'w', encoding='utf-8') as f:
                json.dump(event, f, indent=2, ensure_ascii=False)

            # Download imageCDN and save it in the same folder if available
            image_url = event['raw'].get('imageCDN')
            if image_url:
                try:
                    logger.info(f"Downloading image for event '{event['title']}': {image_url}")
                    img_response = self.session.get(image_url, timeout=10)
                    img_response.raise_for_status()
                    img_extension = image_url.split('.')[-1].split('?')[0]  # Get extension from URL
                    img_filename = folder_path / f"image.{img_extension}"
                    with open(img_filename, 'wb') as img_file:
                        img_file.write(img_response.content)
                    logger.info(f"Saved image to {img_filename}")
                except requests.RequestException as e:
                    logger.error(f"Failed to download image for event '{event['title']}': {e}")
            logger.info(f"Saved event '{event['title']}' to {data_filepath}")

            # For easier reading, also have the title, date, time, description, type in a txt file
            txt_filepath = folder_path / "info.txt"
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {event['title']}\n")
                f.write(f"Date: {event['date']}\n")
                f.write(f"Time: {event['time']}\n")
                f.write(f"Location: {event['location']}\n")
                f.write(f"Type: {event['type']}\n")
                f.write(f"Price: {event['price']}\n")
                f.write(f"Description: {event['description']}\n")
                f.write(f"URL: {event['url']}\n")
                f.write(f"Ticket URL: {event['ticket_url']}\n")
            return True
        except Exception as e:
            logger.error(f"Error saving event '{event.get('title', 'unknown')}': {e}")
            return False

    def save_events(self, events: List[Dict], do_update: bool, filename: str = "events.json") -> bool:
        """
        Save events to JSON file. Also saves the event in a folder containing the downloaded image and the data of the event in a file named data.json. 
        The folder is named after the event date and title.
        
        Args:
            events: List of event dictionaries
            do_update: Whether to update existing events or overwrite them
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Dont save all events in one file, but save each event in a separate folder with its data and image
            #filepath = self.OUTPUT_DIR / filename
            #with open(filepath, 'w', encoding='utf-8') as f:
            #    json.dump(events, f, indent=2, ensure_ascii=False)
            #logger.info(f"Saved {len(events)} events to {filepath}")

            # Save all events to folders with their data and images
            ret = True
            for event in events:
                if not self.save_event(event, do_update):
                    logger.error(f"Failed to save event: {event.get('title', 'unknown')}")
                    ret = False
            return ret
        except Exception as e:
            logger.error(f"Error saving events: {e}")
            return False
    
    def crawl(self, do_update : bool = False) -> bool:
        """
        Main crawling method.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting crawl...")
        
        html = self.fetch_page(self.BASE_URL)
        if not html:
            logger.error("Failed to fetch page")
            return False
        
        events = self.parse_events()
        if not events:
            logger.warning("No events found")
            return False
        
        success = self.save_events(events, do_update)
        
        logger.info("Crawl completed")
        return success


def main():
    """Main entry point."""
    crawler = EventCrawler()
    crawler.crawl()

if __name__ == "__main__":
    main()