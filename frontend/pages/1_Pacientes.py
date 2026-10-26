import streamlit as st

from services import database
from ui import apply_styles, show_page_header


apply_styles()
show_page_header(
    "Pacientes",
    "Consulte e organize as informações dos pacientes do consultório.",
    "👥",
)

with st.form("cadastro_paciente", clear_on_submit=True):
    st.subheader("Cadastrar paciente")
    st.caption("* Campos obrigatórios.")
    nome = st.text_input(
        "Nome *",
        placeholder="Digite o nome completo",
        label_visibility="visible",
    )
    telefone = st.text_input(
        "Telefone *",
        placeholder="Ex.: (11) 99999-9999",
        label_visibility="visible",
    )
    email = st.text_input(
        "Email",
        placeholder="Ex.: exemplo@email.com",
        help="Opcional.",
        label_visibility="visible",
    )
    cadastrar = st.form_submit_button(
        "Cadastrar paciente",
        type="primary",
        icon=":material/person_add:",
    )

if cadastrar:
    try:
        database.create_patient(nome, telefone, email)
        st.success("Paciente cadastrado.")
        st.rerun()
    except database.ValidationError as error:
        st.error(str(error))
    except database.DatabaseError as error:
        st.error(f"Não foi possível salvar o paciente: {error}")

st.divider()
st.subheader("Pacientes cadastrados")
pacientes = database.list_patients()
if pacientes:
    st.dataframe(pacientes, hide_index=True, use_container_width=True)
else:
    st.info("Nenhum paciente cadastrado neste banco SQLite local.")
