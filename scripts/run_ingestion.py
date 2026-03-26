import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.ingestion.mae_scraper import MaeScraper
from app.ingestion.nato_scraper import NatoScraper
from app.ingestion.eu_council_scraper import EuCouncilScraper
from app.ingestion.eeas_scraper import EeasScraper
from app.ingestion.ecfr_scraper import EcfrScraper
from app.ingestion.isw_scraper import IswScraper
from app.ingestion.chathamhouse_scraper import ChathamHouseScraper


def run_scraper(scraper, output_path: Path) -> dict:
    """
    Run a single scraper, save results to JSON, and return a summary.
    Each scraper runs sequentially on its own site,
    but all 7 scrapers run in parallel (one thread per source).
    """
    documents = scraper.fetch_documents()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=4)

    return {
        "source_name": scraper.source_name,
        "source_type": scraper.source_type,
        "count": len(documents),
        "output_path": str(output_path),
    }


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"

    # Define all scrapers and their output files
    jobs = [
        (MaeScraper(), raw_data_dir / "mae_documents.json"),
        (NatoScraper(), raw_data_dir / "nato_documents.json"),
        (EuCouncilScraper(), raw_data_dir / "eu_council_documents.json"),
        (EeasScraper(), raw_data_dir / "eeas_documents.json"),
        (EcfrScraper(), raw_data_dir / "ecfr_documents.json"),
        (IswScraper(), raw_data_dir / "isw_documents.json"),
        (ChathamHouseScraper(), raw_data_dir / "chathamhouse_documents.json"),
    ]

    print(f"Starting ingestion for {len(jobs)} sources in parallel...\n")

    results = []

    with ThreadPoolExecutor(max_workers=7) as executor:
        future_map = {}
        for scraper, output_path in jobs:
            future = executor.submit(run_scraper, scraper, output_path)
            future_map[future] = scraper.source_name

        for future in as_completed(future_map):
            source_name = future_map[future]
            try:
                result = future.result()
                results.append(result)
                print(f"\n[DONE] {result['source_name']} ({result['source_type']}): {result['count']} documents → {result['output_path']}")
            except Exception as e:
                print(f"\n[ERROR] {source_name} failed: {e}")

    print(f"\n{'='*60}")
    print(f"Ingestion complete. Summary:")
    print(f"{'='*60}")
    total = 0
    for r in sorted(results, key=lambda x: x["source_name"]):
        print(f"  {r['source_name']:20s} ({r['source_type']:10s}): {r['count']:>4d} documents")
        total += r["count"]
    print(f"{'='*60}")
    print(f"  {'TOTAL':20s}              : {total:>4d} documents")


if __name__ == "__main__":
    main()
