from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    Base class for all source scrapers used in the project.

    Each scraper must define:
    - source name
    - source_type
    - fetch_documents()

    The role of a scraper is to collect initial document metadata
    from a public source, without performing NLP or deeper analysis.
    """

    def __init__(self, source_name: str, source_type: str) -> None:
        self.source_name = source_name
        self.source_type = source_type

    @abstractmethod
    def fetch_documents(self) -> list[dict]:
        """
        Return a list of document candidates from the source.

        Each document should include at least:
        - source_name
        - source_type
        - title
        - URL
        - publication_date
        """
        pass