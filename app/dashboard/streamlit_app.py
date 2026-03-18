import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path

from app.dashboard.data import load_table_dataframe, get_metrics
from app.dashboard.ui import build_page_html, build_table_html

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "combined_documents.json"


def main() -> None:
    st.set_page_config(
        page_title="OSINT Regional Security Monitor",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    dataframe = load_table_dataframe(str(DOCUMENTS_FILE_PATH))

    timestamp = datetime.now().strftime("%Y-%m-%d · %H:%M UTC")
    metrics = get_metrics(dataframe)

    if "date" in dataframe.columns and not dataframe.empty:
        dates = dataframe["date"].dropna()
        date_range = f"{dates.min()}  →  {dates.max()}" if not dates.empty else "N/A"
    else:
        date_range = "N/A"

    components.html(
        build_page_html(metrics, date_range, timestamp),
        height=400,
        scrolling=False,
    )
    components.html(
        build_table_html(dataframe),
        height=720,
        scrolling=False,
    )


if __name__ == "__main__":
    main()