import streamlit as st

def get_document_explorer_column_config() -> dict:
    """
    Return the Streamlit column configuration for the Explorer component.
    """
    return {
        "Date": st.column_config.TextColumn(
            "Date",
            width="small",
        ),
        "Source": st.column_config.TextColumn(
            "Source",
            width="small",
        ),
        "Title": st.column_config.TextColumn(
            "Title",
            width="large",
            max_chars=120,
        ),
        "Main Theme": st.column_config.TextColumn(
            "Main Theme",
            width="medium",
        ),
        "Secondary Themes": st.column_config.TextColumn(
            "Secondary Themes",
            width="medium",
            max_chars=80,
        ),
        "Countries": st.column_config.TextColumn(
            "Countries",
            width="small",
            max_chars=60,
        ),
        "Organizations": st.column_config.TextColumn(
            "Organizations",
            width="medium",
            max_chars=80,
        ),
        "Content Preview": st.column_config.TextColumn(
            "Content Preview",
            width="large",
            max_chars=160,
        ),
    }