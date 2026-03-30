# OSINT Regional Security Monitor

A personal OSINT analysis project focused on regional security developments relevant to Romania, the Republic of Moldova, Ukraine, Russia, and the NATO/EU eastern flank.

The project collects public documents from selected official institutions and think tanks, processes them into a structured corpus, and supports thematic, entity-based, and trend-oriented exploration through an interactive dashboard.

**Live dashboard:** [https://ddanceanu.github.io/osint---regional---security---monitor/](https://ddanceanu.github.io/osint---regional---security---monitor/)

---

## Purpose

This project was built as a practical system for working with public sources in a structured and explainable way.

Its goal is to show how open-source information can be collected, cleaned, organized, and turned into a usable analytical product. The focus is on source traceability, thematic consistency, and clear separation between institutional communication and analytical interpretation.

The scope was deliberately limited to regional security topics relevant to Romania, especially in relation to the Republic of Moldova, Ukraine, Russia, and the NATO/EU eastern flank.

---

## What the system supports

The platform is designed to support questions such as:

- What themes dominate the document flow in a given period?
- How does thematic emphasis change over time?
- Which actors appear most often, and in what contexts?
- How do official sources and think tanks differ in focus?
- Which recent documents are most relevant for further human review?

---

## Sources

The MVP uses a limited and controlled source set.

**Official sources**
- MAE Romania
- NATO
- Council of the European Union / European Council
- EEAS

**Think tanks**
- ECFR
- ISW
- Chatham House

A core design rule of the project is the separation between official sources and think tanks throughout the pipeline and the dashboard.

---

## Thematic taxonomy

Each document is assigned one main theme and may also receive secondary themes.

- Support for Ukraine
- Eastern Flank / NATO Deterrence
- Romania – Republic of Moldova
- Russia: Actions, Positioning, Regional Implications
- EU and Regional Security
- Black Sea and Regional Security
- Other / Mixed

---

## Processing pipeline

1. **Collection** - public documents are collected from selected sources.
2. **Normalization** - documents receive standardized metadata, normalized dates, and unique IDs.
3. **Cleaning** - article text is extracted and boilerplate elements are removed.
4. **Classification** - documents are assigned to predefined regional security themes.
5. **Entity extraction** - the system extracts relevant countries, organizations, persons, and locations.
6. **Quality checks** - missing fields, short content, and other processing issues are logged.
7. **Analytics** - the processed corpus is used for thematic, temporal, and source-level analysis.
8. **Dashboard presentation** - results are exposed through an interactive dashboard.

---

## Dashboard

The dashboard currently includes four main areas:

- **Overview** - corpus summary, trends, and source comparison
- **Document Explorer** - searchable and filterable document view
- **Themes** - thematic distribution and change over time
- **Entities** - entity visibility, context, and source coverage

---

## Current status

The repository currently contains a functional MVP with multi-source collection, processing and normalization, thematic classification, entity extraction, quality control, and a working dashboard for exploration and analysis.