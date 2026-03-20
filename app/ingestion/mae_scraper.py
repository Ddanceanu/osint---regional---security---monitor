from app.ingestion.base_scraper import BaseScraper

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

    def extract_publication_date(self, article_url: str) -> str | None:
        """
        Extract the publication date from an individual MAE article page.
        Returns the date as text if found, otherwise None.
        """

        soup = self.get_soup(article_url)
        if not soup:
            return None

        date_fields = soup.find_all("div", class_="field field-type-text field-field-date")

        if date_fields:
            raw_text = date_fields[0].get_text(" ", strip=True)
            cleaned_text = raw_text.replace("Date:", "").strip()
            return cleaned_text

        return None

    def fetch_documents(self) -> list[dict]:
        documents = []
        seen_hrefs = set()

        for page_num in range(0, 3):
            if page_num == 0:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}?page={page_num}"

            soup = self.get_soup(page_url)
            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue

            links = soup.find_all("a")

            for link in links:
                href = link.get("href")
                text = link.get_text(strip=True)

                if href and "/en/node/" in href and len(text) >= 30:
                    if href not in seen_hrefs:
                        seen_hrefs.add(href)

                        article_url = f"https://www.mae.ro{href}"
                        publication_date = self.extract_publication_date(article_url)
                        content = self.extract_content(article_url)

                        documents.append({
                            "source_name": self.source_name,
                            "source_type": self.source_type,
                            "title": text,
                            "url": article_url,
                            "publication_date": publication_date,
                            "content": content,
                        })

        return documents

    def extract_content(self, article_url: str) -> str:
        """
        Extract the main textual content from a MAE article page.

        Returns a cleaned text string, or an empty string if extraction fails.
        """

        soup = self.get_soup(article_url)
        if not soup:
            return ""

        article_container = soup.select_one("div.art")
        if not article_container:
            return ""

        paragraphs = []

        for p in article_container.find_all("p", recursive=False):
            text = p.get_text(" ", strip=True)
            text = text.replace("\xa0", " ").strip()

            if not text:
                continue

            if text == "&nbsp;":
                continue

            paragraphs.append(text)
            # print(text[:120])

        return "\n\n".join(paragraphs).strip()