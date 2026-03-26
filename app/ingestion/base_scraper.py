from abc import ABC, abstractmethod
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class BaseScraper(ABC):
    """
    Base class for all source scrapers used in the project.

    Each scraper must define:
    - source name
    - source_type
    - fetch_documents()

    The role of a scraper is to collect initial document metadata
    from a public source, without performing NLP or deeper analysis.
    """

    LOOKBACK_DAYS: int = 90  # set the time for collecting documents (90 days back from now)
    MAX_PAGES: int = 50      # safety limit to prevent infinite pagination
    MAX_RETRIES: int = 3     # retry attempts for rate-limited (429) requests

    def __init__(self, source_name: str, source_type: str) -> None:
        self.source_name = source_name
        self.source_type = source_type
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        self.cutoff_date = datetime.now() - timedelta(days=self.LOOKBACK_DAYS)

    def get_soup(self, url: str) -> BeautifulSoup | None:
        """
        Fetch a page and return a BeautifulSoup object.
        Retries with exponential backoff on 429 (Too Many Requests).
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 429 and attempt < self.MAX_RETRIES:
                    wait = 2 ** attempt
                    print(f"[{self.source_name}] 429 rate limited — retrying in {wait}s (attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")
            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES and "429" in str(e):
                    wait = 2 ** attempt
                    print(f"[{self.source_name}] 429 rate limited — retrying in {wait}s (attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                print(f"Failed to fetch page: {url}")
                print(f"Error: {e}")
                return None

    @abstractmethod
    def fetch_documents(self) -> list[dict]:
        """
        Return a list of document candidates from the source.

        Each document should include at least:
        - source_name
        - source_type
        - title
        - URL
        - publication_date
        """
        pass