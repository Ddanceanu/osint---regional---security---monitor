from app.ingestion.base_scraper import BaseScraper
import requests
from urllib.parse import urljoin
import re

class NatoScraper(BaseScraper):
    """
    Scraper for NATO official media advisories.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="NATO",
            source_type="official"
        )

        self.base_url = "https://www.nato.int"
        self.api_url = (
            "https://www.nato.int/content/nato/en/news-and-events/events/"
            "media-advisories/jcr:content/root/container/"
            "general_search.search.json?query=&searchType=wcm&sortBy=dateDesc"
            "&pageSize=25&page=1&tags=&languages=&startDate=&endDate="
        )

    def extract_publication_date(self, article_url: str) -> str | None:
        """
        Extract the publication date from an individual NATO article page.
        Returns the date as text if found, otherwise returns None.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return None

        # 1. Try <time> tags
        time_tag = soup.find("time")
        if time_tag:
            date_text = time_tag.get_text(" ", strip=True)
            if date_text:
                return date_text

        # 2. Try common meta tags
        meta_candidates = [
            {"property": "article:published_time"},
            {"name": "date"},
            {"name": "publish-date"},
            {"name": "publication_date"},
        ]

        for attrs in meta_candidates:
            meta_tag = soup.find("meta", attrs=attrs)
            if meta_tag and meta_tag.get("content"):
                return meta_tag["content"].strip()

        # 3. Fallback: look for a text date pattern in page text
        page_text = soup.get_text("\n", strip=True)
        match = re.search(r"\b\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\b", page_text)
        if match:
            return match.group(0)

        return None

    def fetch_documents(self) -> list[dict]:
        """
        Fetch NATO media advisories from the JSON search endpoint
        and convert them to the standard document format.
        """
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            pages = data.get("pages", [])

            documents = []

            for page in pages:
                title = page.get("title", "").strip()
                relative_link = page.get("link", "").strip()

                if not title or not  relative_link:
                    continue

                publication_date = page.get("pageDate", "").strip()
                full_url = urljoin(self.base_url, relative_link)
                content = self.extract_content(full_url)

                if not publication_date:
                    publication_date = self.extract_publication_date(full_url) or ""

                documents.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content
                }
                )
            return documents
        except requests.RequestException as e:
            print(f"Failed to fetch source: {self.api_url}")
            print(f"Error: {e}")
            return []
        except ValueError as e:
            print("Response is not valid JSON")
            print(f"Error: {e}")
            return []


    def extract_content(self, article_url: str) -> str:
        """
        Extract the main content from an individual NATO article page.
        Returns a cleaned text string, or an empty string if extraction fails.
        """

        soup = self.get_soup(article_url)
        if not soup:
            return ""

        content_container = soup.select_one(
            "div.ca04-rich-text div.cmp-text__background-container"
        )
        if not content_container:
            return ""

        blocks = []

        for tag in content_container.find_all(["p", "li"]):
            text = tag.get_text(" ", strip=True)
            text = text.replace("\xa0", " ").strip()  # \xa0 -> caracter unicode non-breaking space

            if not text:
                continue

            blocks.append(text)

        return "\n\n".join(blocks).strip()
