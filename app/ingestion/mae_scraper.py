from app.ingestion.base_scraper import BaseScraper

class MaeScraper(BaseScraper):
    """
    Scraper for Ministry of Foreign Affairs of Romania (MAE).

    The first version only defines the scraper structure.
    Real extraction logic will be added later.
    """

    def __init__(self) -> None:
        super().__init__(
            source_name="MAE Romania",
            source_type="official"
        )

    def fetch_documents(self) -> list[dict]:
        """
        Return document candidates collected from the MAE source.

        For now, this method returns an empty list because
        the scraping logic is not implemented yet.
        """
        return []