import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #f4f8fb;
                color: #17384d;
            }
            .block-container {
                max-width: 1440px;
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            h1, h2, h3 {
                color: #124d74;
                letter-spacing: -0.025em;
            }
            h1 {
                margin-bottom: 0.25rem;
            }
            .bontempo-eyebrow {
                color: #087f8c;
                font-size: 0.78rem;
                font-weight: 750;
                letter-spacing: 0.12em;
                margin-bottom: 0.4rem;
                text-transform: uppercase;
            }
            .bontempo-description {
                color: #547083;
                font-size: 1.02rem;
                line-height: 1.65;
                margin: 0.2rem 0 1.2rem;
                max-width: 820px;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #ffffff;
                border-color: #dce8ef;
                border-radius: 16px;
                box-shadow: 0 5px 18px rgba(18, 77, 116, 0.06);
            }
            div[data-testid="stVerticalBlockBorderWrapper"] h3 {
                margin-bottom: 0.35rem;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] p {
                color: #547083;
                line-height: 1.6;
            }
            div[data-testid="stDataFrame"] {
                border: 1px solid #dce8ef;
                border-radius: 12px;
                overflow: hidden;
            }
            [data-testid="stAlert"] {
                border-radius: 12px;
            }
            @media (max-width: 760px) {
                .block-container {
                    padding: 1.25rem 1rem 2rem;
                }
                .bontempo-description {
                    font-size: 0.95rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_page_header(title: str, description: str, icon: str) -> None:
    st.markdown(
        "<div class='bontempo-eyebrow'>Bontempo · Gestão de Consultório</div>",
        unsafe_allow_html=True,
    )
    st.title(f"{icon} {title}")
    st.markdown(
        f"<div class='bontempo-description'>{description}</div>",
        unsafe_allow_html=True,
    )
