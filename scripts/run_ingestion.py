from app.ingestion.mae_scraper import MaeScraper
import json
from pathlib import Path

def main() -> None:
    scraper = MaeScraper()
    documents = scraper.fetch_documents()

    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "data" / "raw" / "mae_documents.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=4)
        print(f"Documents saved to: {output_path}")

    print(f"Source: {scraper.source_name}")
    print(f"Type: {scraper.source_type}")
    print(f"Documents found: {len(documents)}")
    print(documents[:10])

if __name__ == "__main__":
    main()