from typing import Any

import streamlit as st

from services.xano import (
    XanoClient,
    XanoError,
    XanoHTTPError,
    XanoSettings,
    api_enabled,
    prontuarios_api_enabled,
    prontuarios_write_enabled,
)
from services.xano_cache import (
    XanoReadRateLimit,
    clear_xano_read_caches,
    load_prontuario,
    load_prontuarios,
)
from ui import apply_styles, show_page_header


def _raise_cached_rate_limit(result: object) -> object:
    if isinstance(result, XanoReadRateLimit):
        raise XanoHTTPError(result.status_code)
    return result


def _catalog_names(records: list[dict[str, Any]]) -> dict[int, str]:
    names: dict[int, str] = {}
    for record in records:
        record_id = record.get("id")
        name = record.get("nome")
        if (
            isinstance(record_id, int)
            and not isinstance(record_id, bool)
            and record_id > 0
            and isinstance(name, str)
        ):
            names[record_id] = name
    return names


apply_styles()
show_page_header(
    "Prontuários",
    "Gerencie os registros de prontuário integrados ao Xano.",
    ":material/assignment:",
)

settings = XanoSettings.from_environment()
client = XanoClient(settings)

if not prontuarios_api_enabled():
    st.warning(
        "A leitura de Prontuários está desabilitada. Defina "
        "XANO_PRONTUARIOS_API_ENABLED=true para conectar esta página ao Xano."
    )
    st.stop()

if not settings.prontuarios_base_url or not settings.prontuarios_base_url.strip():
    st.error("XANO_PRONTUARIOS_BASE_URL não está configurada.")
    st.stop()

prontuarios: list[dict[str, Any]] = []
patients: list[dict[str, Any]] = []
professionals: list[dict[str, Any]] = []
read_failed = False

try:
    prontuarios = list(
        _raise_cached_rate_limit(
            load_prontuarios(
                settings.prontuarios_base_url,
                settings.authorization,
            )
        )
    )
except XanoError as error:
    read_failed = True
    st.error(f"Não foi possível carregar Prontuários do Xano: {error}")

if api_enabled():
    try:
        patients = client.list_records("pacientes")
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Pacientes: {error}")
    try:
        professionals = client.list_records("profissionais")
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Profissionais: {error}")
else:
    st.warning("A leitura de Pacientes e Profissionais está desabilitada.")

patient_names = _catalog_names(patients)
professional_names = _catalog_names(professionals)
write_enabled = (
    prontuarios_write_enabled()
    and not read_failed
    and bool(patient_names)
    and bool(professional_names)
)

if not write_enabled:
    st.info(
        "As gravações estão desabilitadas. Defina "
        "XANO_PRONTUARIOS_WRITE_ENABLED=true somente após autorização explícita."
    )

st.divider()
st.subheader("Cadastrar prontuário")

patient_id = st.selectbox(
    "Paciente *",
    options=list(patient_names),
    index=None,
    placeholder="Selecione um paciente",
    format_func=lambda item_id: f"{patient_names[item_id]} (#{item_id})",
    key="xano_create_prontuario_patient",
)
professional_id = st.selectbox(
    "Profissional *",
    options=list(professional_names),
    index=None,
    placeholder="Selecione um profissional",
    format_func=lambda item_id: f"{professional_names[item_id]} (#{item_id})",
    key="xano_create_prontuario_professional",
)

with st.form("xano_create_prontuario", clear_on_submit=True):
    numero_prontuario = st.text_input(
        "Número do prontuário",
        key="xano_create_prontuario_numero",
    )
    observacoes = st.text_area(
        "Observações",
        key="xano_create_prontuario_observacoes",
    )
    submitted = st.form_submit_button(
        "Cadastrar prontuário",
        type="primary",
        disabled=not write_enabled,
    )

if submitted:
    if patient_id is None or professional_id is None:
        st.error("Paciente e profissional são obrigatórios.")
    elif patient_id not in patient_names:
        st.error("O paciente selecionado não existe no catálogo carregado.")
    elif professional_id not in professional_names:
        st.error("O profissional selecionado não existe no catálogo carregado.")
    else:
        payload = {
            "paciente_id": patient_id,
            "profissional_id": professional_id,
            "numero_prontuario": numero_prontuario.strip() or None,
            "observacoes": observacoes.strip() or None,
        }
        try:
            client.create_prontuario(payload)
        except XanoError as error:
            st.error(f"Não foi possível cadastrar o prontuário: {error}")
        else:
            clear_xano_read_caches()
            st.session_state["prontuarios_feedback"] = (
                "Prontuário cadastrado no Xano."
            )
            st.rerun()

feedback = st.session_state.pop("prontuarios_feedback", None)
if feedback:
    st.success(feedback)

