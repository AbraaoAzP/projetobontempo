from collections.abc import Mapping, Sequence
from datetime import date, datetime, time
from typing import Any

import streamlit as st

from services.xano import (
    CONSULTATION_TIMEZONE,
    XanoClient,
    XanoError,
    XanoHTTPError,
    XanoSettings,
    api_enabled,
    consultation_datetime_to_unix_ms,
    consultation_status_api_enabled,
    consultation_timestamp_to_local_datetime,
    consultations_api_enabled,
    consultations_write_enabled,
    professional_specialties_api_enabled,
    specialties_api_enabled,
)
from services.xano_cache import (
    XanoReadRateLimit,
    clear_xano_read_caches,
    load_consultations,
    load_consultation_statuses,
    load_professional_specialties,
    load_records,
    load_specialties,
)
from ui import apply_styles, show_page_header


def _raise_cached_rate_limit(result: object) -> object:
    if isinstance(result, XanoReadRateLimit):
        raise XanoHTTPError(result.status_code)
    return result


def _catalog_names(records: Sequence[Mapping[str, Any]]) -> dict[int, str]:
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


def _same_schedule(
    consultations: Sequence[Mapping[str, Any]],
    professional_id: int,
    timestamp_ms: int,
    excluding_id: int | None = None,
) -> bool:
    for consultation in consultations:
        consultation_id = consultation.get("id")
        if excluding_id is not None and consultation_id == excluding_id:
            continue
        if (
            consultation.get("profissional_id") == professional_id
            and consultation.get("data_e_hora_do_agendamento") == timestamp_ms
        ):
            return True
    return False


apply_styles()
show_page_header(
    "Consultas",
    "Gerencie consultas e horários integrados ao Xano.",
    ":material/calendar_month:",
)

settings = XanoSettings.from_environment()
client = XanoClient(settings)

if not consultations_api_enabled():
    st.warning(
        "A leitura de Consultas está desabilitada. Defina "
        "XANO_CONSULTAS_API_ENABLED=true para conectar esta página ao Xano."
    )
    st.stop()

if not settings.consultations_base_url or not settings.consultations_base_url.strip():
    st.error("XANO_CONSULTAS_BASE_URL não está configurada.")
    st.stop()

consultations: list[dict[str, Any]] = []
statuses: list[dict[str, Any]] = []
patients: list[dict[str, Any]] = []
professionals: list[dict[str, Any]] = []
specialties: list[dict[str, Any]] = []
associations: list[dict[str, int]] = []

read_failed = False
try:
    consultations = list(
        _raise_cached_rate_limit(
            load_consultations(
                settings.consultations_base_url,
                settings.authorization,
            )
        )
    )
except XanoError as error:
    read_failed = True
    st.error(f"Não foi possível carregar Consultas do Xano: {error}")

if consultation_status_api_enabled():
    try:
        statuses = list(
            _raise_cached_rate_limit(
                load_consultation_statuses(
                    settings.statuses_base_url or "",
                    settings.authorization,
                )
            )
        )
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Status de Consulta: {error}")
else:
    st.warning("XANO_STATUS_CONSULTA_API_ENABLED=true não está habilitado.")

if api_enabled():
    try:
        patients = list(
            _raise_cached_rate_limit(
                load_records(
                    "pacientes",
                    settings.patients_base_url or "",
                    settings.authorization,
                )
            )
        )
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Pacientes: {error}")
    try:
        professionals = list(
            _raise_cached_rate_limit(
                load_records(
                    "profissionais",
                    settings.professionals_base_url or "",
                    settings.authorization,
                )
            )
        )
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Profissionais: {error}")
else:
    st.warning("A leitura de Pacientes e Profissionais está desabilitada.")

if specialties_api_enabled():
    try:
        specialties = list(
            _raise_cached_rate_limit(
                load_specialties(
                    settings.specialties_base_url or "",
                    settings.authorization,
                )
            )
        )
    except XanoError as error:
        read_failed = True
        st.error(f"Não foi possível carregar Especialidades: {error}")
else:
    st.warning("XANO_ESPECIALIDADES_API_ENABLED=true não está habilitado.")

