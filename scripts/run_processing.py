import json
from pathlib import Path

from app.processing.normalizer import normalize_documents, sort_documents_by_date

def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"

    mae_input_path = raw_data_dir / "mae_documents.json"
    nato_input_path = raw_data_dir / "nato_documents.json"
    output_path = processed_data_dir / "combined_documents.json"

    with open(mae_input_path, "r", encoding="utf-8") as mae_file:
        mae_documents = json.load(mae_file)

    with open(nato_input_path, "r", encoding="utf-8") as nato_file:
        nato_documents = json.load(nato_file)

    all_documents = mae_documents + nato_documents
    normalized_documents = normalize_documents(all_documents)
    sorted_documents = sort_documents_by_date(normalized_documents)

    processed_data_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(sorted_documents, output_file, ensure_ascii=False, indent=4)

    print(f"Processed documents saved to: {output_path}")
    print(f"Total raw documents loaded: {len(all_documents)}")
    print(f"Total normalized documents saved: {len(normalized_documents)}")
    print(sorted_documents[:5])

if __name__ == "__main__":
    main()