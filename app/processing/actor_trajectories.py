from datetime import date, timedelta


# ── Constants ──────────────────────────────────────────────────────────────────

WINDOW_DAYS = 90       # total lookback window
WEEK_SIZE   = 7        # days per bucket
MIN_RAW_MENTIONS = 5   # entity must have at least this many raw mentions across
                       # the whole window to be included in the actor list

DEFAULT_ACTORS = [
    "Ukraine",
    "Russia",
    "European Union",
    "NATO",
    "Volodymyr Zelenskyy",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _group_by_source(docs):
    """Return {source_key: [docs]} dict."""
    groups = {}
    for doc in docs:
        key = doc.get("source_key")
        if key:
            groups.setdefault(key, []).append(doc)
    return groups


def _source_normalized_rate(docs_in_window, entity, category, all_source_keys):
    """
    Source-normalized visibility rate for a single entity over a set of docs.

    For each source: rate = docs_mentioning_entity / total_docs_from_source
    Final score:     mean(rate per source) — sources with 0 docs contribute 0

    This is the same formula used across Strategic Pulse, Thematic Shift, etc.
    """
    source_groups = _group_by_source(docs_in_window)
    num_sources = len(all_source_keys)
    if num_sources == 0:
        return 0.0

    rates = []
    for source_key in all_source_keys:
        source_docs = source_groups.get(source_key, [])
        total = len(source_docs)
        if total == 0:
            rates.append(0.0)
            continue

        count = 0
        for doc in source_docs:
            if category == "themes":
                if doc.get("main_theme") == entity:
                    count += 1
                elif entity in doc.get("secondary_themes", []):
                    count += 1
            else:
                if entity in doc.get("entities", {}).get(category, []):
                    count += 1

        rates.append((count / total) * 100)

    return round(sum(rates) / num_sources, 2)


def _entity_raw_count(docs, entity, category):
    """Raw count of docs mentioning entity across the whole window."""
    count = 0
    for doc in docs:
        if category == "themes":
            if doc.get("main_theme") == entity or entity in doc.get("secondary_themes", []):
                count += 1
        else:
            if entity in doc.get("entities", {}).get(category, []):
                count += 1
    return count


# ── Weekly bucket builder ──────────────────────────────────────────────────────

def _build_weekly_buckets(documents, window_days=WINDOW_DAYS, week_size=WEEK_SIZE):
    """
    Split the last `window_days` days into weekly buckets.

    Returns:
        buckets  — list of (week_label, [docs_in_week]) tuples, oldest first
        all_sources — set of all source_keys seen across the entire window
    """
    today = date.today()
    window_start = today - timedelta(days=window_days - 1)

    # Index docs by date
    dated_docs = []
    for doc in documents:
        raw = doc.get("publication_date_iso")
        if not raw:
            continue
        try:
            pub = date.fromisoformat(raw)
        except (ValueError, TypeError):
            continue
        if pub >= window_start:
            dated_docs.append((pub, doc))

    # Collect all source keys seen in the window
    all_sources = set(doc.get("source_key") for _, doc in dated_docs if doc.get("source_key"))

    # Build week buckets: week 0 = oldest, week N-1 = most recent
    num_weeks = window_days // week_size
    buckets = []
    for w in range(num_weeks):
        week_start = window_start + timedelta(days=w * week_size)
        week_end   = week_start + timedelta(days=week_size - 1)
        week_docs  = [doc for pub, doc in dated_docs if week_start <= pub <= week_end]

        # Label: "3 Mar" — lstrip handles Windows zero-padding
        label = week_start.strftime("%d %b").lstrip("0").strip() or week_start.strftime("%d %b").strip()

        buckets.append((label, week_docs))

    return buckets, all_sources


# ── Actor catalogue builder ────────────────────────────────────────────────────

def _collect_actors(documents, all_sources):
    """
    Build a catalogue of all actors (entities + themes) that appear at least
    MIN_RAW_MENTIONS times in the window.

    Returns a dict keyed by actor name:
        {name: {"category": ..., "default": bool}}
    """
    actors = {}

    for category in ("persons", "countries", "organizations"):
        freq = {}
        for doc in documents:
            for entity in set(doc.get("entities", {}).get(category, [])):
                freq[entity] = freq.get(entity, 0) + 1
        for name, count in freq.items():
            if count >= MIN_RAW_MENTIONS:
                actors[name] = {
                    "category": category,
                    "default": name in DEFAULT_ACTORS,
                }

    # Themes
    theme_freq = {}
    for doc in documents:
        themes = set()
        if doc.get("main_theme"):
            themes.add(doc["main_theme"])
        themes.update(doc.get("secondary_themes", []))
        for t in themes:
            theme_freq[t] = theme_freq.get(t, 0) + 1
    for name, count in theme_freq.items():
        if count >= MIN_RAW_MENTIONS:
            actors[name] = {
                "category": "themes",
                "default": name in DEFAULT_ACTORS,
            }

    return actors


# ── Main entry point ───────────────────────────────────────────────────────────

def compute_actor_trajectories(documents, window_days=WINDOW_DAYS, week_size=WEEK_SIZE):
    """
    Compute weekly source-normalized visibility trajectories for all actors.

    For each actor and each week:
        rate = mean over all sources of (docs_mentioning_actor / total_source_docs)

    This is the same normalization used in Strategic Pulse and Thematic Shift,
    ensuring no single high-volume source dominates the trajectory.

    Returns a JSON-ready dict consumed by the Actor Trajectories frontend panel.
    """
    today = date.today()
    window_start = today - timedelta(days=window_days - 1)

    # Filter to window
    window_docs = []
    for doc in documents:
        raw = doc.get("publication_date_iso")
        if not raw:
            continue
        try:
            pub = date.fromisoformat(raw)
        except (ValueError, TypeError):
            continue
        if pub >= window_start:
            window_docs.append(doc)

    buckets, all_sources = _build_weekly_buckets(window_docs, window_days, week_size)
    actors = _collect_actors(window_docs, all_sources)

    # Build trajectories: {actor_name: [rate_week0, rate_week1, ...]}
    trajectories = {}
    for name, meta in actors.items():
        category = meta["category"]
        series = []
        for _label, week_docs in buckets:
            rate = _source_normalized_rate(week_docs, name, category, all_sources)
            series.append(rate)
        trajectories[name] = series

    week_labels = [label for label, _ in buckets]

    return {
        "period_start": str(window_start),
        "period_end": str(today),
        "window_days": window_days,
        "week_size": week_size,
        "num_weeks": len(buckets),
        "week_labels": week_labels,
        "default_actors": DEFAULT_ACTORS,
        "actors": {
            name: {
                "category": meta["category"],
                "default": meta["default"],
                "trajectory": trajectories[name],
            }
            for name, meta in actors.items()
        },
    }
