from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

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

    def get_soup(self, url: str) -> BeautifulSoup | None:
        """
        Fetch a page and return a BeautifulSoup object.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
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