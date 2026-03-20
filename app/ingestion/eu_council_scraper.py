from app.ingestion.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import cloudscraper
from urllib.parse import urljoin

class EuCouncilScraper(BaseScraper):
    """
    Scraper for EU Council (Consilium) press releases.

    Uses couldscraper instead of requests because
    consilium.europa.eu has browser-check protection
    that blocks standard HTTP requests.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="EU Council",
            source_type="official"
        )
        self.base_url = "https://www.consilium.europa.eu"
        self.listing_url = "https://www.consilium.europa.eu/en/press/press-releases/"
        self.scraper = cloudscraper.create_scraper()


    def get_soup_cs(self, url: str) -> BeautifulSoup | None:
        """
        Fetch a page using cloudscraper and return a BeautifulSoup object.

        This replaces BaseScraper.get_soup() for this source only,
        because consilium.europa.eu requires cloudscraper to bypass
        browser-check protection.
        """
        try:
            response = self.scraper.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"Failed to fetch page: {url}")
            print(f"Exception: {e}")
            return None

    def fetch_documents(self) -> list[dict]:
        """
        Fetch press releases from multiple pages of the EU Council listing
        and convert them to the standard document format.
        """
        documents = []
        total_pages = 3

        for page_num in range(1, total_pages + 1):
            page_url = f"{self.listing_url}?Page={page_num}"
            soup = self.get_soup_cs(page_url)

            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue

            items = soup.find_all("a", class_="gsc-excerpt-item__link")
            print(f"Page {page_num}: {len(items)} articles found")

            for item in items:
                title_tag = item.find("span", class_="gsc-excerpt-item__title")
                time_tag = item.find("time")
                href = item.get("href", "").strip()

                title = title_tag.get_text(strip=True) if title_tag else ""
                publication_date = time_tag.get("datetime", "").strip() if time_tag else ""

                if not title or not href:
                    continue

                full_url = urljoin(self.base_url, href)
                content = self.extract_content(full_url)

                documents.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content,
                })

        return documents

    def extract_content(self, article_url: str) -> str:
        """
        Extract the main text content from an individual EU Council article page.
        Returns the article text, or an empty string if extraction fails.
        """
        soup = self.get_soup_cs(article_url)
        if not soup:
            return ""

        content_div = soup.find("div", class_="gsc-bge-grid__area")
        if content_div:
            return content_div.get_text(" ", strip=True)

        return ""

