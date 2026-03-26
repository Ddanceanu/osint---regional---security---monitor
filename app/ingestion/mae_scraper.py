from app.ingestion.base_scraper import BaseScraper
from datetime import datetime


class MaeScraper(BaseScraper):
    """
    Scraper for the Ministry of Foreign Affairs of Romania (MAE).

    The scraper collects article candidates from the MAE press releases page
    and builds standardized document records with basic metadata.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="MAE Romania",
            source_type="official"
        )
        self.base_url = "https://www.mae.ro/en/taxonomy/term/952"


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse MAE date string (MM/DD/YY) into datetime.
        Returns None on failure.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), "%m/%d/%y")
        except ValueError:
            return None


    def _fetch_article(self, article_url: str) -> dict:
        """
        Fetch a single article page and extract date and content in one request.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return {"publication_date": None, "content": ""}

        publication_date = None
        date_fields = soup.find_all(
            "div",
            class_="field field-type-text field-field-date"
        )
        if date_fields:
            raw_text = date_fields[0].get_text(" ", strip=True)
            publication_date = raw_text.replace("Date:", "").strip()

        content = ""
        article_container = soup.select_one("div.art")
        if article_container:
            paragraphs = []
            for p in article_container.find_all("p", recursive=False):
                text = p.get_text(" ", strip=True).replace("\xa0", " ").strip()
                if text and text != "&nbsp;":
                    paragraphs.append(text)
            content = "\n\n".join(paragraphs).strip()

        return {
            "publication_date": publication_date,
            "content": content
        }


    def _collect_links_from_page(self, soup) -> list[tuple[str, str]]:
        """
        Extract unique (href, title) pairs from a listing page.
        Deduplicates by href since the same article can appear in multiple <a> tags.
        """
        seen = set()
        results = []
        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if "/en/node/" in href and len(text) >= 30 and href not in seen:
                seen.add(href)
                results.append((href, text))

        return results


    def fetch_documents(self) -> list[dict]:
        """
        Collect MAE press releases published within the last LOOKBACK_DAYS.
        """
        documents = []
        seen_hrefs = set()
        page_num = 0

        while page_num <= self.MAX_PAGES:
            page_url = self.base_url if page_num == 0 else f"{self.base_url}?page={page_num}"
            print(f"[MAE] Fetching page {page_num}: {page_url}")

            soup = self.get_soup(page_url)
            if not soup:
                print(f"[MAE] Failed to fetch page {page_num} - stopping.")
                break

            raw_links = self._collect_links_from_page(soup)
            new_links = [(href, text) for href, text in raw_links if href not in seen_hrefs]

            if not new_links:
                print(f"[MAE] No new links on page {page_num} - stopping.")
                break

            for href, _ in new_links:
                seen_hrefs.add(href)

            print(f"[MAE] Found {len(new_links)} articles — fetching sequentially...")
            found_older_doc = False
            page_docs = []

            for href, title in new_links:
                article_url = f"https://www.mae.ro{href}"
                result = self._fetch_article(article_url)

                parsed_date = self._parse_date(result["publication_date"])

                if parsed_date is not None and parsed_date < self.cutoff_date:
                    found_older_doc = True
                    continue

                page_docs.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": article_url,
                    "publication_date": result["publication_date"],
                    "content": result["content"],
                })

            documents.extend(page_docs)
            print(f"[MAE] Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[MAE] Reached cutoff date on page {page_num} - stopping.")
                break

            page_num += 1

        print(f"[MAE] Done. Total: {len(documents)} documents.")
        return documents
