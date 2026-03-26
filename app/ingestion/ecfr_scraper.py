from app.ingestion.base_scraper import BaseScraper
from datetime import datetime


class EcfrScraper(BaseScraper):
    """
    Scraper for ECFR (European Council on Foreign Relations) publications.

    ECFR publishes policy briefs, commentaries and analyses
    focused on European foreign policy, the eastern neighbourhood,
    Moldova, Ukraine and EU strategic positioning.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="ECFR",
            source_type="think_tank"
        )
        self.base_url = "https://ecfr.eu"
        self.listing_url = f"{self.base_url}/publications/"


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse ECFR date string into datetime.
        Supports formats like '25 March 2026' and '2026-03-25'.
        Returns None on failure.
        """
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %B %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None


    def _fetch_article_content(self, article_url: str) -> str:
        """
        Extract the main text content from an individual ECFR article page.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return ""

        content_div = soup.find("div", class_="text-body")
        if not content_div:
            return ""

        paragraphs = content_div.find_all("p")
        text_blocks = []

        for p in paragraphs:
            text = p.get_text(" ", strip=True)
            if text:
                text_blocks.append(text)

        return "\n\n".join(text_blocks)


    def fetch_documents(self) -> list[dict]:
        """
        Collect ECFR publications published within the last LOOKBACK_DAYS.
        Uses dynamic pagination — stops when documents older than the cutoff are found.
        """
        documents = []
        page_num = 1

        while page_num <= self.MAX_PAGES:
            page_url = self.listing_url if page_num == 1 else f"{self.listing_url}page/{page_num}"
            print(f"[ECFR] Fetching page {page_num}: {page_url}")

            soup = self.get_soup(page_url)
            if not soup:
                print(f"[ECFR] Failed to fetch page {page_num} — stopping.")
                break

            cards = soup.find_all("article")

            if not cards:
                print(f"[ECFR] No articles on page {page_num} — stopping.")
                break

            # Parse listing metadata
            article_meta = []
            for card in cards:
                title_tag = card.find("h2", class_="post-title")
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

                publication_date = ""
                time_tag = card.find("time")
                if time_tag:
                    publication_date = time_tag.get("datetime", "").strip()
                    if not publication_date:
                        publication_date = time_tag.get_text(strip=True)

                article_meta.append((full_url, title, publication_date))

            print(f"[ECFR] Found {len(article_meta)} articles — fetching sequentially...")

            found_older_doc = False
            page_docs = []

            for full_url, title, publication_date in article_meta:
                parsed_date = self._parse_date(publication_date)

                if parsed_date is not None and parsed_date < self.cutoff_date:
                    found_older_doc = True
                    continue

                content = self._fetch_article_content(full_url)

                page_docs.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content,
                })

            documents.extend(page_docs)
            print(f"[ECFR] Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[ECFR] Reached cutoff date on page {page_num} — stopping.")
                break

            page_num += 1

        print(f"[ECFR] Done. Total: {len(documents)} documents.")
        return documents
