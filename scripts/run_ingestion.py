from app.ingestion.mae_scraper import MaeScraper

def main() -> None:
    scraper = MaeScraper()
    documents = scraper.fetch_documents()

    print(f"Source: {scraper.source_name}")
    print(f"Type: {scraper.source_type}")
    print(f"Documents found: {len(documents)}")
    print(documents)

if __name__ == "__main__":
    main()