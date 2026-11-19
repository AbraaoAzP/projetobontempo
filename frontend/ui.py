from html import escape
from typing import Any

import streamlit as st


_MATERIAL_ICON_FALLBACKS = {
    ":material/medical_information:": "🩺",
    ":material/medical_services:": "⚕️",
    ":material/groups:": "👥",
    ":material/calendar_month:": "📅",
    ":material/clinical_notes:": "📋",
    ":material/description:": "📄",
    ":material/home:": "🏥",
    ":material/assignment:": "📋",
}


def apply_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            :root {
                color-scheme: light;
                --bt-primary: #0D9488;
                --bt-primary-dark: #0F766E;
                --bt-primary-soft: #CCFBF1;
                --bt-navy: #0F172A;
                --bt-slate: #475569;
                --bt-bg: #F1F5F9;
                --bt-card: #FFFFFF;
                --bt-border: #E2E8F0;
            }

            html, body, [class*="css"], .stApp {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }

            .stApp,
            [data-testid="stAppViewContainer"],
            [data-testid="stMain"] {
                background-color: var(--bt-bg) !important;
                color: var(--bt-navy) !important;
            }

            header[data-testid="stHeader"] {
                background: rgba(241, 245, 249, 0.88) !important;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--bt-border);
            }
            header[data-testid="stHeader"] * {
                color: var(--bt-navy) !important;
            }

            h1, h2, h3, h4 {
                color: var(--bt-navy) !important;
                font-weight: 700 !important;
                letter-spacing: -0.025em;
            }
            h1 {
                font-size: 2.05rem !important;
                margin-bottom: 0.25rem !important;
            }
            p, li, label, [data-testid="stCaptionContainer"] {
                color: var(--bt-slate);
            }

            /* Cabeçalho exclusivo Bontempo */
            .bontempo-header-card {
                background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFA 100%);
                border: 1px solid #CBD5E1;
                border-left: 5px solid var(--bt-primary);
                border-radius: 16px;
                padding: 1.35rem 1.6rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
            }
            .bontempo-eyebrow {
                display: inline-block;
                background-color: #CCFBF1;
                color: #0F766E;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.1em;
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
                margin-bottom: 0.55rem;
                text-transform: uppercase;
            }
            .bontempo-title {
                color: #0F172A;
                font-size: 1.85rem;
                font-weight: 800;
                letter-spacing: -0.03em;
                margin: 0;
                line-height: 1.2;
            }
            .bontempo-description {
                color: #475569;
                font-size: 0.98rem;
                line-height: 1.55;
                margin: 0.45rem 0 0;
                max-width: 820px;
            }

            /* Sidebar */
            [data-testid="stSidebar"],
            [data-testid="stSidebar"] > div:first-child {
                background-color: #FFFFFF !important;
                border-right: 1px solid var(--bt-border) !important;
            }
            [data-testid="stSidebar"] a {
                border-radius: 10px !important;
                margin: 2px 0 !important;
                padding: 0.45rem 0.75rem !important;
                transition: all 0.18s ease;
            }
            [data-testid="stSidebar"] a,
            [data-testid="stSidebar"] a span,
            [data-testid="stSidebar"] a p {
                color: #334155 !important;
                font-weight: 500 !important;
            }
            [data-testid="stSidebar"] a:hover {
                background-color: #F1F5F9 !important;
            }
            [data-testid="stSidebar"] a[aria-current="page"] {
                background: linear-gradient(90deg, #CCFBF1 0%, #E0F2FE 100%) !important;
                border-left: 3px solid var(--bt-primary) !important;
            }
            [data-testid="stSidebar"] a[aria-current="page"] span,
            [data-testid="stSidebar"] a[aria-current="page"] p {
                color: #0F172A !important;
                font-weight: 700 !important;
            }
            [data-testid="stSidebar"] [data-testid="stIconMaterial"],
            [data-testid="stSidebar"] span[translate="no"],
            [data-testid="stSidebar"] svg {
                color: #0D9488 !important;
                fill: #0D9488 !important;
            }

            /* Alertas limpos com APENAS UMA borda */
            [data-testid="stAlert"] {
                background-color: #F0FDFA !important;
                border: 1px solid #99F6E4 !important;
                border-left: 4px solid #0D9488 !important;
                border-radius: 12px !important;
                padding: 0.75rem 1rem !important;
                box-shadow: none !important;
            }
            [data-testid="stAlert"] > div,
            [data-testid="stAlertContainer"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
            [data-testid="stAlert"] p,
            [data-testid="stAlert"] span,
            [data-testid="stAlert"] div {
                color: #0F172A !important;
            }

            /* Containers & Cards */
            .block-container {
                max-width: 1440px;
                padding-top: 3.6rem !important;
                padding-bottom: 3rem !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 16px !important;
                box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
                transition: box-shadow 0.15s ease;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:hover {
                box-shadow: 0 8px 24px rgba(13, 148, 136, 0.08) !important;
            }
            [data-testid="stMetricValue"],
            [data-testid="stMetricValue"] * {
                color: #0F172A !important;
                font-weight: 800 !important;
            }
            [data-testid="stMetricLabel"],
            [data-testid="stMetricLabel"] * {
                color: #475569 !important;
                font-weight: 600 !important;
            }

            /* Labels e Inputs */
            [data-testid="stWidgetLabel"] p,
            [data-testid="stWidgetLabel"] label,
            [data-testid="stWidgetLabel"] span {
                color: #0F172A !important;
                font-weight: 600 !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInputRootElement"],
            [data-testid="stTextAreaRootElement"],
            [data-testid="stDateInputField"],
            [data-testid="stTimeInputTimeDisplay"],
            [data-testid="stSelectbox"] [role="combobox"],
            [data-testid="stMultiSelect"] [role="combobox"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E1 !important;
                border-radius: 10px !important;
                color: #0F172A !important;
            }
            [data-testid="stTextInputRootElement"] input,
            [data-testid="stTextAreaRootElement"] textarea,
            [data-testid="stSelectbox"] input,
            [data-testid="stMultiSelect"] input,
            [data-testid="stDateInput"] input,
            [data-testid="stTimeInput"] input {
                color: #0F172A !important;
            }
            [data-testid="stTextInputRootElement"] input::placeholder,
            [data-testid="stTextAreaRootElement"] textarea::placeholder {
                color: #64748B !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInputRootElement"]:focus-within,
            [data-testid="stTextAreaRootElement"]:focus-within,
            [data-testid="stSelectbox"] [role="combobox"]:focus-within,
            [data-testid="stMultiSelect"] [role="combobox"]:focus-within {
                border-color: var(--bt-primary) !important;
                box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
            }

            /* Dropdowns / Menus */
            [data-baseweb="popover"],
            [data-baseweb="menu"],
            [role="listbox"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 10px !important;
                color: #0F172A !important;
            }
            [role="option"] {
                color: #0F172A !important;
            }
            [role="option"]:hover,
            [role="option"][aria-selected="true"] {
                background-color: #CCFBF1 !important;
                color: #0F766E !important;
            }

            /* Botões */
            [data-testid^="stBaseButton-primary"] {
                background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important;
                border: none !important;
                border-radius: 10px !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25) !important;
            }
            [data-testid^="stBaseButton-primary"] * {
                color: #FFFFFF !important;
            }
            [data-testid^="stBaseButton-primary"]:hover {
                filter: brightness(1.05);
            }
            [data-testid^="stBaseButton-secondary"] {
                background-color: #FFFFFF !important;
                border: 1px solid #CBD5E1 !important;
                border-radius: 10px !important;
                color: #0F172A !important;
                font-weight: 600 !important;
            }
            [data-testid^="stBaseButton-secondary"]:hover {
                background-color: #F0FDFA !important;
                border-color: #0D9488 !important;
                color: #0F766E !important;
            }
            button[data-testid^="stBaseButton-"]:disabled {
                background-color: #E2E8F0 !important;
                border-color: #CBD5E1 !important;
                color: #64748B !important;
                opacity: 1 !important;
            }
            button[data-testid^="stBaseButton-"]:disabled * {
                color: #64748B !important;
            }

            /* Links de página (Acesso rápido) */
            [data-testid="stPageLink"] a {
                background-color: #F8FAFC !important;
                border: 1px solid #CBD5E1 !important;
                border-radius: 10px !important;
                color: #0F766E !important;
                font-weight: 600 !important;
                padding: 0.45rem 0.85rem !important;
                text-decoration: none !important;
                transition: all 0.15s ease;
            }
            [data-testid="stPageLink"] a:hover {
                background-color: #CCFBF1 !important;
                border-color: #0D9488 !important;
                color: #0F172A !important;
            }

            /* Expanders e Tabelas */
            [data-testid="stExpander"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
            }
            [data-testid="stExpander"] summary,
            [data-testid="stExpander"] summary * {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                font-weight: 600 !important;
            }
            [data-testid="stDataFrame"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 14px !important;
                overflow: hidden;
            }

            /* Tabela HTML clara e moderna Bontempo */
            .bt-table-wrap {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                overflow-x: auto;
                box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
                margin-bottom: 0.75rem;
            }
            .bt-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.92rem;
                color: #0F172A;
            }
            .bt-table thead {
                background: #F0FDFA;
                border-bottom: 2px solid #99F6E4;
            }
            .bt-table th {
                text-align: left;
                padding: 0.8rem 1rem;
                color: #0F766E;
                font-weight: 700;
                text-transform: uppercase;
                font-size: 0.76rem;
                letter-spacing: 0.06em;
            }
            .bt-table td {
                padding: 0.78rem 1rem;
                border-bottom: 1px solid #F1F5F9;
                color: #1E293B;
            }
            .bt-table tbody tr:nth-child(even) {
                background-color: #F8FAFC;
            }
            .bt-table tbody tr:hover {
                background-color: #F0FDFA;
            }
            .bt-table tbody tr:last-child td {
                border-bottom: none;
            }

            @media (max-width: 760px) {
                .block-container {
                    padding: 2.5rem 1rem 2rem !important;
                }
                .bontempo-title {
                    font-size: 1.45rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_page_header(title: str, description: str, icon: str) -> None:
    resolved_icon = _MATERIAL_ICON_FALLBACKS.get(icon.strip(), icon)
    st.markdown(
        f"""
        <div class="bontempo-header-card">
            <div class="bontempo-eyebrow">Bontempo · Gestão de Consultório</div>
            <h1 class="bontempo-title">{resolved_icon} {title}</h1>
            <p class="bontempo-description">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_clean_table(
    rows: list[dict[str, Any]],
    headers: dict[str, str] | None = None,
) -> None:
    if not rows:
        return
    columns = list(headers.keys()) if headers else list(rows[0].keys())
    labels = [headers[col] if headers else col for col in columns]

    thead = "".join(f"<th>{escape(str(label))}</th>" for label in labels)
    tbody_rows = []
    for row in rows:
        cells = "".join(
            f"<td>{escape(str(row.get(col, '') or '—'))}</td>" for col in columns
        )
        tbody_rows.append(f"<tr>{cells}</tr>")

    html = f"""
    <div class="bt-table-wrap">
        <table class="bt-table">
            <thead><tr>{thead}</tr></thead>
            <tbody>{"".join(tbody_rows)}</tbody>
        </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)