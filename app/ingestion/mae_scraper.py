from app.ingestion.base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup

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
        self.base_url = "https://www.mae.ro/en/taxonomy/term/952"

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
            soup = BeautifulSoup(response.text, "html.parser")

            if soup.title:
                print(f"Page title: {soup.title.get_text(strip=True)}") # scrip=True ia textul curat din tag
            else:
                print("Page title not found.")

            links = soup.find_all("a")

            print(f"Total links found on page: {len(links)}")

            for link in links[:30]:
                text = link.get_text(strip=True)
                href = link.get("href")
                print(f"Link text: {text} | href: {href}")

            article_candidates = []
            seen_hrefs = set()

            for link in links:
                href = link.get("href")
                text = link.get_text(strip=True)

                if href and "/en/node" in href and len(text) >= 30:
                    if href not in seen_hrefs:
                        article_candidates.append((text, href))
                        seen_hrefs.add(href)

            print(f"Potential article candidates found: {len(article_candidates)}")

            for text, href in article_candidates[:15]:
                print(f"Candidate title: {text} | href: {href}")

            documents = []
            for title, href in article_candidates:
                document = {
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": f"https://www.mae.ro{href}",
                    "publication_date": None,
                }
                documents.append(document)

            print(f"Standardized documents created: {len(documents)}")

            for document in documents[:5]:
                print(document)

            return documents

        except requests.RequestException as e:
            print(f"Failed to fetch source: {self.base_url}")
            print(f"Error: {e}")

        return []