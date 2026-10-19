import streamlit as st


st.set_page_config(
    page_title="Sistema de Gestão de Consultório",
    page_icon=":hospital:",
    layout="wide",
)


def show_home() -> None:
    st.title("Sistema de Gestão de Consultório")
    st.write(
        "Bem-vindo. Utilize a navegação para acessar as áreas de pacientes "
        "e profissionais."
    )


pages = [
    st.Page(show_home, title="Início", default=True),
    st.Page("pages/1_Pacientes.py", title="Pacientes"),
    st.Page("pages/2_Profissionais.py", title="Profissionais"),
]

st.navigation(pages).run()