if professional_specialties_api_enabled():
    try:
        associations = list(
            _raise_cached_rate_limit(
                load_professional_specialties(
                    settings.professional_specialties_base_url or "",
                    settings.authorization,
                )
            )
        )
    except XanoError as error:
        read_failed = True
        st.error(
            "Não foi possível carregar vínculos "
            f"Profissional–Especialidade: {error}"
        )
else:
    st.warning(
        "XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED=true não está habilitado."
    )

patient_names = _catalog_names(patients)
professional_names = _catalog_names(professionals)
specialty_names = _catalog_names(specialties)
status_names = _catalog_names(statuses)

valid_associations: dict[int, set[int]] = {}
invalid_associations = 0
seen_associations: set[tuple[int, int]] = set()
for association in associations:
    professional_id = association.get("profissional_id")
    specialty_id = association.get("especialidade_id")
    if (
        not isinstance(professional_id, int)
        or not isinstance(specialty_id, int)
        or professional_id not in professional_names
        or specialty_id not in specialty_names
    ):
        invalid_associations += 1
        continue
    pair = (professional_id, specialty_id)
    if pair in seen_associations:
        invalid_associations += 1
        continue
    seen_associations.add(pair)
    valid_associations.setdefault(professional_id, set()).add(specialty_id)

if invalid_associations:
    st.error(
        f"{invalid_associations} vínculo(s) inválido(s) ou duplicado(s) "
        "foram bloqueados."
    )

write_enabled = (
    not read_failed
    and consultations_write_enabled()
    and bool(patient_names)
    and bool(professional_names)
    and bool(specialty_names)
    and bool(status_names)
)

st.subheader("Consultas cadastradas")
if not consultations:
    st.info("Nenhuma consulta foi retornada pelo Xano.")
else:
    table_rows: list[dict[str, Any]] = []
    invalid_timestamp = False
    for consultation in consultations:
        try:
            local_datetime = consultation_timestamp_to_local_datetime(
                consultation["data_e_hora_do_agendamento"]
            )
        except (KeyError, ValueError):
            invalid_timestamp = True
            break
        table_rows.append(
            {
                "ID": consultation["id"],
                "Paciente": patient_names.get(
                    consultation["paciente_id"],
                    f"ID {consultation['paciente_id']}",
                ),
                "Profissional": professional_names.get(
                    consultation["profissional_id"],
                    f"ID {consultation['profissional_id']}",
                ),
                "Especialidade": specialty_names.get(
                    consultation["especialidade_id"],
                    f"ID {consultation['especialidade_id']}",
                ),
                "Data e hora": local_datetime.strftime("%d/%m/%Y %H:%M"),
                "Status": status_names.get(
                    consultation["status_consulta_id"],
                    f"ID {consultation['status_consulta_id']}",
                ),
            }
        )
    if invalid_timestamp:
        st.error("A lista contém uma Consulta com timestamp incompatível.")
    else:
        st.dataframe(table_rows, hide_index=True, width="stretch")
        st.caption("Fonte: API HTTP do Xano.")

st.divider()
st.subheader("Cadastrar consulta")

if not write_enabled:
    st.info(
        "As gravações estão desabilitadas. Defina "
        "XANO_CONSULTAS_WRITE_ENABLED=true somente após autorização explícita."
    )

professional_id = st.selectbox(
    "Profissional *",
    options=list(professional_names),
    index=None,
    placeholder="Selecione uma opção",
    format_func=lambda item_id: f"{professional_names[item_id]} (#{item_id})",
    key="xano_create_professional",
)
available_specialty_ids = (
    sorted(valid_associations.get(professional_id, set()))
    if professional_id is not None
    else []
)

