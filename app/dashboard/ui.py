import html as html_lib

# Design Tokens

COLORS = {
    "bg_primary":    "#060C16",
    "surface":       "#0D1828",
    "border":        "#182A42",
    "border_strong": "#223D60",
    "text_primary":  "#E4EDF8",
    "text_secondary":"#7A9DC0",
    "text_muted":    "#3E5570",
    "accent":        "#3B7BFF",
    "accent_hover":  "#5B95FF",
    "accent_soft":   "#0F2050",
    "accent_cyan":   "#00CFFF",
}


THEME_BADGES = {
    "support_ukraine":              {"label": "Support for Ukraine",      "bg": "#0C1E4A", "text": "#7EB8FF", "border": "#1A3C8A"},
    "eastern_flank_nato_deterrence":{"label": "Eastern Flank NATO",       "bg": "#1C0E50", "text": "#B8A8FF", "border": "#3D2290"},
    "romania_republic_of_moldova":  {"label": "Romania & Moldova",        "bg": "#3A1505", "text": "#FFB87A", "border": "#8A3A10"},
    "russia_regional_implications": {"label": "Russia Regional",          "bg": "#3A0808", "text": "#FF9494", "border": "#8A2020"},
    "eu_regional_security":         {"label": "EU Regional Security",     "bg": "#051E14", "text": "#5EDBA0", "border": "#0D5034"},
    "black_sea_regional_security":  {"label": "Black Sea Security",       "bg": "#051828", "text": "#60CCFF", "border": "#0A4070"},
    "other_mixed":                  {"label": "Other / Mixed",            "bg": "#111824", "text": "#7A9DC0", "border": "#223040"},
}


def _get_page_css() -> str:
    return """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    body{background:#060C16;font-family:'IBM Plex Sans','Segoe UI',sans-serif;color:#E4EDF8;padding:0 0 6px;}

    /* ── Header ── */
    .page-header{padding:1.5rem 0 1.25rem;border-bottom:1px solid #182A42;margin-bottom:1.5rem;position:relative;}
    .page-header::after{content:'';position:absolute;bottom:-1px;left:0;width:100px;height:1px;background:linear-gradient(90deg,#3B7BFF,transparent);}
    .header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;}
    .eyebrow{display:flex;align-items:center;gap:6px;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#3B7BFF;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;}
    .dot-live{width:5px;height:5px;border-radius:50%;background:#3B7BFF;box-shadow:0 0 7px #3B7BFF;animation:pulse 2.4s ease-in-out infinite;}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
    .page-title{font-family:'Exo 2','IBM Plex Sans',sans-serif;font-size:1.75rem;font-weight:700;letter-spacing:-.025em;background:linear-gradient(135deg,#E4EDF8 35%,#5B95FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:3px;}
    .page-subtitle{font-size:.76rem;color:#3E5570;letter-spacing:.04em;}
    .ts-badge{display:flex;align-items:center;gap:6px;background:rgba(59,123,255,.07);border:1px solid rgba(59,123,255,.18);border-radius:8px;padding:5px 11px;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#5B95FF;white-space:nowrap;}
    .ts-dot{width:6px;height:6px;border-radius:50%;background:#00CFFF;box-shadow:0 0 9px #00CFFF;}

    /* ── KPI Cards ── */
    .kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1.25rem;}
    .kpi-card{position:relative;background:#0D1828;border:1px solid #182A42;border-radius:12px;padding:1rem 1.125rem .875rem;overflow:hidden;}
    .kpi-glow{position:absolute;top:-30px;right:-30px;width:90px;height:90px;border-radius:50%;filter:blur(28px);pointer-events:none;opacity:.55;}
    .kpi-abbr{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.6rem;font-weight:600;letter-spacing:.12em;border:1px solid;border-radius:3px;padding:1px 5px;margin-bottom:10px;opacity:.85;}
    .kpi-value{font-family:'Exo 2','IBM Plex Sans',sans-serif;font-size:2.1rem;font-weight:700;letter-spacing:-.025em;line-height:1;margin-bottom:4px;}
    .kpi-label{font-size:.65rem;color:#3E5570;letter-spacing:.1em;text-transform:uppercase;}

    /* ── Dataset Strip ── */
    .dataset-strip{display:flex;align-items:center;gap:1.25rem;padding:.55rem 1rem;background:rgba(24,42,66,.4);border:1px solid #182A42;border-radius:8px;font-family:'IBM Plex Mono',monospace;font-size:.65rem;color:#3E5570;margin-bottom:1.25rem;}
    .ds-item{display:flex;align-items:center;gap:5px;}
    .ds-val{color:#5B95FF;font-weight:500;}
    .ds-sep{width:1px;height:10px;background:#182A42;}

    /* ── Section Header ── */
    .sec-hdr{display:flex;align-items:center;gap:9px;}
    .sec-bar{width:3px;height:18px;border-radius:2px;background:linear-gradient(180deg,#3B7BFF,#00CFFF);}
    .sec-title{font-family:'Exo 2','IBM Plex Sans',sans-serif;font-size:1rem;font-weight:600;color:#E4EDF8;letter-spacing:-.02em;}
    .sec-sub{font-size:.72rem;color:#3E5570;letter-spacing:.04em;margin-top:2px;margin-left:12px;}
    """


