import json
from pathlib import Path
from app.dashboard.formatters import build_table_rows
import pandas as pd

def load_documents(file_path: str) -> list[dict]:
    """
    Load raw documents from a JSON file.

    The function expects the JSON file to contain a list of document objects.
    If the file does not exist or the content is not a list, an exception will be thrown.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Documents file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("Expected the JSON file to contain a list of documents")

    return documents


def load_table_rows(file_path: str) -> list[dict]:
    """
    Load raw documents from JSON and transform them into dashboard-ready table rows.
    """
    documents = load_documents(file_path)
    return build_table_rows(documents)


def load_table_dataframe(file_path: str) -> pd.DataFrame:
    """
    Load raw documents from JSON, transform them into table rows,
    and return them as a pandas DataFrame.
    """

    table_rows = load_table_rows(file_path)
    return pd.DataFrame(table_rows)


def format_list_cell(value) -> str:
    """
    Convert a list-like table cell into a readable display string.
    """
    if not value:
        return "—"

    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "—"

    return str(value)


def build_display_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Build the final display dataframe for the Document Explorer table.

    This function keeps only the UI-facing columns, formats list values for
    readable display, and renames the columns for presentation.
    """

    display_columns = [
        "date",
        "source",
        "title",
        "main_theme",
        "secondary_themes",
        "countries",
        "organizations",
        "content_preview",
    ]

    display_dataframe = dataframe[display_columns].copy()

    list_columns = [
        "secondary_themes",
        "countries",
        "organizations",
    ]

    for column in list_columns:
        display_dataframe[column] = display_dataframe[column].apply(format_list_cell)

    display_dataframe = display_dataframe.rename(
        columns={
            "date": "Date",
            "source": "Source",
            "title": "Title",
            "main_theme": "Main Theme",
            "secondary_themes": "Secondary Themes",
            "countries": "Countries",
            "organizations": "Organizations",
            "content_preview": "Content Preview",
        }
    )

    return display_dataframe