with st.form("xano_create_consultation", clear_on_submit=True):
    patient_id = st.selectbox(
        "Paciente *",
        options=list(patient_names),
        index=None,
        placeholder="Selecione uma opção",
        format_func=lambda item_id: f"{patient_names[item_id]} (#{item_id})",
        key="xano_create_patient",
    )
    specialty_id = st.selectbox(
        "Especialidade *",
        options=available_specialty_ids,
        index=None,
        placeholder=(
            "Nenhum vínculo disponível"
            if professional_id is not None
            else "Selecione um profissional"
        ),
        disabled=not available_specialty_ids,
        format_func=lambda item_id: f"{specialty_names[item_id]} (#{item_id})",
        key="xano_create_specialty",
    )
    status_id = st.selectbox(
        "Status *",
        options=list(status_names),
        index=None,
        placeholder="Selecione uma opção",
        format_func=lambda item_id: f"{status_names[item_id]} (#{item_id})",
        key="xano_create_status",
    )
    appointment_date = st.date_input(
        "Data da consulta *",
        value=datetime.now(CONSULTATION_TIMEZONE).date(),
        key="xano_create_date",
    )
    appointment_time = st.time_input(
        "Horário da consulta *",
        value=time(9, 0),
        key="xano_create_time",
    )
    observations = st.text_area(
        "Observações (opcional)",
        key="xano_create_observacoes",
    )
    submitted = st.form_submit_button(
        "Cadastrar consulta",
        type="primary",
        disabled=not write_enabled,
    )

if submitted:
    if (
        patient_id is None
        or professional_id is None
        or specialty_id is None
        or status_id is None
    ):
        st.error("Paciente, profissional, especialidade e status são obrigatórios.")
    elif appointment_date < date.today():
        st.error("Não é permitido agendar uma consulta em data passada.")
    else:
        timestamp_ms = consultation_datetime_to_unix_ms(
            appointment_date,
            appointment_time,
        )
        if _same_schedule(
            consultations,
            professional_id,
            timestamp_ms,
        ):
            st.error(
                "Já existe uma consulta para este profissional no mesmo instante."
            )
        else:
            payload = {
                "paciente_id": patient_id,
                "profissional_id": professional_id,
                "especialidade_id": specialty_id,
                "data_e_hora_do_agendamento": timestamp_ms,
                "status_consulta_id": status_id,
                "observacoes": observations if observations.strip() else None,
            }
            try:
                with st.spinner("Cadastrando consulta no Xano..."):
                    client.create_consultation(payload)
            except XanoError as error:
                st.error(f"Não foi possível cadastrar a consulta: {error}")
            else:
                clear_xano_read_caches()
                st.success("Consulta cadastrada no Xano.")
                st.rerun()

st.divider()
st.subheader("Consultar, editar ou excluir")

consultation_ids = [
    int(consultation["id"])
    for consultation in consultations
    if isinstance(consultation.get("id"), int)
    and consultation["id"] > 0
]

if not consultation_ids:
    st.info("Não há consultas válidas para consultar ou editar.")
