import streamlit as st

from app.dashboard.design_tokens import DESIGN_TOKENS

def get_token(section: str, key: str):
    """
    Return a design token value from the dashboard token dictionary.
    """
    return DESIGN_TOKENS[section][key]


def inject_global_styles() -> None:
    """
    Inject the global dashboard styles into the Streamlit app.

    This function applies the visual foundation of the dashboard:
    page background, typography, layout width, sidebar styling,
    input controls, buttons, and reusable surface styling.
    """
    colors = DESIGN_TOKENS["colors"]
    spacing = DESIGN_TOKENS["spacing"]
    radius = DESIGN_TOKENS["radius"]
    typography = DESIGN_TOKENS["typography"]
    layout = DESIGN_TOKENS["layout"]
    cards = DESIGN_TOKENS["cards"]

    css = f"""
    <style>
    :root {{
        --color-background-primary: {colors["background_primary"]};
        --color-background-secondary: {colors["background_secondary"]};
        --color-surface-primary: {colors["surface_primary"]};
        --color-surface-secondary: {colors["surface_secondary"]};
        --color-surface-hover: {colors["surface_hover"]};
        --color-surface-selected: {colors["surface_selected"]};

        --color-border-subtle: {colors["border_subtle"]};
        --color-border-strong: {colors["border_strong"]};

        --color-text-primary: {colors["text_primary"]};
        --color-text-secondary: {colors["text_secondary"]};
        --color-text-muted: {colors["text_muted"]};

        --color-accent-primary: {colors["accent_primary"]};
        --color-accent-hover: {colors["accent_hover"]};
        --color-accent-active: {colors["accent_active"]};
        --color-accent-soft: {colors["accent_soft"]};

        --space-2: {spacing["space_2"]};
        --space-3: {spacing["space_3"]};
        --space-4: {spacing["space_4"]};
        --space-6: {spacing["space_6"]};
        --space-8: {spacing["space_8"]};
        --space-10: {spacing["space_10"]};
        --space-12: {spacing["space_12"]};

        --radius-md: {radius["md"]};
        --radius-lg: {radius["lg"]};
        --radius-xl: {radius["xl"]};
        --radius-2xl: {radius["2xl"]};
        --radius-pill: {radius["pill"]};

        --font-family-base: {typography["font_family_base"]};
        --font-family-mono: {typography["font_family_mono"]};

        --font-size-sm: {typography["font_size_sm"]};
        --font-size-md: {typography["font_size_md"]};
        --font-size-lg: {typography["font_size_lg"]};
        --font-size-xl: {typography["font_size_xl"]};
        --font-size-2xl: {typography["font_size_2xl"]};
        --font-size-3xl: {typography["font_size_3xl"]};
        --font-size-4xl: {typography["font_size_4xl"]};

        --font-weight-regular: {typography["font_weight_regular"]};
        --font-weight-medium: {typography["font_weight_medium"]};
        --font-weight-semibold: {typography["font_weight_semibold"]};
        --font-weight-bold: {typography["font_weight_bold"]};

        --line-height-tight: {typography["line_height_tight"]};
        --line-height-normal: {typography["line_height_normal"]};
        --line-height-relaxed: {typography["line_height_relaxed"]};

        --page-max-width: {layout["page_max_width"]};
        --content-max-width: {layout["content_max_width"]};
        --sidebar-width: {layout["sidebar_width"]};

        --card-background: {cards["background"]};
        --card-border: {cards["border"]};
        --card-radius: {cards["border_radius"]};
        --card-padding: {cards["padding"]};
        --card-shadow: {cards["shadow"]};
    }}

    .stApp {{
        background: var(--color-background-primary);
        color: var(--color-text-primary);
        font-family: var(--font-family-base);
    }}

    .main .block-container {{
        max-width: var(--content-max-width);
        padding-top: {layout["container_padding_y"]};
        padding-bottom: {layout["container_padding_y"]};
        padding-left: {layout["container_padding_x"]};
        padding-right: {layout["container_padding_x"]};
    }}

    section[data-testid="stSidebar"] {{
        background: var(--color-background-secondary);
        border-right: 1px solid var(--color-border-subtle);
        width: var(--sidebar-width) !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-top: var(--space-8);
        padding-bottom: var(--space-8);
        padding-left: var(--space-4);
        padding-right: var(--space-4);
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--color-text-primary);
        letter-spacing: {typography["letter_spacing_tight"]};
        line-height: var(--line-height-tight);
    }}

    h1 {{
        font-size: var(--font-size-4xl);
        font-weight: var(--font-weight-bold);
        margin-bottom: var(--space-2);
    }}

    h2 {{
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-semibold);
        margin-top: var(--space-8);
        margin-bottom: var(--space-3);
    }}

    h3 {{
        font-size: var(--font-size-xl);
        font-weight: var(--font-weight-semibold);
        margin-top: var(--space-6);
        margin-bottom: var(--space-2);
    }}

    p, label, .stMarkdown, .stCaption {{
        color: var(--color-text-secondary);
        font-size: var(--font-size-md);
        line-height: var(--line-height-normal);
    }}

    [data-testid="stCaptionContainer"] {{
        color: var(--color-text-muted);
    }}

    hr {{
        border: none;
        border-top: 1px solid var(--color-border-subtle);
        margin-top: var(--space-6);
        margin-bottom: var(--space-6);
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {{
        background: var(--color-surface-primary);
        border: 1px solid var(--color-border-subtle);
        border-radius: var(--radius-lg);
        color: var(--color-text-primary);
    }}

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {{
        color: var(--color-text-primary);
    }}

    div[data-baseweb="tag"] {{
        background: var(--color-accent-soft);
        border-radius: var(--radius-pill);
        color: var(--color-text-primary);
    }}

    .stButton > button {{
        background: var(--color-accent-primary);
        color: var(--color-text-primary);
        border: 1px solid var(--color-accent-primary);
        border-radius: var(--radius-lg);
        padding: {spacing["space_3"]} {spacing["space_5"]};
        font-weight: var(--font-weight-semibold);
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background: var(--color-accent-hover);
        border-color: var(--color-accent-hover);
        color: var(--color-text-primary);
    }}

    .stButton > button:focus {{
        outline: none;
        box-shadow: 0 0 0 0.2rem rgba(75, 134, 245, 0.25);
    }}

    [data-testid="stMetric"] {{
        background: var(--card-background);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--card-padding);
        box-shadow: var(--card-shadow);
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--color-text-secondary);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
    }}

    [data-testid="stMetricValue"] {{
        color: var(--color-text-primary);
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid var(--color-border-subtle);
        border-radius: var(--radius-xl);
        overflow: hidden;
    }}

    .stAlert {{
        border-radius: var(--radius-lg);
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)