from app.ingestion.mae_scraper import MaeScraper
import json
from pathlib import Path

from app.ingestion.nato_scraper import NatoScraper
from app.ingestion.eu_council_scraper import EuCouncilScraper
from app.ingestion.eeas_scraper import EeasScraper
from app.ingestion.ecfr_scraper import EcfrScraper
from app.ingestion.isw_scraper import IswScraper
from app.ingestion.chathamhouse_scraper import ChathamHouseScraper


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

    # EU Council Scraper
    eu_council_scraper = EuCouncilScraper()
    eu_council_documents = eu_council_scraper.fetch_documents()

    eu_council_output_path = raw_data_dir / "eu_council_documents.json"

    with open(eu_council_output_path, "w", encoding="utf-8") as f:
        json.dump(eu_council_documents, f, ensure_ascii=False, indent=4)
        print(f"EU Council documents saved to: {eu_council_output_path}")

    print(f"Source: {eu_council_scraper.source_name}")
    print(f"Type: {eu_council_scraper.source_type}")
    print(f"Documents found: {len(eu_council_documents)}")
    print(eu_council_documents[:10])


    # EEAS Scraper
    eeas_scraper = EeasScraper()
    eeas_documents = eeas_scraper.fetch_documents()

    eeas_output_path = raw_data_dir / "eeas_documents.json"

    with open(eeas_output_path, "w", encoding="utf-8") as f:
        json.dump(eeas_documents, f, ensure_ascii=False, indent=4)
        print(f"EEAS documents saved to: {eeas_output_path}")

    print(f"Source: {eeas_scraper.source_name}")
    print(f"Type: {eeas_scraper.source_type}")
    print(f"Documents found: {len(eeas_documents)}")
    print(eeas_documents[:10])


    # ECFR Scraper
    ecfr_scraper = EcfrScraper()
    ecfr_documents = ecfr_scraper.fetch_documents()

    ecfr_output_path = raw_data_dir / "ecfr_documents.json"

    with open(ecfr_output_path, "w", encoding="utf-8") as f:
        json.dump(ecfr_documents, f, ensure_ascii=False, indent=4)
        print(f"ECFR documents saved to: {ecfr_output_path}")

    print(f"Source: {ecfr_scraper.source_name}")
    print(f"Type: {ecfr_scraper.source_type}")
    print(f"Documents found: {len(ecfr_documents)}")


    # ISW Scraper
    isw_scraper = IswScraper()
    isw_documents = isw_scraper.fetch_documents()

    isw_output_path = raw_data_dir / "isw_documents.json"

    with open(isw_output_path, "w", encoding="utf-8") as f:
        json.dump(isw_documents, f, ensure_ascii=False, indent=4)
        print(f"ISW documents saved to: {isw_output_path}")

    print(f"Source: {isw_scraper.source_name}")
    print(f"Type: {isw_scraper.source_type}")
    print(f"Documents found: {len(isw_documents)}")


    # Chatham House
    chathamhouse_scraper = ChathamHouseScraper()
    chathamhouse_documents = chathamhouse_scraper.fetch_documents()

    chathamhouse_output_path = raw_data_dir / "chathamhouse_documents.json"

    with open(chathamhouse_output_path, "w", encoding="utf-8") as f:
        json.dump(chathamhouse_documents, f, ensure_ascii=False, indent=4)
        print(f"Chatham House documents saved to: {chathamhouse_output_path}")

    print(f"Source: {chathamhouse_scraper.source_name}")
    print(f"Type: {chathamhouse_scraper.source_type}")
    print(f"Documents found: {len(chathamhouse_documents)}")


if __name__ == "__main__":
    main()