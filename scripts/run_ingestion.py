from app.ingestion.mae_scraper import MaeScraper
import json
from pathlib import Path

from app.ingestion.nato_scraper import NatoScraper


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"

    # MAE
    mae_scraper = MaeScraper()
    mae_documents = mae_scraper.fetch_documents()

    mae_output_path = raw_data_dir / "mae_documents.json"

    with open(mae_output_path, "w", encoding="utf-8") as f:
        json.dump(mae_documents, f, ensure_ascii=False, indent=4)
        print(f"MAE documents saved to: {mae_output_path}")

    print(f"Source: {mae_scraper.source_name}")
    print(f"Type: {mae_scraper.source_type}")
    print(f"Documents found: {len(mae_documents)}")
    print(mae_documents[:10])

    # NATO
    nato_scraper = NatoScraper()
    nato_documents = nato_scraper.fetch_documents()

    nato_output_path = raw_data_dir / "nato_documents.json"

    with open(nato_output_path, "w", encoding="utf-8") as f:
        json.dump(nato_documents, f, ensure_ascii=False, indent=4)
        print(f"NATO documents saved to: {nato_output_path}")

    print(f"Source: {nato_scraper.source_name}")
    print(f"Type: {nato_scraper.source_type}")
    print(f"Documents found: {len(nato_documents)}")
    print(nato_documents[:10])

if __name__ == "__main__":
    main()