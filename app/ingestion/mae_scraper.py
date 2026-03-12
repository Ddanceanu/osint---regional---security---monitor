from app.ingestion.base_scraper import BaseScraper
import requests

class MaeScraper(BaseScraper):
    """
    Scraper for Ministry of Foreign Affairs of Romania (MAE).

    The first version only defines the scraper structure.
    Real extraction logic will be added later.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="MAE Romania",
            source_type="official"
        )
        self.base_url = "https://www.mae.ro/en"

    def fetch_documents(self) -> list[dict]:
        """
        Test access to the MAE source and return am empty list for now.
        """

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

        try:
            response = requests.get(self.base_url, headers=headers, timeout = 10)

            print(f"Fetching from: {self.base_url}")
            print(f"Status code: {response.status_code}")

        except requests.RequestException as e:
            print(f"Failed to fetch source: {self.base_url}")
            print(f"Error: {e}")

        return []