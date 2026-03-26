import time
from app.ingestion.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import cloudscraper
from urllib.parse import urljoin


class EuCouncilScraper(BaseScraper):
    """
    Scraper for EU Council (Consilium) press releases.

    Uses cloudscraper instead of requests because
    consilium.europa.eu has browser-check protection
    that blocks standard HTTP requests.

    Fetches articles sequentially (no threading) to avoid
    triggering rate limits or browser-check failures.
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
        Retries with exponential backoff on 429 and 403 errors.

        This replaces BaseScraper.get_soup() for this source only,
        because consilium.europa.eu requires cloudscraper to bypass
        browser-check protection.
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self.scraper.get(url, timeout=10)
                if response.status_code in (429, 403) and attempt < self.MAX_RETRIES:
                    wait = 2 ** attempt
                    print(f"[{self.source_name}] {response.status_code} — retrying in {wait}s (attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                if attempt < self.MAX_RETRIES and ("429" in str(e) or "403" in str(e)):
                    wait = 2 ** attempt
                    print(f"[{self.source_name}] {e} — retrying in {wait}s (attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                print(f"Failed to fetch page: {url}")
                print(f"Exception: {e}")
                return None


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse EU Council date string into datetime.
        Supports API format (3/24/2026 3:10:00 PM), ISO, and display formats.
        Returns None on failure.
        """
        if not date_str:
            return None
        for fmt in ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y", "%Y-%m-%d", "%d %B %Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None


    def _fetch_article_content(self, article_url: str) -> str:
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


    def fetch_documents(self) -> list[dict]:
        """
        Collect EU Council press releases published within the last LOOKBACK_DAYS.
        Uses dynamic pagination — stops when documents older than the cutoff are found.
        Fetches articles sequentially to avoid browser-check failures.
        """
        documents = []
        page_num = 1

        while page_num <= self.MAX_PAGES:
            page_url = f"{self.listing_url}?Page={page_num}"
            print(f"[EU Council] Fetching page {page_num}: {page_url}")

            soup = self.get_soup_cs(page_url)
            if not soup:
                print(f"[EU Council] Failed to fetch page {page_num} — stopping.")
                break

            items = soup.find_all("a", class_="gsc-excerpt-item__link")

            if not items:
                print(f"[EU Council] No articles on page {page_num} — stopping.")
                break

            # Parse listing metadata
            article_meta = []
            for item in items:
                title_tag = item.find("span", class_="gsc-excerpt-item__title")
                time_tag = item.find("time")
                href = item.get("href", "").strip()

                title = title_tag.get_text(strip=True) if title_tag else ""
                publication_date = time_tag.get("datetime", "").strip() if time_tag else ""

                if not title or not href:
                    continue

                full_url = urljoin(self.base_url, href)
                article_meta.append((full_url, title, publication_date))

            print(f"[EU Council] Found {len(article_meta)} articles — fetching sequentially...")

            found_older_doc = False
            page_docs = []

            for full_url, title, publication_date in article_meta:
                parsed_date = self._parse_date(publication_date)

                if parsed_date is not None and parsed_date < self.cutoff_date:
                    found_older_doc = True
                    continue

                content = self._fetch_article_content(full_url)
                time.sleep(1)

                page_docs.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content,
                })

            documents.extend(page_docs)
            print(f"[EU Council] Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[EU Council] Reached cutoff date on page {page_num} — stopping.")
                break

            page_num += 1

        print(f"[EU Council] Done. Total: {len(documents)} documents.")
        return documents
