from collections import Counter
from datetime import datetime

def get_document_issues(document: dict) -> list[str]:
    """
    Return a list of quality issues detected for a single document.
    """

    issues = []

    title = (document.get("title") or "").strip()
    url = (document.get("url") or "").strip()
    publication_date = (document.get("publication_date") or "").strip()
    publication_date_iso = (document.get("publication_date_iso") or "").strip()
    content = (document.get("content") or "").strip()
    document_id = (document.get("document_id") or "").strip()

    if not title:
        issues.append("empty_title")

    if not url:
        issues.append("empty_url")

    if not publication_date:
        issues.append("empty_publication_date")

    if not publication_date_iso:
        issues.append("empty_publication_date_iso")

    if not content:
        issues.append("empty_content")
    elif len(content) < 200:
        issues.append("short_content")

    if not document_id:
        issues.append("empty_document_id")

    return issues


def collect_quality_warnings(documents: list[dict]) -> list[dict]:
    """
    Return all problematic documents together with their detected issues.
    """

    warnings = []

    for document in documents:
        issues = get_document_issues(document)

        if not issues:
            continue

        warnings.append({
            "document_id": document.get("document_id", ""),
            "source_key": document.get("source_key", ""),
            "title": document.get("title", ""),
            "url": document.get("url", ""),
            "issues": issues,
        })

    return warnings


def build_quality_report(
        raw_documents: list[dict],
        normalized_documents: list[dict],
        deduplicated_documents: list[dict],
) -> dict:
    """
    Build an aggregate quality report for the current processing run.
    """

    issue_counter = Counter()
    source_counter = Counter()

    for document in deduplicated_documents:
        source_key = (document.get("source_key") or "unknown").strip() or "unknown"
        source_counter[source_key] += 1
        issue_counter.update(get_document_issues(document))

    report = {
        "run_timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "raw_documents_total": len(raw_documents),
        "normalized_documents_total": len(normalized_documents),
        "deduplicated_documents_total": len(deduplicated_documents),
        "duplicates_removed": len(normalized_documents) - len(deduplicated_documents),
        "documents_per_source": dict(source_counter),
        "empty_title_count": issue_counter["empty_title"],
        "empty_url_count": issue_counter["empty_url"],
        "empty_publication_date_count": issue_counter["empty_publication_date"],
        "empty_publication_date_iso_count": issue_counter["empty_publication_date_iso"],
        "empty_content_count": issue_counter["empty_content"],
        "short_content_count": issue_counter["short_content"],
        "empty_document_id_count": issue_counter["empty_document_id"],
    }

    return report
