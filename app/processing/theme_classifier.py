import re

from app.processing.theme_config import THEME_KEYWORDS, THEME_ANCHOR_KEYWORDS

TITLE_MATCH_POINTS = 3
CONTENT_MATCH_POINTS = 1
TITLE_KEYWORD_CAP = 2
CONTENT_KEYWORD_CAP = 5
SECONDARY_THEME_MIN_SCORE = 3

def normalize_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def count_keyword_matches(text: str, keyword: str, cap: int) -> int:
    normalized_text = normalize_text(text)
    normalized_keyword = normalize_text(keyword)

    matches = re.findall(re.escape(normalized_keyword), normalized_text)
    count = len(matches)

    return min(count, cap)  # cap -> plafon pentru nr cuvinte


def has_anchor_keyword(title: str, content: str, theme_key: str) -> bool:
    if theme_key not in THEME_ANCHOR_KEYWORDS:
        return True

    combined_text = normalize_text(title + " " + content)

    for anchor in THEME_ANCHOR_KEYWORDS[theme_key]:
        normalized_anchor = normalize_text(anchor)
        pattern = r"\b" + re.escape(normalized_anchor) + r"\b"
        if re.search(pattern, combined_text):
            return True

    return False


def compute_theme_scores(title: str, content: str) -> dict[str, int]:
    theme_scores = {}

    for theme_key, keywords in THEME_KEYWORDS.items():
        theme_score = 0

        for keyword in keywords:
            title_matches = count_keyword_matches(title, keyword, TITLE_KEYWORD_CAP)
            content_matches = count_keyword_matches(content, keyword, CONTENT_KEYWORD_CAP)

            theme_score += title_matches * TITLE_MATCH_POINTS
            theme_score += content_matches * CONTENT_MATCH_POINTS

        theme_scores[theme_key] = theme_score

    return theme_scores


def classify_document(document: dict) -> dict:
    """
    Classify a document into themes based on title and content.
    Returns a copy of the document enriched with theme_scores,
    main_theme and secondary_theme.
    """

    classified_document = document.copy()

    title = document.get("title", "")
    content = document.get("content_clean", document.get("content", ""))

    theme_scores = compute_theme_scores(title, content)

    # Zero out themes that fail the anchor keyword check
    for theme_key in list(theme_scores.keys()):
        if theme_scores[theme_key] > 0 and not has_anchor_keyword(title, content, theme_key):
            theme_scores[theme_key] = 0

    if not theme_scores:
        main_theme = "other_mixed"
        secondary_themes = []
    else:
        max_score = max(theme_scores.values())

        if max_score == 0:
            main_theme = "other_mixed"
            secondary_themes = []
        else:
            main_theme = max(theme_scores, key=theme_scores.get)

            secondary_themes = [
                theme_key
                for theme_key, score in sorted(
                    theme_scores.items(),
                    key=lambda item: item[1],
                    reverse=True
                )
                if theme_key != main_theme and score >= SECONDARY_THEME_MIN_SCORE
            ]

    classified_document["theme_scores"] = theme_scores
    classified_document["main_theme"] = main_theme
    classified_document["secondary_themes"] = secondary_themes

    return classified_document