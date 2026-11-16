from collections.abc import Mapping, Sequence
from typing import Any

import streamlit as st

from services.xano import (
    XanoClient,
    XanoError,
    XanoSettings,
    specialties_api_enabled,
    specialties_write_enabled,
)
from ui import apply_styles, render_clean_table, show_page_header


def _duplicate_name(
    name: str,
    specialties: Sequence[Mapping[str, Any]],
    *,
    excluding_id: int | None = None,
) -> bool:
    normalized_name = name.strip().casefold()
    return any(
        specialty["id"] != excluding_id
        and specialty["nome"].strip().casefold() == normalized_name
        for specialty in specialties
    )


apply_styles()
show_page_header(
    "Especialidades",
    "Gerencie o catálogo de especialidades no Xano.",
    ":material/medical_information:",
)

feedback = st.session_state.pop("specialties_feedback", None)
if feedback:
    st.success(feedback)

settings = XanoSettings.from_environment()
client = XanoClient(settings)
enabled = specialties_api_enabled()
if not settings.specialties_base_url or not settings.specialties_base_url.strip():
    st.warning(
        "A URL da API de Especialidades não está configurada. Defina "
        "XANO_ESPECIALIDADES_BASE_URL no ambiente da aplicação."
    )
    enabled = False
elif not enabled:
    st.info(
        "A integração com o Xano está desabilitada. Defina "
        "XANO_ESPECIALIDADES_API_ENABLED=true para permitir chamadas à API."
    )

specialties: list[dict[str, Any]] = []
list_succeeded = False
if enabled:
    with st.spinner("Carregando especialidades do Xano..."):
        try:
            specialties = client.list_specialties()
        except XanoError as error:
            st.error(f"Não foi possível carregar especialidades do Xano: {error}")
        else:
            list_succeeded = True

write_enabled = enabled and list_succeeded and specialties_write_enabled()
if enabled and list_succeeded and not specialties_write_enabled():
    st.info(
        "As operações de escrita estão desabilitadas. Defina "
        "XANO_ESPECIALIDADES_WRITE_ENABLED=true para habilitá-las."
    )
elif enabled and not list_succeeded:
    st.info("As operações de escrita ficam indisponíveis sem carregar o catálogo.")

with st.form("create_specialty", clear_on_submit=True):
    st.subheader("Cadastrar especialidade")
    name = st.text_input("Nome *", key="specialty_create_name")
    create_submitted = st.form_submit_button(
        "Cadastrar especialidade",
        type="primary",
        disabled=not write_enabled,
    )

if create_submitted:
    normalized_name = name.strip()
    if not normalized_name:
        st.error("O campo nome é obrigatório.")
    elif _duplicate_name(normalized_name, specialties):
        st.error("Já existe uma especialidade com esse nome.")
    else:
        with st.spinner("Cadastrando especialidade no Xano..."):
            try:
                client.create_specialty({"nome": normalized_name})
            except XanoError as error:
                st.error(f"Não foi possível cadastrar a especialidade: {error}")
            else:
                st.session_state["specialties_feedback"] = (
                    "Especialidade cadastrada no Xano."
                )
                st.rerun()

if enabled and list_succeeded:
    st.divider()
    st.subheader("Especialidades cadastradas")
    if specialties:
        render_clean_table(
            specialties,
            headers={"id": "ID", "nome": "Especialidade"},
        )
        st.caption("Fonte: API HTTP do Xano.")
    else:
        st.info("Nenhuma especialidade cadastrada no Xano.")

if list_succeeded and specialties:
    specialty_ids = [int(specialty["id"]) for specialty in specialties]
    specialty_labels = {
        int(specialty["id"]): f"{specialty['nome']} · ID {int(specialty['id'])}"
        for specialty in specialties
    }

    with st.expander("Consultar ou editar especialidade"):
        selected_id = st.selectbox(
            "Especialidade",
            specialty_ids,
            format_func=lambda specialty_id: specialty_labels[specialty_id],
            key="specialty_edit_selection",
        )
        if st.button(
            "Carregar especialidade",
            key="specialty_load",
            disabled=not enabled,
        ):
            try:
                loaded_specialty = client.get_specialty(selected_id)
            except XanoError as error:
                st.error(f"Não foi possível consultar a especialidade: {error}")
            else:
                st.session_state.pop(
                    f"specialty_edit_name_{selected_id}", None
                )
                st.session_state["specialty_edit_record"] = loaded_specialty

        specialty_to_edit = st.session_state.get("specialty_edit_record")
        if specialty_to_edit:
            edit_id = int(specialty_to_edit["id"])
            with st.form(f"edit_specialty_{edit_id}"):
                edit_name = st.text_input(
                    "Nome *",
                    value=str(specialty_to_edit["nome"]),
                    key=f"specialty_edit_name_{edit_id}",
                )
                update_submitted = st.form_submit_button(
                    "Salvar alterações",
                    disabled=not write_enabled,
                )
            if update_submitted:
                normalized_name = edit_name.strip()
                if not normalized_name:
                    st.error("O campo nome é obrigatório.")
                elif _duplicate_name(
                    normalized_name,
                    specialties,
                    excluding_id=edit_id,
                ):
                    st.error("Já existe uma especialidade com esse nome.")
                else:
                    with st.spinner("Atualizando especialidade no Xano..."):
                        try:
                            client.update_specialty(
                                edit_id, {"nome": normalized_name}
                            )
                        except XanoError as error:
                            st.error(
                                f"Não foi possível atualizar a especialidade: "
                                f"{error}"
                            )
                        else:
                            st.session_state.pop("specialty_edit_record", None)
                            st.session_state["specialties_feedback"] = (
                                "Especialidade atualizada no Xano."
                            )
                            st.rerun()

    st.subheader("Excluir especialidade")
    st.warning(
        "A exclusão é permanente. Confirme somente a especialidade selecionada; "
        "a API pode rejeitar a operação se houver referências."
    )
    with st.container(border=True):
        delete_id = st.selectbox(
            "Selecione a especialidade para excluir",
            specialty_ids,
            format_func=lambda specialty_id: specialty_labels[specialty_id],
            key="specialty_delete_selection",
        )
        selected_specialty = next(
            s for s in specialties if int(s["id"]) == delete_id
        )
        confirmed = st.checkbox(
            f"Confirmo a exclusão de {selected_specialty['nome']}",
            key=f"specialty_delete_confirm_{delete_id}",
            disabled=not write_enabled,
        )
        if st.button(
            "Excluir especialidade",
            key=f"specialty_delete_{delete_id}",
            type="secondary",
            disabled=not write_enabled or not confirmed,
        ):
            with st.spinner("Excluindo especialidade no Xano..."):
                try:
                    client.delete_specialty(delete_id)
                except XanoError as error:
                    st.error(
                        f"Não foi possível excluir a especialidade: {error}"
                    )
                else:
                    st.session_state.pop("specialty_edit_record", None)
                    st.session_state["specialties_feedback"] = (
                        "Especialidade excluída no Xano."
                    )
                    st.rerun()

st.caption(
    "Esta página usa o catálogo Xano e não acessa o SQLite como alternativa. "
    "Consultas continua usando o catálogo SQLite local, sem sincronização."
)