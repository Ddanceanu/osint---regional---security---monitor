import streamlit as st
from pathlib import Path

from app.dashboard.data_loader import load_table_dataframe, build_display_dataframe
from app.dashboard.styles import inject_global_styles
from app.dashboard.table_config import get_document_explorer_column_config
from app.dashboard.metrics import (
    get_total_documents,
    get_total_sources,
    get_total_organizations,
    get_total_main_themes
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "combined_documents.json"

def render_kpi_row(dataframe) -> None:
    """
    Render the KPI cards row for the Document Explorer page.
    """
    total_documents = get_total_documents(dataframe)
    total_sources = get_total_sources(dataframe)
    total_organizations = get_total_organizations(dataframe)
    total_main_themes = get_total_main_themes(dataframe)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.metric("Total Documents", total_documents)

    with col2:
        st.metric("Sources", total_sources)

    with col3:
        st.metric("Main Themes", total_main_themes)

    with col4:
        st.metric("Organizations", total_organizations)


def main() -> None:
    """
    Run the OSINT Regional Security Monitor app.
    """
    st.set_page_config(
        page_title="OSINT Regional Security Monitor",
        page_icon="🌐",
        layout="wide",
    )

    inject_global_styles()

    st.title("OSINT Regional Security Monitor")
    st.caption("Document Explorer - initial dashboard validation view")

    dataframe = load_table_dataframe(str(DOCUMENTS_FILE_PATH))
    display_dataframe = build_display_dataframe(dataframe)

    st.subheader("Dataset overview")
    st.write(f"Loaded documents: {len(dataframe)}")

    render_kpi_row(dataframe)

    st.subheader("Document Explorer")
    st.dataframe(
        display_dataframe,
        use_container_width=True,
        hide_index=True,
        column_config=get_document_explorer_column_config(),
    )


if __name__ == "__main__":
    main()