from app.ingestion.base_scraper import BaseScraper
import requests
from urllib.parse import urljoin

class NatoScraper(BaseScraper):
    """
    Scraper for NATO official media advisories.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="NATO",
            source_type="official"
        )

        self.base_url = "https://www.nato.int"
        self.api_url = (
            "https://www.nato.int/content/nato/en/news-and-events/events/"
            "media-advisories/jcr:content/root/container/"
            "general_search.search.json?query=&searchType=wcm&sortBy=dateDesc"
            "&pageSize=25&page=1&tags=&languages=&startDate=&endDate="
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

    def fetch_documents(self) -> list[dict]:
        """
        Fetch NATO media advisories from the JSON search endpoint
        and convert them to the standard document format.
        """
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            pages = data.get("pages", [])

            documents = []

            for page in pages:
                title = page.get("title", "").strip()
                relative_link = page.get("link", "").strip()
                publication_date = page.get("pageDate", "").strip()

                if not title or not relative_link:
                    continue

                full_url = urljoin(self.base_url, relative_link)

                documents.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date
                }
                )
            return documents
        except requests.RequestException as e:
            print(f"Failed to fetch source: {self.api_url}")
            print(f"Error: {e}")
            return []
        except ValueError as e:
            print("Response is not valid JSON")
            print(f"Error: {e}")
            return []