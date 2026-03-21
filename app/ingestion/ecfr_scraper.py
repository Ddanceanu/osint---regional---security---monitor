from app.ingestion.base_scraper import BaseScraper

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

    def fetch_documents(self) -> list[dict]:
        """
        Fetch publications from multiple pages of the ECFR listing.
        """
        documents = []
        total_pages = 3

        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                page_url = self.listing_url
            else:
                page_url = f"{self.listing_url}page/{page_num}"

            soup = self.get_soup(page_url)

            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue

            cards = soup.find_all("article")

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
                    publication = time_tag.get("datetime", "").strip()
                    if not publication_date:
                        publication_date = time_tag.get_text(strip=True)

                content = self.extract_content(full_url)

                documents.append({
                    "source_name": "ECFR",
                    "source_type": "think_tank",
                    "title": title,
                    "url": full_url,
                    "publication_date": publication_date,
                    "content": content
                })

        return documents


    def extract_content(self, article_url: str) -> str:
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

if __name__ == "__main__":
    scraper = EcfrScraper()
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