import streamlit as st

from ui import apply_styles


st.set_page_config(
    page_title="Sistema de Gestão de Consultório",
    page_icon=":hospital:",
    layout="wide",
)

apply_styles()


def show_home() -> None:
    st.markdown(
        "<div class='bontempo-eyebrow'>Bem-vindo ao</div>",
        unsafe_allow_html=True,
    )
    st.title("🏥 Bontempo")
    st.markdown(
        "<div class='bontempo-description'>Sistema de Gestão de Consultório</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "Uma interface para apoiar a organização do consultório e facilitar o acesso aos seus módulos.",
    )
    st.divider()
    st.subheader("Acesso rápido")

    columns = st.columns(2)
    for column, page, title, description, icon in (
        (
            columns[0],
            patients_page,
            "Pacientes",
            "Acesse o módulo de gestão de pacientes.",
            ":material/groups:",
        ),
        (
            columns[1],
            professionals_page,
            "Profissionais",
            "Acesse o módulo de gestão de profissionais.",
            ":material/medical_services:",
        ),
    ):
        with column:
            with st.container(border=True):
                st.subheader(title)
                st.write(description)
                st.page_link(page, label=f"Abrir {title.lower()}", icon=icon)

    with st.container(border=True):
        st.markdown("**📅 Agenda** · Módulo futuro")
        st.caption("A organização dos atendimentos será apresentada em uma etapa futura.")


patients_page = st.Page("pages/1_Pacientes.py", title="Pacientes", icon=":material/groups:")
professionals_page = st.Page(
    "pages/2_Profissionais.py",
    title="Profissionais",
    icon=":material/medical_services:",
)
pages = [
    st.Page(show_home, title="Início", icon=":material/home:", default=True),
    patients_page,
    professionals_page,
]

st.navigation(pages, position="sidebar").run()
