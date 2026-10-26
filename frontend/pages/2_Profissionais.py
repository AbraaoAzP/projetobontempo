import streamlit as st

from services import database
from ui import apply_styles, show_page_header


apply_styles()
show_page_header(
    "Profissionais",
    "Consulte os profissionais e suas áreas de atuação no consultório.",
    "🩺",
)

especialidades = database.list_specialties()
especialidade_ids = [int(especialidade["id"]) for especialidade in especialidades]
nomes_especialidades = {
    int(especialidade["id"]): str(especialidade["nome"])
    for especialidade in especialidades
}

with st.form("cadastro_profissional", clear_on_submit=True):
    st.subheader("Cadastrar profissional")
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
    especialidades_selecionadas = st.multiselect(
        "Especialidades",
        options=especialidade_ids,
        format_func=lambda specialty_id: nomes_especialidades[specialty_id],
        placeholder="Selecione uma opção",
        help="É permitido cadastrar o profissional sem especialidades durante a transição.",
        label_visibility="visible",
    )
    cadastrar = st.form_submit_button(
        "Cadastrar profissional",
        type="primary",
        icon=":material/person_add:",
    )

if cadastrar:
    try:
        database.create_professional(
            nome,
            telefone,
            email,
            especialidades_selecionadas,
        )
        st.success("Profissional cadastrado.")
        st.rerun()
    except database.ValidationError as error:
        st.error(str(error))
    except database.DatabaseError as error:
        st.error(f"Não foi possível salvar o profissional: {error}")

st.divider()
st.subheader("Profissionais cadastrados")
profissionais = database.list_professionals()
if profissionais:
    st.dataframe(profissionais, hide_index=True, use_container_width=True)
    st.subheader("Gerenciar especialidades dos profissionais")
    for profissional in profissionais:
        professional_id = int(profissional["id"])
        with st.expander(f"{profissional['nome']} · ID {professional_id}"):
            with st.form(f"especialidades_profissional_{professional_id}"):
                selected = st.multiselect(
                    "Especialidades vinculadas",
                    options=especialidade_ids,
                    default=database.list_professional_specialties(professional_id),
                    format_func=lambda specialty_id: nomes_especialidades[specialty_id],
                    placeholder="Selecione uma opção",
                    key=f"vinculos_{professional_id}",
                    label_visibility="visible",
                )
                salvar = st.form_submit_button("Salvar vínculos")
            if salvar:
                try:
                    database.set_professional_specialties(professional_id, selected)
                    st.success("Vínculos atualizados.")
                    st.rerun()
                except database.DatabaseError as error:
                    st.error(str(error))
else:
    st.info("Nenhum profissional cadastrado neste banco SQLite local.")
