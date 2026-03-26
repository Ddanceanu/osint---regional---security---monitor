from datetime import datetime
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
        self.api_base_url = (
            "https://www.nato.int/content/nato/en/news-and-events/events/"
            "media-advisories/jcr:content/root/container/"
            "general_search.search.json"
        )
        self.api_params = {
            "query": "",
            "searchType": "wcm",
            "sortBy": "dateDesc",
            "pageSize": 50,
            "tags": "",
            "languages": "",
            "startDate": "",
            "endDate": "",
        }


    def _parse_date(self, date_str: str | None) -> datetime | None:
        """
        Parse NATO date string into datetime. Return None on failure.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), "%d %B %Y")
        except ValueError:
            return None


    def _fetch_article(self, article_url: str) -> dict:
        """
        Fetch a single article page and extract content and fallback date in one request.
        """
        soup = self.get_soup(article_url)
        if not soup:
            return {"content": "", "fallback_date": None}

        content = ""
        content_container = soup.select_one(
            "div.ca04-rich-text div.cmp-text__background-container"
        )
        if content_container:
            blocks = []
            for tag in content_container.find_all(["p", "li"]):
                text = tag.get_text(" ", strip=True).replace("\xa0", " ").strip()
                if text:
                    blocks.append(text)
            content = "\n\n".join(blocks).strip()

        fallback_date = None

        time_tag = soup.find("time")
        if time_tag:
            fallback_date = time_tag.get_text(" ", strip=True) or None

        if not fallback_date:
            for attrs in [
                {"property": "article:published_time"},
                {"name": "date"},
                {"name": "publish-date"},
                {"name": "publication_date"},
            ]:
                meta_tag = soup.find("meta", attrs=attrs)
                if meta_tag and meta_tag.get("content"):
                    fallback_date = meta_tag["content"].strip()
                    break

        if not fallback_date:
            page_text = soup.get_text("\n", strip=True)
            match = re.search(r"\b\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\b", page_text)
            if match:
                fallback_date = match.group(0)

        return {"content": content, "fallback_date": fallback_date}


    def fetch_documents(self) -> list[dict]:
        """Collect NATO media advisories published within the last LOOKBACK_DAYS."""
        documents = []
        page_num = 1

        while page_num <= self.MAX_PAGES:
            print(f"[NATO] Fetching API page {page_num}...")

            params = {**self.api_params, "page": page_num}

            try:
                response = requests.get(
                    self.api_base_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                print(f"[NATO] Request failed on page {page_num}: {e}")
                break
            except ValueError as e:
                print(f"[NATO] Invalid JSON on page {page_num}: {e}")
                break

            pages = data.get("pages", [])

            if not pages:
                print(f"[NATO] No results on page {page_num} — stopping.")
                break

            print(f"[NATO]   {len(pages)} item(s) received — fetching sequentially...")

            found_older_doc = False
            page_docs = []

            for item in pages:
                title = item.get("title", "").strip()
                publication_date = item.get("pageDate", "").strip()
                relative_link = item.get("link", "").strip()

                if not relative_link or not title:
                    continue

                full_url = urljoin(self.base_url, relative_link)
                result = self._fetch_article(full_url)

                # Use fallback date only if API did not provide pageDate
                if not publication_date and result["fallback_date"]:
                    publication_date = result["fallback_date"]

                parsed_date = self._parse_date(publication_date)

                if parsed_date is not None and parsed_date < self.cutoff_date:
                    found_older_doc = True
                    continue

                page_docs.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": result["content"],
                })

            documents.extend(page_docs)
            print(f"[NATO]   Kept {len(page_docs)} document(s) from page {page_num}.")

            if found_older_doc:
                print(f"[NATO] Reached cutoff date on page {page_num} — stopping.")
                break

            page_num += 1

        print(f"[NATO] Done. Total: {len(documents)} documents.")
        return documents
