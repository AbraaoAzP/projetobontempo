import streamlit as st


st.set_page_config(
    page_title="Sistema de Gestão de Consultório",
    page_icon=":hospital:",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #f3f8fb;
            color: #123b52;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0e4f7a 0%, #1a7d96 100%);
        }
        div[data-testid="stSidebar"] .stSidebarNav {
            color: white;
        }
        h1, h2, h3 {
            color: #0f4c81;
            margin-bottom: 0.35rem;
        }
        .section-label {
            color: #0f4c81;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }
        .card {
            background: #ffffff;
            border: 1px solid #dfeaf3;
            border-radius: 16px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 4px 14px rgba(15, 76, 129, 0.08);
            margin-bottom: 1rem;
        }
        .card-title {
            color: #0f4c81;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .card-text {
            color: #3d5d72;
            line-height: 1.6;
        }
        .caption {
            color: #4d6980;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_home() -> None:
    st.title("Sistema de Gestão de Consultório")
    st.markdown(
        "<div class='caption'>Organização, agenda e acompanhamento do consultório em um ambiente visualmente claro.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='card'><div class='card-text'>"
        "Este sistema tem como objetivo centralizar a organização do consultório, "
        "facilitando o acompanhamento das áreas de pacientes, profissionais e da agenda em "
        "futuras etapas de evolução.</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-label'>Módulos do sistema</div>", unsafe_allow_html=True)

    cards = [
        (
            "Pacientes",
            "Acompanhe e organize a relação com os pacientes conforme o consultório evoluir.",
        ),
        (
            "Profissionais",
            "Estruture a gestão dos profissionais e a organização da atuação do consultório.",
        ),
        (
            "Agenda",
            "A agenda será organizada em etapas futuras para apoiar a gestão dos atendimentos.",
        ),
    ]

    columns = st.columns(3)
    for column, (title, description) in zip(columns, cards):
        with column:
            st.markdown(
                f"<div class='card'><div class='card-title'>{title}</div><div class='card-text'>{description}</div></div>",
                unsafe_allow_html=True,
            )


pages = [
    st.Page(show_home, title="Início", default=True),
    st.Page("pages/1_Pacientes.py", title="Pacientes"),
    st.Page("pages/2_Profissionais.py", title="Profissionais"),
]

st.navigation(pages).run()
