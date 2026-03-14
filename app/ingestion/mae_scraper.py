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
        """
        Fetch article candidates from the MAE press releases page
        and return standardized document records.
        """

        soup = self.get_soup(self.base_url)
        if not soup:
            return []

        links = soup.find_all("a")

        article_candidates = []
        seen_hrefs = set()

        for link in links:
            href = link.get("href")
            text = link.get_text(strip=True)

            if href and "/en/node/" in href and len(text) >= 30:
                if href not in seen_hrefs:
                    article_candidates.append((text, href))
                    seen_hrefs.add(href)

        documents = []
        for title, href in article_candidates:
            article_url = f"https://www.mae.ro{href}"
            publication_date = self.extract_publication_date(article_url)

            document = {
                "source_name": self.source_name,
                "source_type": self.source_type,
                "title": title,
                "url": article_url,
                "publication_date": publication_date,
            }
            documents.append(document)

        return documents