def _get_table_css() -> str:
    return """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    body{background:#060C16;font-family:'IBM Plex Sans','Segoe UI',sans-serif;}

    /* ── Wrapper & Scroll ── */
    .doc-table-wrapper{border:1px solid #182A42;border-radius:1rem;overflow:hidden;background:#0D1828;box-shadow:0 16px 48px rgba(0,0,0,.3);}
    .doc-table-scroll{overflow-x:auto;overflow-y:auto;max-height:650px;scrollbar-width:thin;scrollbar-color:#223D60 transparent;}
    .doc-table-scroll::-webkit-scrollbar{width:6px;height:6px;}
    .doc-table-scroll::-webkit-scrollbar-thumb{background:#223D60;border-radius:3px;}

    /* ── Table Layout ── */
    .doc-table{width:100%;border-collapse:collapse;table-layout:fixed;min-width:1100px;}
    .doc-header-row{position:sticky;top:0;z-index:10;}
    .doc-table thead th{background:#08111E;color:#3E5570;font-size:.6875rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;padding:.75rem .875rem;text-align:left;border-bottom:1px solid #223D60;white-space:nowrap;}

    /* ── Column Widths ── */
    .col-date{width:94px;} .col-source{width:80px;} .col-title{width:230px;}
    .col-theme{width:160px;} .col-secondary{width:160px;}
    .col-countries{width:115px;} .col-orgs{width:135px;} .col-preview{width:auto;}

    /* ── Rows ── */
    .doc-row{background:#0D1828;transition:background .12s ease;}
    .doc-row-alt{background:#0B1522;}
    .doc-row:hover{background:#132030 !important;}
    .doc-table tbody td{padding:.875rem;color:#C8D8EA;font-size:.8125rem;line-height:1.45;vertical-align:top;border-bottom:1px solid #162033;word-break:break-word;}

    /* ── Cell Elements ── */
    .cell-muted{color:#3E5570;font-style:italic;font-size:.7rem;}
    .cell-source{text-align:center;}
    .date-mono{font-family:'IBM Plex Mono',monospace;font-size:.6875rem;color:#3E5570;}
    .source-tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.6rem;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:#5B95FF;background:#0F2050;border:1px solid rgba(59,123,255,.2);border-radius:4px;padding:2px 6px;}
    .title-text{font-weight:500;color:#E4EDF8;font-size:.8125rem;line-height:1.4;display:block;}
    .theme-badge{display:inline-block;font-size:.7rem;font-weight:600;padding:.25rem .5rem;border-radius:4px;border:1px solid;line-height:1.4;word-break:break-word;}
    .sec-theme-tag{display:inline-block;font-size:.675rem;font-weight:500;padding:.175rem .4375rem;border-radius:4px;border:1px solid;line-height:1.35;}
    .pills-row{display:flex;flex-wrap:wrap;gap:.25rem;}
    .entity-pill{display:inline-block;font-size:.675rem;font-weight:500;color:#7A9DC0;background:#111F32;border:1px solid #182A42;border-radius:4px;padding:.175rem .4375rem;}
    .entity-more{font-family:'IBM Plex Mono',monospace;font-size:.65rem;color:#3E5570;padding:.175rem .25rem;}
    .preview-text{font-size:.75rem;color:#7A9DC0;line-height:1.6;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
    """


def _theme_badge_html(theme_key: str) -> str:
    cfg = THEME_BADGES.get(theme_key, THEME_BADGES["other_mixed"])
    label = html_lib.escape(cfg["label"])
    return (
        f'<span class="theme-badge" '
        f'style="background:{cfg["bg"]};color:{cfg["text"]};border-color:{cfg["border"]};">'
        f'{label}</span>'
    )


def _pills_html(values: list, hidden_count: int) -> str:
    if not values:
        return '<span class="cell-muted">—</span>'
    pills = "".join(
        f'<span class="entity-pill">{html_lib.escape(str(v))}</span>'
        for v in values if v
    )
    if hidden_count > 0:
        pills += f'<span class="entity-more">+{hidden_count}</span>'
    return f'<div class="pills-row">{pills}</div>'


