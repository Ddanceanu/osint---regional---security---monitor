import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
import requests
from datetime import datetime
from app.ingestion.base_scraper import BaseScraper


class ChathamHouseScraper(BaseScraper):
    """
    Scraper for Chatham House publications via RSS feed.

    Chatham House publishes expert comments, research papers and analyses
    focused on European security, Russia, Ukraine and Black Sea regional dynamics.

    Unlike other scrapers, this one uses an RSS feed (single request)
    so there is no pagination or parallel fetching needed —
    content comes directly from the feed description field.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="Chatham House",
            source_type="think_tank"
        )
        self.base_url = "https://www.chathamhouse.org"
        self.feed_url = f"{self.base_url}/path/whatsnew.xml"


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse Chatham House date string into datetime.
        Supports ISO with timezone (2026-03-23T15:22:14+00:00) and display format (25 March 2026).
        Returns None on failure.
        """
        if not date_str:
            return None

        # Handle ISO with timezone: strip timezone suffix for parsing
        clean = date_str.strip()
        if "T" in clean:
            clean = clean.split("T")[0]

        for fmt in ("%Y-%m-%d", "%d %B %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue
        return None


    def extract_date_from_description(self, description_raw: str) -> str:
        """
        Extract the publication date from the HTML-encoded RSS description field.
        """
        if not description_raw:
            return ""

        soup = BeautifulSoup(description_raw, "html.parser")
        time_tag = soup.find("time")

        if time_tag:
            return time_tag.get("datetime", "").strip()

        return ""


    def extract_text_from_description(self, description_raw: str) -> str:
        """
        Extract the plain text summary from the HTML-encoded RSS description field.
        """
        if not description_raw:
            return ""

        soup = BeautifulSoup(description_raw, "html.parser")
        paragraphs = soup.find_all("p")
        text_blocks = []

        for p in paragraphs:
            text = p.get_text(" ", strip=True)
            if text:
                text_blocks.append(text)

        return "\n\n".join(text_blocks)


    def fetch_documents(self) -> list[dict]:
        """
        Collect Chatham House publications published within the last LOOKBACK_DAYS.
        Fetches the RSS feed and filters by cutoff date.
        """
        print(f"[Chatham House] Fetching RSS feed: {self.feed_url}")

        try:
            response = requests.get(self.feed_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[Chatham House] Failed to fetch RSS feed: {e}")
            return []

        root = ET.fromstring(response.content)
        channel = root.find("channel")

        if not channel:
            print("[Chatham House] No channel found in RSS feed — stopping.")
            return []

        items = channel.findall("item")
        print(f"[Chatham House] {len(items)} item(s) in feed — filtering by cutoff...")

        documents = []

        for item in items:
            title = item.findtext("title", "").strip()
            url = item.findtext("link", "").strip()

            if not title or not url:
                continue

            description_raw = item.findtext("description", "")
            publication_date = self.extract_date_from_description(description_raw)

            parsed_date = self._parse_date(publication_date)
            if parsed_date is not None and parsed_date < self.cutoff_date:
                continue

            content = self.extract_text_from_description(description_raw)

            documents.append({
                "source_name": self.source_name,
                "source_type": self.source_type,
                "title": title,
                "url": url,
                "publication_date": publication_date,
                "content": content,
            })

        print(f"[Chatham House] Done. Total: {len(documents)} documents.")
        return documents