else:
    consultation_id = st.selectbox(
        "Consulta",
        options=consultation_ids,
        index=None,
        placeholder="Selecione uma consulta",
        key="xano_edit_consultation_id",
    )
    if st.button(
        "Carregar consulta",
        key="xano_load_consultation",
        disabled=consultation_id is None,
    ):
        try:
            record = client.get_consultation(consultation_id)
        except XanoError as error:
            st.error(f"Não foi possível carregar a Consulta: {error}")
        else:
            st.session_state["xano_consultation_edit"] = record
            st.rerun()

    record = st.session_state.get("xano_consultation_edit")
    if (
        isinstance(record, dict)
        and consultation_id is not None
        and record.get("id") == consultation_id
    ):
        local_datetime = consultation_timestamp_to_local_datetime(
            record["data_e_hora_do_agendamento"]
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
            key="xano_edit_professional",
        )
        edit_specialty_ids = (
            sorted(valid_associations.get(edit_professional_id, set()))
            if edit_professional_id is not None
            else []
        )

        with st.form("xano_edit_consultation"):
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
                key="xano_edit_patient",
            )
            edit_specialty_id = st.selectbox(
                "Especialidade *",
                options=edit_specialty_ids,
                index=(
                    edit_specialty_ids.index(record["especialidade_id"])
                    if record["especialidade_id"] in edit_specialty_ids
                    else None
                ),
                placeholder="Nenhum vínculo disponível",
                disabled=not edit_specialty_ids,
                format_func=lambda item_id: (
                    f"{specialty_names[item_id]} (#{item_id})"
                ),
                key="xano_edit_specialty",
            )
            edit_status_id = st.selectbox(
                "Status *",
                options=list(status_names),
                index=(
                    list(status_names).index(record["status_consulta_id"])
                    if record["status_consulta_id"] in status_names
                    else None
                ),
                format_func=lambda item_id: (
                    f"{status_names[item_id]} (#{item_id})"
                ),
                key="xano_edit_status",
            )
            edit_date = st.date_input(
                "Data da consulta *",
                value=local_datetime.date(),
                key="xano_edit_date",
            )
            edit_time = st.time_input(
                "Horário da consulta *",
                value=local_datetime.time().replace(tzinfo=None),
                key="xano_edit_time",
            )
            edit_observations = st.text_area(
                "Observações (opcional)",
                value=record.get("observacoes") or "",
                key="xano_edit_observacoes",
            )
            edit_submitted = st.form_submit_button(
                "Salvar alterações",
                disabled=not write_enabled,
            )

        if edit_submitted:
            if (
                edit_patient_id is None
                or edit_professional_id is None
                or edit_specialty_id is None
                or edit_status_id is None
            ):
                st.error(
                    "Paciente, profissional, especialidade e status são obrigatórios."
                )
            elif edit_date < date.today():
                st.error("Não é permitido definir uma consulta em data passada.")
            else:
                edit_timestamp = consultation_datetime_to_unix_ms(
                    edit_date,
                    edit_time,
                )
                if _same_schedule(
                    consultations,
                    edit_professional_id,
                    edit_timestamp,
                    excluding_id=consultation_id,
                ):
                    st.error(
                        "Já existe outra consulta para este profissional "
                        "no mesmo instante."
                    )
                else:
                    payload: dict[str, Any] = {}
                    if edit_patient_id != record["paciente_id"]:
                        payload["paciente_id"] = edit_patient_id
                    if edit_professional_id != record["profissional_id"]:
                        payload["profissional_id"] = edit_professional_id
                    if edit_specialty_id != record["especialidade_id"]:
                        payload["especialidade_id"] = edit_specialty_id
                    if edit_status_id != record["status_consulta_id"]:
                        payload["status_consulta_id"] = edit_status_id
                    if edit_timestamp != record["data_e_hora_do_agendamento"]:
                        payload["data_e_hora_do_agendamento"] = edit_timestamp
                    new_observations = (
                        edit_observations if edit_observations.strip() else None
                    )
                    if new_observations != record.get("observacoes"):
                        payload["observacoes"] = new_observations
                    if not payload:
                        st.info("Nenhuma alteração foi informada.")
                    else:
                        try:
                            with st.spinner("Atualizando consulta no Xano..."):
                                client.update_consultation(
                                    consultation_id,
                                    payload,
                                )
                        except XanoError as error:
                            st.error(
                                f"Não foi possível atualizar a consulta: {error}"
                            )
                        else:
                            clear_xano_read_caches()
                            st.session_state.pop(
                                "xano_consultation_edit",
                                None,
                            )
                            st.success("Consulta atualizada no Xano.")
                            st.rerun()

        st.subheader("Excluir consulta")
        confirmed = st.checkbox(
            f"Confirmo a exclusão da consulta #{consultation_id}",
            key=f"xano_delete_confirm_{consultation_id}",
            disabled=not write_enabled,
        )
        if st.button(
            "Excluir consulta",
            key="xano_delete_consultation",
            type="secondary",
            disabled=not write_enabled or not confirmed,
        ):
            try:
                with st.spinner("Excluindo consulta no Xano..."):
                    client.delete_consultation(consultation_id)
            except XanoError as error:
                st.error(f"Não foi possível excluir a consulta: {error}")
            else:
                clear_xano_read_caches()
                st.session_state.pop("xano_consultation_edit", None)
                st.success("Consulta excluída no Xano.")
                st.rerun()

st.caption(
    "A página usa somente APIs Xano. O frontend bloqueia o mesmo instante "
    "para o mesmo profissional; disponibilidade, duração e conflitos definitivos "
    "devem ser confirmados no backend."
)
