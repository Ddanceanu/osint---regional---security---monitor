import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path

from app.dashboard.data import load_table_dataframe, get_metrics, THEME_LABELS
from app.dashboard.ui import build_page_html, build_table_html
from app.dashboard.filters import apply_filters

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "combined_documents.json"


def render_sidebar(dataframe) -> dict:
    """
    Render the sidebar filters and return the active filter values.
    """
    with st.sidebar:
        st.markdown("### 🔍 Search")
        search = st.text_input(
            "Search in title and content",
            value="",
            placeholder="Type to search...",
            label_visibility="collapsed",
        )

        st.divider()

        st.markdown("### 📰 Source")
        available_sources = sorted(dataframe["source"].dropna().unique().tolist())
        selected_sources = st.multiselect(
            "Sources",
            options=available_sources,
            default=available_sources,
            label_visibility="collapsed",
        )

        st.divider()

        st.markdown("### 📅 Date Range")
        available_dates = dataframe["date"].dropna()
        date_min = available_dates.min() if not available_dates.empty else ""
        date_max = available_dates.max() if not available_dates.empty else ""

        date_start = st.text_input(
            "From (YYYY-MM-DD)",
            value=date_min,
            placeholder="YYYY-MM-DD",
        )
        date_end = st.text_input(
            "To (YYYY-MM-DD)",
            value=date_max,
            placeholder="YYYY-MM-DD",
        )

        st.divider()

        st.markdown("### 🏷️ Main Theme")
        available_theme_keys = dataframe["main_theme_key"].dropna().unique().tolist()
        theme_options = {
            THEME_LABELS.get(key, key): key
            for key in available_theme_keys
            if key
        }
        selected_theme_labels = st.multiselect(
            "Themes",
            options=list(theme_options.keys()),
            default=list(theme_options.keys()),
            label_visibility="collapsed",
        )
        selected_themes = [theme_options[label] for label in selected_theme_labels]

        st.divider()

        st.markdown("### 🌍 Entities")

        all_countries = sorted(set(
            country
            for countries in dataframe["countries"]
            if isinstance(countries, list)
            for country in countries
            if country
        ))
        selected_countries = st.multiselect(
            "Countries",
            options=all_countries,
            default=[],
            placeholder="All countries",
        )

        all_organizations = sorted(set(
            org
            for orgs in dataframe["organizations"]
            if isinstance(orgs, list)
            for org in orgs
            if org
        ))
        selected_organizations = st.multiselect(
            "Organizations",
            options=all_organizations,
            default=[],
            placeholder="All organizations",
        )

    return {
        "search": search,
        "sources": selected_sources,
        "date_start": date_start,
        "date_end": date_end,
        "themes": selected_themes,
        "countries": selected_countries if selected_countries else None,
        "organizations": selected_organizations if selected_organizations else None,
    }

def init_session_state():
    """
    Initialize session state defaults for filter persistence across reruns.
    """
    if "search" not in st.session_state:
        st.session_state["search"] = ""
    if "selected_doc_id" not in st.session_state:
        st.session_state["selected_doc_id"] = ""


def main() -> None:
    """
    Run the OSINT Regional Security Monitor dashboard.
    """
    st.set_page_config(
        page_title="OSINT Regional Security Monitor",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()

    selected_doc_id = st.query_params.get("doc", "")
    dataframe = load_table_dataframe(str(DOCUMENTS_FILE_PATH))
    filters = render_sidebar(dataframe)

    filtered_dataframe = apply_filters(
        dataframe,
        search=filters["search"],
        sources=filters["sources"],
        date_start=filters["date_start"],
        date_end=filters["date_end"],
        themes=filters["themes"],
        countries=filters["countries"],
        organizations=filters["organizations"],
    )

    timestamp = datetime.now().strftime("%Y-%m-%d · %H:%M UTC")
    metrics = get_metrics(filtered_dataframe)

    if "date" in filtered_dataframe.columns and not filtered_dataframe.empty:
        dates = filtered_dataframe["date"].dropna()
        date_range = f"{dates.min()}  →  {dates.max()}" if not dates.empty else "N/A"
    else:
        date_range = "N/A"

    components.html(
        build_page_html(metrics, date_range, timestamp),
        height=400,
        scrolling=False,
    )
    components.html(
        build_table_html(filtered_dataframe),
        height=720,
        scrolling=False,
    )


if __name__ == "__main__":
    main()