def build_table_html(dataframe) -> str:
    if dataframe is None or dataframe.empty:
        return '<div class="doc-table-empty">No documents to display.</div>'

    headers = [
        ("col-date",      "Date"),
        ("col-source",    "Source"),
        ("col-title",     "Title"),
        ("col-theme",     "Main Theme"),
        ("col-secondary", "Secondary Themes"),
        ("col-countries", "Countries"),
        ("col-orgs",      "Organizations"),
        ("col-preview",   "Content Preview"),
    ]
    header_cells = "".join(
        f'<th class="{cls}">{label}</th>'
        for cls, label in headers
    )

    rows_html = ""
    for index, (_, row) in enumerate(dataframe.iterrows()):
        row_class = "doc-row" + (" doc-row-alt" if index % 2 == 1 else "")

        theme_key  = str(row.get("main_theme_key", ""))
        sec_themes = row.get("secondary_themes", [])
        sec_hidden = int(row.get("secondary_themes_hidden_count", 0) or 0)
        countries  = row.get("countries", [])
        c_hidden   = int(row.get("countries_hidden_count", 0) or 0)
        orgs       = row.get("organizations", [])
        o_hidden   = int(row.get("organizations_hidden_count", 0) or 0)

        rows_html += f"""
        <tr class="{row_class}">
            <td class="cell-date"><span class="date-mono">{html_lib.escape(str(row.get("date", "—")))}</span></td>
            <td class="cell-source"><span class="source-tag">{html_lib.escape(str(row.get("source", "—")))}</span></td>
            <td><span class="title-text">{html_lib.escape(str(row.get("title", "—")))}</span></td>
            <td>{_theme_badge_html(theme_key)}</td>
            <td>{_pills_html(sec_themes, sec_hidden)}</td>
            <td>{_pills_html(countries, c_hidden)}</td>
            <td>{_pills_html(orgs, o_hidden)}</td>
            <td><span class="preview-text">{html_lib.escape(str(row.get("content_preview", "—")))}</span></td>
        </tr>"""

    fonts = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{fonts}" rel="stylesheet">
<style>{_get_table_css()}</style>
</head><body>
    <div class="doc-table-wrapper">
        <div class="doc-table-scroll">
            <table class="doc-table">
                <thead><tr class="doc-header-row">{header_cells}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    </div>
</body></html>"""


def build_page_html(metrics: dict, date_range: str, timestamp: str) -> str:
    kpi_items = [
        ("DOC", metrics["documents"],    "#3B7BFF", "rgba(59,123,255,0.18)",  "Total Documents"),
        ("SRC", metrics["sources"],      "#00CFFF", "rgba(0,207,255,0.15)",   "Sources"),
        ("THM", metrics["themes"],       "#A78BFA", "rgba(167,139,250,0.15)", "Main Themes"),
        ("ORG", metrics["organizations"],"#34D399", "rgba(52,211,153,0.15)",  "Organizations"),
    ]
    kpi_html = ""
    for abbr, val, accent, glow, label in kpi_items:
        kpi_html += f"""
        <div class="kpi-card" style="border-top:2px solid {accent};">
            <div class="kpi-abbr" style="color:{accent};border-color:{accent};">{abbr}</div>
            <div class="kpi-value" style="color:{accent};">{val}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-glow" style="background:{glow};"></div>
        </div>"""

    fonts = "https://fonts.googleapis.com/css2?family=Exo+2:wght@700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{fonts}" rel="stylesheet">
<style>{_get_page_css()}</style>
</head><body>
  <div class="page-header">
    <div class="header-row">
      <div>
        <div class="eyebrow"><span class="dot-live"></span>OSINT · Regional Security Intelligence</div>
        <div class="page-title">Regional Security Monitor</div>
        <div class="page-subtitle">Document Explorer — analysis workspace</div>
      </div>
      <div class="ts-badge"><span class="ts-dot"></span>{timestamp}</div>
    </div>
  </div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="dataset-strip">
    <div class="ds-item"><span>Documents loaded</span><span class="ds-val">{metrics["documents"]}</span></div>
    <div class="ds-sep"></div>
    <div class="ds-item"><span>Date range</span><span class="ds-val">{date_range}</span></div>
    <div class="ds-sep"></div>
    <div class="ds-item"><span>Source</span><span class="ds-val">combined_documents.json</span></div>
  </div>
  <div class="sec-hdr">
    <div class="sec-bar"></div>
    <div>
      <div class="sec-title">Document Explorer</div>
      <div class="sec-sub">Browse and inspect the full document corpus</div>
    </div>
  </div>
</body></html>"""

