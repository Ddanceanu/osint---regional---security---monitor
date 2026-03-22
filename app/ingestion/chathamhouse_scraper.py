import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
import requests
from app.ingestion.base_scraper import BaseScraper

class ChathamHouseScraper(BaseScraper):
    """
    Scraper for Chatham House publications via RSS feed.

    Chatham House publishes expert comments, research papers and analyses
    focused on European security, Russia, Ukraine and Black Sea regional dynamics.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="Chatham House",
            source_type="think_tank"
        )
        self.base_url = "https://www.chathamhouse.org"
        self.feed_url = f"{self.base_url}/path/whatsnew.xml"

    def fetch_documents(self) -> list[dict]:
        """
        Fetch publications from the Chatham House RSS feed.
        """

        try:
            response = requests.get(self.feed_url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch RSS feed: {self.feed_url}")
            print(f"Error: {e}")
            return []

        root = ET.fromstring(response.content)
        channel = root.find("channel")

        if not channel:
            print("No channel found in RSS feed")
            return []

        items = channel.findall("item")
        print(f"Total items in feed: {len(items)}")

        documents = []

        for item in items:
            title = item.findtext("title", "").strip()
            url = item.findtext("link", "").strip()

            if not title or not url:
                continue

            description_raw = item.findtext("description", "")
            publication_date = self.extract_date_from_description(description_raw)
            content = self.extract_text_from_description(description_raw)

            documents.append({
                "source_name": self.source_name,
                "source_type": self.source_type,
                "title": title,
                "url": url,
                "publication_date": publication_date,
                "content": content
            })

        return documents


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


if __name__ == "__main__":
    scraper = ChathamHouseScraper()
    documents = scraper.fetch_documents()
    print(f"\nSource: {scraper.source_name}")
    print(f"Type: {scraper.source_type}")
    print(f"Documents found: {len(documents)}")

    for i, doc in enumerate(documents[:3]):
        print(f"\n{'='*60}")
        print(f"Document {i + 1}")
        print(f"Title: {doc['title']}")
        print(f"URL: {doc['url']}")
        print(f"Publication Date: {doc['publication_date']}")
        print(f"Content preview: {doc['content'][:200]}")