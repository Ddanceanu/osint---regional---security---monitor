import time
from app.ingestion.base_scraper import BaseScraper
from datetime import datetime


class EeasScraper(BaseScraper):
    """
    Scraper for EEAS (European External Action Service) press materials.

    EEAS publishes press releases, statements, and council conclusions
    relevant to EU external action, especially regarding the eastern
    neighbourhood, Moldova, Ukraine and regional security.

    Fetches articles sequentially with delays because EEAS aggressively
    rate-limits with 429 responses.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="EEAS",
            source_type="official"
        )
        self.base_url = "https://www.eeas.europa.eu"
        self.listing_url = f"{self.base_url}/eeas/press-material_en"


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse EEAS date string into datetime.
        Supports formats like '26.03.2026', '25 March 2026' and '25/03/2026'.
        Returns None on failure.
        """
        if not date_str:
            return None
        for fmt in ("%d.%m.%Y", "%d %B %Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None


    def _fetch_article_content(self, article_url: str) -> str:
        """
        Extract the main text content from an individual EEAS article page.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return ""

        content_div = soup.find("div", class_="field--name-field-text")
        if not content_div:
            return ""

        paragraphs = content_div.find_all("p")
        text_blocks = []

        for p in paragraphs:
            text = p.get_text("", strip=True)
            if text:
                text_blocks.append(text)

        return "\n\n".join(text_blocks)


    def fetch_documents(self) -> list[dict]:
        """
        Collect EEAS press materials published within the last LOOKBACK_DAYS.
        Uses dynamic pagination — stops when documents older than the cutoff are found.
        Fetches articles sequentially with delays to avoid 429 rate limiting.
        """
        documents = []
        page_num = 0

        while page_num <= self.MAX_PAGES:
            page_url = f"{self.listing_url}?page={page_num}"
            print(f"[EEAS] Fetching page {page_num}: {page_url}")

            soup = self.get_soup(page_url)
            if not soup:
                print(f"[EEAS] Failed to fetch page {page_num} — stopping.")
                break

            cards = soup.find_all("div", class_="card")

            if not cards:
                print(f"[EEAS] No articles on page {page_num} — stopping.")
                break

            # Parse listing metadata
            article_meta = []
            for card in cards:
                title_tag = card.find("h3", class_="card-title")
                if not title_tag:
                    continue

                link = title_tag.find("a")
                if not link:
                    continue

                title = link.get_text(strip=True)
                href = link.get("href", "").strip()

                if not title or not href:
                    continue

                if href.startswith("http"):
                    full_url = href
                else:
                    full_url = f"{self.base_url}{href}"

                # Skip external links (from EU council)
                if "eeas.europa.eu" not in full_url:
                    continue

                publication_date = ""
                footer = card.find("div", class_="card-footer")
                if footer:
                    publication_date = footer.get_text(strip=True)

                article_meta.append((full_url, title, publication_date))

            print(f"[EEAS] Found {len(article_meta)} articles — fetching sequentially...")

            found_older_doc = False
            page_docs = []

            for full_url, title, publication_date in article_meta:
                parsed_date = self._parse_date(publication_date)

                if parsed_date is not None and parsed_date < self.cutoff_date:
                    found_older_doc = True
                    continue

                content = self._fetch_article_content(full_url)
                time.sleep(4)

                page_docs.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content,
                })

            documents.extend(page_docs)
            print(f"[EEAS] Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[EEAS] Reached cutoff date on page {page_num} — stopping.")
                break

            time.sleep(5)
            page_num += 1

        print(f"[EEAS] Done. Total: {len(documents)} documents.")
        return documents
