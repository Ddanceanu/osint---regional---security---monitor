from app.ingestion.base_scraper import BaseScraper
from datetime import datetime


class IswScraper(BaseScraper):
    """
    Scraper for ISW (Institute for the Study of War) research reports.

    ISW publishes daily campaign assessments and analyses focused on
    the Russia-Ukraine conflict, relevant to the eastern flank and
    regional security dynamics monitored by this project.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="ISW",
            source_type="think_tank"
        )
        self.base_url = "https://understandingwar.org"
        self.listing_url = f"{self.base_url}/research/"
        self.relevant_tags = {"RUSSIA & UKRAINE", "UKRAINE"}


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse ISW date string into datetime.
        Supports formats like 'March 25, 2026' and '25 March 2026'.
        Returns None on failure.
        """
        if not date_str:
            return None
        for fmt in ("%b %d, %Y", "%B %d, %Y", "%d %B %Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None


    def is_relevant(self, card) -> bool:
        """
        Return True if the card contains at least one relevant tag.

        Only articles tagged with 'RUSSIA & UKRAINE' or 'UKRAINE'
        are considered relevant for this project.
        """
        tag_elements = card.find_all("p", class_="tag-cloud-on-cards")

        for tag_element in tag_elements:
            tag_text = tag_element.get_text(strip=True).upper()
            if tag_text in self.relevant_tags:
                return True

        return False


    def _fetch_article_content(self, article_url: str) -> str:
        """
        Extract the main text content from an individual ISW article page.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return ""

        content_div = soup.find("div", class_="dynamic-entry-content")
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
        Collect ISW Russia-Ukraine reports published within the last LOOKBACK_DAYS.
        Uses dynamic pagination — stops when documents older than the cutoff are found.
        """
        documents = []
        page_num = 1

        while page_num <= self.MAX_PAGES:
            page_url = self.listing_url if page_num == 1 else f"{self.listing_url}?_paged={page_num}"
            print(f"[ISW] Fetching page {page_num}: {page_url}")

            soup = self.get_soup(page_url)
            if not soup:
                print(f"[ISW] Failed to fetch page {page_num} — stopping.")
                break

            cards = soup.find_all("div", class_="research-card-loop-item-3colgrid")

            if not cards:
                print(f"[ISW] No articles on page {page_num} — stopping.")
                break

            print(f"[ISW] Found {len(cards)} cards — filtering relevant articles...")

            # Parse listing metadata, applying relevance filter
            article_meta = []
            for card in cards:
                if not self.is_relevant(card):
                    continue

                title_tag = card.find("h3", class_="research-card-title")
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
                date_tag = card.find("p", class_="research-card-post-date")
                if date_tag:
                    publication_date = date_tag.get_text(strip=True)

                article_meta.append((full_url, title, publication_date))

            if not article_meta:
                print(f"[ISW] No relevant articles on page {page_num} — stopping.")
                break

            print(f"[ISW] {len(article_meta)} relevant article(s) — fetching sequentially...")

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
            print(f"[ISW] Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[ISW] Reached cutoff date on page {page_num} — stopping.")
                break

            page_num += 1

        print(f"[ISW] Done. Total: {len(documents)} documents.")
        return documents
