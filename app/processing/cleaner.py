import re


BOILERPLATE_LINE_PATTERNS = [
    # Social media
    r"follow\s+us\b",
    r"share\s+(this|on)\b",
    r"tweet\s+this\b",
    r"find\s+us\s+on\b",
    r"\b(facebook|twitter|instagram|linkedin|youtube|tiktok)\b.*\b(follow|like|share|subscribe)\b",
    r"\b(follow|like|share|subscribe)\b.*\b(facebook|twitter|instagram|linkedin|youtube|tiktok)\b",
    # Newsletter / subscription
    r"subscribe\s+to\b",
    r"sign\s+up\s+(for|to)\b",
    r"newsletter",
    r"stay\s+(informed|updated|connected)\b",
    r"get\s+(the\s+)?latest\b",
    r"join\s+our\s+mailing\s+list\b",
    # Press / contact
    r"press\s+contact",
    r"media\s+contact",
    r"for\s+(more\s+)?information\s*,?\s*contact\b",
    r"press\s+office\b",
    r"spokesperson\b",
    # Navigation / menus
    r"skip\s+to\s+(main\s+)?content\b",
    r"back\s+to\s+top\b",
    r"read\s+more\b$",
    r"^\s*menu\s*$",
    r"^\s*search\s*$",
    r"^\s*home\s*$",
    # Cookie / privacy banners
    r"(accept|manage)\s+(all\s+)?cookies\b",
    r"cookie\s+(policy|settings|preferences)\b",
    r"privacy\s+(policy|notice|statement)\b",
    # Copyright / legal
    r"all\s+rights\s+reserved\b",
    r"terms\s+(of\s+use|and\s+conditions)\b",
    r"©\s*\d{4}",
    # Download / print
    r"^\s*(download|print)\s+(pdf|this|page)\b",
]

BOILERPLATE_LINE_REGEXES = [re.compile(p, re.IGNORECASE) for p in BOILERPLATE_LINE_PATTERNS]

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    if not text:
        return text

    # Remove standalone URLs
    text = URL_PATTERN.sub("", text)

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Skip very short lines (likely navigation fragments)
        if len(stripped) < 5:
            continue

        # Skip lines matching boilerplate patterns
        is_boilerplate = False
        for regex in BOILERPLATE_LINE_REGEXES:
            if regex.search(stripped):
                is_boilerplate = True
                break

        if not is_boilerplate:
            cleaned_lines.append(stripped)

    cleaned = " ".join(cleaned_lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def clean_document(document: dict) -> dict:
    cleaned_document = document.copy()

    content = document.get("content", "")
    cleaned_document["content_clean"] = clean_text(content)

    return cleaned_document
