from app.ingestion.base_scraper import BaseScraper


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

    def fetch_documents(self) -> list[dict]:
        """
        Fetch Russia-Ukraine reports from multiple pages of the ISW listing.
        """
        documents = []
        total_pages = 5

        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                page_url = self.listing_url
            else:
                page_url = f"{self.listing_url}?_paged={page_num}"

            soup = self.get_soup(page_url)

            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue

            cards = soup.find_all("div", class_="research-card-loop-item-3colgrid")
            print(f"Page {page_num}: {len(cards)} cards found")

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


if __name__ == "__main__":
    scraper = IswScraper()
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