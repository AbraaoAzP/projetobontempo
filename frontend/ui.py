import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: #f4f8fb;
                color: #17384d;
            }
            div[data-testid="stWidgetLabel"] p,
            div[data-testid="stWidgetLabel"] label,
            div[data-testid="stWidgetLabel"] span,
            .stTextInput label,
            .stSelectbox label,
            .stMultiSelect label,
            .stDateInput label,
            .stTimeInput label {
                color: #17384d !important;
                font-weight: 650 !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInputRootElement"],
            [data-testid="stTextAreaRootElement"],
            [data-testid="stDateInputField"],
            [data-testid="stTimeInputTimeDisplay"],
            [data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"],
            [data-testid="stMultiSelect"] .react-aria-ComboBox > div {
                background-color: #ffffff !important;
                border-color: #8299a8 !important;
            }
            [data-testid="stDateInputField"] [role="spinbutton"],
            [data-testid="stTimeInputTimeDisplay"] [role="spinbutton"] {
                color: #17384d !important;
            }
            [data-testid="stTextInputField"],
            [data-testid="stTextArea"] textarea,
            [data-testid="stSelectbox"] input,
            [data-testid="stMultiSelect"] input,
            [data-testid="stDateInput"] input,
            [data-testid="stTimeInput"] input {
                color: #17384d !important;
            }
            [data-testid="stTextInputField"]::placeholder,
            [data-testid="stTextArea"] textarea::placeholder,
            [data-testid="stSelectbox"] input::placeholder,
            [data-testid="stMultiSelect"] input::placeholder,
            [data-testid="stDateInput"] input::placeholder,
            [data-testid="stTimeInput"] input::placeholder {
                color: #536b7a !important;
                opacity: 1 !important;
            }
            [data-testid="stTextInputRootElement"]:focus-within,
            [data-testid="stTextAreaRootElement"]:focus-within,
            [data-testid="stDateInputField"]:focus-within,
            [data-testid="stTimeInputTimeDisplay"]:focus-within,
            [data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"]:focus-within,
            [data-testid="stMultiSelect"] .react-aria-ComboBox > div:focus-within {
                border-color: #087f8c !important;
                box-shadow: 0 0 0 1px #087f8c !important;
            }
            [data-testid^="stBaseButton-primary"] {
                background-color: #087f8c !important;
                border-color: #087f8c !important;
                color: #ffffff !important;
            }
            [data-testid^="stBaseButton-primary"]:hover {
                background-color: #06737c !important;
                border-color: #06737c !important;
            }
            [data-testid^="stBaseButton-primary"]:focus-visible {
                outline: 2px solid #124d74;
                outline-offset: 2px;
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
            main [data-testid="stAlert"] p {
                color: #17384d !important;
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