st.divider()
st.subheader("Consultar, editar ou excluir")

prontuario_ids = [
    int(record["id"])
    for record in prontuarios
    if isinstance(record.get("id"), int)
    and not isinstance(record["id"], bool)
    and record["id"] > 0
]

if not prontuario_ids:
    st.info("Não há prontuários válidos para consultar ou editar.")
else:
    selected_id = st.selectbox(
        "Prontuário",
        options=prontuario_ids,
        index=None,
        placeholder="Selecione um prontuário",
        key="xano_edit_prontuario_id",
    )
    if st.button(
        "Carregar prontuário",
        key="xano_load_prontuario",
        disabled=selected_id is None,
    ):
        try:
            record = _raise_cached_rate_limit(
                load_prontuario(
                    int(selected_id),
                    settings.prontuarios_base_url,
                    settings.authorization,
                )
            )
        except XanoError as error:
            st.error(f"Não foi possível carregar o Prontuário: {error}")
        else:
            st.session_state["xano_prontuario_edit"] = record

    record = st.session_state.get("xano_prontuario_edit")
    if record and int(record["id"]) == selected_id:
        prontuario_id = int(record["id"])
        with st.form(f"xano_edit_prontuario_{prontuario_id}"):
            edit_patient_id = st.selectbox(
                "Paciente *",
                options=list(patient_names),
                index=(
                    list(patient_names).index(record["paciente_id"])
                    if record["paciente_id"] in patient_names
                    else None
                ),
                format_func=lambda item_id: (
                    f"{patient_names[item_id]} (#{item_id})"
                ),
                key=f"xano_edit_prontuario_patient_{prontuario_id}",
            )
            edit_professional_id = st.selectbox(
                "Profissional *",
                options=list(professional_names),
                index=(
                    list(professional_names).index(record["profissional_id"])
                    if record["profissional_id"] in professional_names
                    else None
                ),
                format_func=lambda item_id: (
                    f"{professional_names[item_id]} (#{item_id})"
                ),
                key=f"xano_edit_prontuario_professional_{prontuario_id}",
            )
            edit_numero = st.text_input(
                "Número do prontuário",
                value=str(record.get("numero_prontuario") or ""),
                key=f"xano_edit_prontuario_numero_{prontuario_id}",
            )
            edit_observacoes = st.text_area(
                "Observações",
                value=str(record.get("observacoes") or ""),
                key=f"xano_edit_prontuario_observacoes_{prontuario_id}",
            )
            edit_submitted = st.form_submit_button(
                "Salvar alterações",
                disabled=not write_enabled,
            )

        if edit_submitted:
            if edit_patient_id is None or edit_professional_id is None:
                st.error("Paciente e profissional são obrigatórios.")
            elif (
                edit_patient_id not in patient_names
                or edit_professional_id not in professional_names
            ):
                st.error("Paciente ou profissional selecionado não existe.")
            else:
                payload: dict[str, Any] = {}
                if edit_patient_id != record["paciente_id"]:
                    payload["paciente_id"] = edit_patient_id
                if edit_professional_id != record["profissional_id"]:
                    payload["profissional_id"] = edit_professional_id
                numero_value = edit_numero.strip() or None
                if numero_value != record.get("numero_prontuario"):
                    payload["numero_prontuario"] = numero_value
                observations_value = edit_observacoes.strip() or None
                if observations_value != record.get("observacoes"):
                    payload["observacoes"] = observations_value

                if not payload:
                    st.info("Nenhuma alteração foi informada.")
                else:
                    try:
                        client.update_prontuario(prontuario_id, payload)
                    except XanoError as error:
                        st.error(
                            f"Não foi possível atualizar o Prontuário: {error}"
                        )
                    else:
                        clear_xano_read_caches()
                        st.session_state.pop("xano_prontuario_edit", None)
                        st.session_state["prontuarios_feedback"] = (
                            "Prontuário atualizado no Xano."
                        )
                        st.rerun()

        st.subheader("Excluir prontuário")
        confirmed = st.checkbox(
            f"Confirmo a exclusão do prontuário #{prontuario_id}",
            key=f"xano_delete_confirm_prontuario_{prontuario_id}",
            disabled=not write_enabled,
        )
        if st.button(
            "Excluir prontuário",
            key=f"xano_delete_prontuario_{prontuario_id}",
            type="secondary",
            disabled=not write_enabled or not confirmed,
        ):
            try:
                client.delete_prontuario(prontuario_id)
            except XanoError as error:
                st.error(f"Não foi possível excluir o Prontuário: {error}")
            else:
                clear_xano_read_caches()
                st.session_state.pop("xano_prontuario_edit", None)
                st.session_state["prontuarios_feedback"] = (
                    "Prontuário excluído no Xano."
                )
                st.rerun()
