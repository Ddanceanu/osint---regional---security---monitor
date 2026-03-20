import json
from pathlib import Path

from app.processing.normalizer import (
    normalize_documents,
    sort_documents_by_date,
    deduplicate_documents,
)

from app.processing.quality_checks import collect_quality_warnings, build_quality_report
from app.processing.theme_classifier import classify_document
from app.processing.entity_extractor import enrich_document_with_entities

def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"

    mae_input_path = raw_data_dir / "mae_documents.json"
    nato_input_path = raw_data_dir / "nato_documents.json"
    eu_council_input_path = raw_data_dir / "eu_council_documents.json"
    output_path = processed_data_dir / "combined_documents.json"
    quality_report_path = processed_data_dir / "quality_report.json"
    quality_warnings_path = processed_data_dir / "quality_warnings.json"
    docs_output_path = project_root / "docs" / "data" / "documents.json"

    with open(mae_input_path, "r", encoding="utf-8") as mae_file:
        mae_documents = json.load(mae_file)

    with open(nato_input_path, "r", encoding="utf-8") as nato_file:
        nato_documents = json.load(nato_file)

    with open(eu_council_input_path, "r", encoding="utf-8") as eu_council_file:
        eu_council_documents = json.load(eu_council_file)

    all_documents = mae_documents + nato_documents + eu_council_documents
    normalized_documents = normalize_documents(all_documents)
    deduplicated_documents = deduplicate_documents(normalized_documents)
    sorted_documents = sort_documents_by_date(deduplicated_documents)

    classified_documents = [classify_document(document) for document in sorted_documents]

    document_with_entities = [
        enrich_document_with_entities(document)
        for document in classified_documents
    ]

    quality_warnings = collect_quality_warnings(document_with_entities)
    quality_report = build_quality_report(
        all_documents,
        normalized_documents,
        document_with_entities,
    )

    processed_data_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(document_with_entities, output_file, ensure_ascii=False, indent=4)

    with open(quality_warnings_path, "w", encoding="utf-8") as quality_warnings_file:
        json.dump(quality_warnings, quality_warnings_file, ensure_ascii=False, indent=4)

    with open(quality_report_path, "w", encoding="utf-8") as report_file:
        json.dump(quality_report, report_file, ensure_ascii=False, indent=4)

    print(f"Processed documents saved to: {output_path}")
    print(f"Total raw documents loaded: {len(all_documents)}")
    print(f"Total final documents saved: {len(document_with_entities)}")
    print(document_with_entities[:5])

    # salvare in documentul final de unde se incarca tabelul html
    with open(docs_output_path, "w", encoding="utf-8") as output_file:
        json.dump(document_with_entities, output_file, ensure_ascii=False, indent=4)

    print("Dashboard data saved to: {docs_output_path}")

if __name__ == "__main__":
    main()