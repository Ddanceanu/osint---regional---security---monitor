import streamlit as st
from pathlib import Path
from app.dashboard.data_loader import load_table_dataframe

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_FILE_PATH = PROJECT_ROOT / "data" / "processed" / "combined_documents.json"

def main() -> None:
    """
    Run the OSINT Regional Security Monitor app.
    """

    st.set_page_config(
        page_title="OSINT Regional Security Monitor",
        page_icon="🌐",
        layout="wide",
    )

    st.title("OSINT Regional Security Monitor")
    st.caption("Document Explorer - initial dashboard validation view")

    dataframe = load_table_dataframe(DOCUMENTS_FILE_PATH)

    st.subheader("Dataset overview")
    st.write(f"Loaded documents: {len(dataframe)}")

    st.subheader("Table preview")
    st.dataframe(dataframe, use_container_width=True)

if __name__ == "__main__":
    main()