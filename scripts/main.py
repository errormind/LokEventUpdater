"""
Main entry point for the LokEventUpdater application.
"""

from CollectData import EventCrawler
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = EventCrawler()
    crawler.crawl()
