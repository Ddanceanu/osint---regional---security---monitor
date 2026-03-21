from app.ingestion.base_scraper import BaseScraper

class EeasScraper(BaseScraper):
    """
    Scraper for EEAS (European External Action Service) press materials.

    EEAS publishes press releases, statements, and council conclusions
    relevant to EU external action, especially regarding the eastern
    neighbourhood, Moldova, Ukraine and regional security.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="EEAS",
            source_type="official"
        )
        self.base_url = "https://www.eeas.europa.eu"
        self.listing_url = f"{self.base_url}/eeas/press-material_en"

    def fetch_documents(self) -> list[dict]:
        """
        Fetch press materials from multiple pages of the EEAS listing.
        """
        documents = []
        total_pages = 3

        for page_num in range(total_pages):
            page_url = f"{self.listing_url}?page={page_num}"
            soup = self.get_soup(page_url)

            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue

            cards = soup.find_all("div", class_="card")

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

                content = self.extract_content(full_url)

                documents.append({
                    "source_name": self.source_name,
                    "source_type": self.source_type,
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content
                })

        return documents

    def extract_content(self, article_url: str) -> str:
        """
        Extract the main text content from an individual EEAS artcle page.
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


if __name__ == "__main__":
    scraper = EeasScraper()
    documents = scraper.fetch_documents()
    print(f"\nSource: {scraper.source_name}")
    print(f"Documents found: {len(documents)}")

    for i, doc in enumerate(documents[:3]):
        print(f"\n{'='*60}")
        print(f"Document {i + 1}")
        print(f"Title: {doc['title']}")
        print(f"URL: {doc['url']}")
        print(f"Publication Date: {doc['publication_date']}")
        print(f"Content: {doc['content']}")