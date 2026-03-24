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
from app.processing.trending import compute_trending
from app.processing.theme_shift import compute_theme_shift
from app.processing.source_divergence import compute_source_divergence

def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"

    mae_input_path = raw_data_dir / "mae_documents.json"
    nato_input_path = raw_data_dir / "nato_documents.json"
    eu_council_input_path = raw_data_dir / "eu_council_documents.json"
    eeas_input_path = raw_data_dir / "eeas_documents.json"
    ecfr_input_path = raw_data_dir / "ecfr_documents.json"
    isw_input_path = raw_data_dir / "isw_documents.json"
    chathamhouse_output_path = raw_data_dir / "chathamhouse_documents.json"
    output_path = processed_data_dir / "combined_documents.json"
    quality_report_path = processed_data_dir / "quality_report.json"
    quality_warnings_path = processed_data_dir / "quality_warnings.json"
    docs_output_path = project_root / "docs" / "data" / "documents.json"
    trending_output_path = project_root / "docs" / "data" / "trending.json"

    with open(mae_input_path, "r", encoding="utf-8") as mae_file:
        mae_documents = json.load(mae_file)

    with open(nato_input_path, "r", encoding="utf-8") as nato_file:
        nato_documents = json.load(nato_file)

    with open(eu_council_input_path, "r", encoding="utf-8") as eu_council_file:
        eu_council_documents = json.load(eu_council_file)

    with open(eeas_input_path, "r", encoding="utf-8") as eeas_file:
        eeas_documents = json.load(eeas_file)

    with open(ecfr_input_path, "r", encoding="utf-8") as ecfr_file:
        ecfr_documents = json.load(ecfr_file)

    with open(isw_input_path, "r", encoding="utf-8") as isw_file:
        isw_documents = json.load(isw_file)

    with open(chathamhouse_output_path, "r", encoding="utf-8") as chathamhouse_output_file:
        chathamhouse_documents = json.load(chathamhouse_output_file)

    all_documents = (mae_documents + nato_documents + eu_council_documents + eeas_documents + ecfr_documents
                     + isw_documents + chathamhouse_documents)
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

    trending_data = compute_trending(document_with_entities)

    with open(trending_output_path, "w", encoding="utf-8") as trending_file:
        json.dump(trending_data, trending_file, ensure_ascii=False, indent=4)

    print(f"Trending data saved to: {trending_output_path}")
    print(f"  Period: {trending_data['period_start']} -> {trending_data['period_end']}")
    print(f"  Documents in period: {trending_data['total_documents_in_period']}")

    theme_shift_data = compute_theme_shift(document_with_entities)

    theme_shift_output_path = project_root / "docs" / "data" / "theme_shift.json"
    with open(theme_shift_output_path, "w", encoding="utf-8") as theme_shift_file:
        json.dump(theme_shift_data, theme_shift_file, ensure_ascii=False, indent=4)

    print(f"Theme shift data saved to: {theme_shift_output_path}")
    print(f"  Weeks covered: {len(theme_shift_data['weeks'])}")
    print(f"  Themes tracked: {len(theme_shift_data['themes'])}")

    divergence_data = compute_source_divergence(document_with_entities)

    divergence_output_path = project_root / "docs" / "data" / "source_divergence.json"
    with open(divergence_output_path, "w", encoding="utf-8") as divergence_file:
        json.dump(divergence_data, divergence_file, ensure_ascii=False, indent=4)

    print(f"Source divergence data saved to: {divergence_output_path}")
    print(f"  Official: {divergence_data['official']['total_documents']} docs from {len(divergence_data['official']['sources'])} sources")
    print(f"  Think tank: {divergence_data['think_tank']['total_documents']} docs from {len(divergence_data['think_tank']['sources'])} sources")
    print(f"  Theme gaps computed: {len(divergence_data['divergence']['theme_gaps'])}")


if __name__ == "__main__":
    main()