# Arhitecture

## MVP arhitecture overview

The project is designed as a small modular pipeline that transforms public documents into structured analytical records.

The workflow follows four main components:
1. Source collection;
2. Document processing;
3. Data storage;
4. Analytical interface.

## 1. Source collection

This component is responsible for accessing the selected public sources, identifying relevant documents, and collectiong the initial metadata needed for processing.

Typical outputs:

- source name;
- source type;
- title;
- URL;
- publication date.


## 2. Document processing

This component transforms raw collected material into structured content that can be analyzed more easily.

Main responsabilities:

- text extraction;
- cleaning and normalization;
- thematic classification;
- entity extraction;
- short summary generation.

## 3. Data storage 

This component stores both metadata and processed analytical fields in a structured form.

Stored elements include:
- source metadata;
- raw and cleaned text;
- theme labels;
- extracted entities;
- summary fields;
- analytical support fiels.

## 4. Analytical interface

This component presents the processed information in a usable form through filtering, comparison, and visual exploration.

Planned capabilities:
- filtering by source, date, and theme;
- browsing document records;
- basic trend visualization;
- actor frequency views;
- short analytical summaries.

## Design principles

The MVP arhitecture follow a few simple principles:

- modularity over complexity;
- traceble sources over high volume;
- analytical clarity over feature overload;
- incremental development over premature sophistication.

## Tehnical direction

The initial tehnical stack planned for the MVP includes:
- Python;
- FastAPI;
- PostgreSQL;
- SQLAlchemy;
- requests;
- BeautifulSoup;
- pandas;
- spaCY;
- Streamlit;
- Plotly.

