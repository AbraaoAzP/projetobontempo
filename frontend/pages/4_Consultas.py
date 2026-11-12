from datetime import date, datetime, time

import streamlit as st

from services import database
from services.xano import (
    XanoClient,
    XanoError,
    CONSULTATION_TIMEZONE,
    api_enabled,
    consultation_datetime_to_unix_ms,
    consultation_status_api_enabled,
    consultation_timestamp_to_local_datetime,
    consultations_api_enabled,
    specialties_api_enabled,
)
from ui import apply_styles, show_page_header


def _catalog_names(records: list[dict[str, object]]) -> dict[int, str]:
    return {
        record["id"]: record["nome"]
        for record in records
        if isinstance(record.get("id"), int)
        and not isinstance(record.get("id"), bool)
        and record["id"] > 0
        and isinstance(record.get("nome"), str)
    }


apply_styles()
xano_mode_enabled = (
    consultations_api_enabled() or consultation_status_api_enabled()
)
show_page_header(
    "Consultas",
    (
        "Consulte consultas e status no Xano."
        if xano_mode_enabled
        else "Agende consultas locais, evite conflitos de horário e acompanhe o status."
    ),
    ":material/calendar_month:",
)

if xano_mode_enabled:
    client = XanoClient()
    consultations = None
    statuses = None
    patients = None
    professionals = None
    specialties = None

    st.subheader("Consultas no Xano")
    if consultations_api_enabled():
        try:
            consultations = client.list_consultations()
        except XanoError as error:
            st.error(f"Não foi possível carregar consultas do Xano: {error}")
        else:
            if consultations:
                st.info(
                    f"{len(consultations)} consulta(s) retornada(s). "
                    "Os campos ainda não foram confirmados para exibição."
                )
            else:
                st.info("Nenhuma consulta retornada pelo Xano.")
    else:
        st.info("A leitura de Consultas no Xano está desabilitada.")

    st.subheader("Status das Consultas no Xano")
    if consultation_status_api_enabled():
        try:
            statuses = client.list_consultation_statuses()
        except XanoError as error:
            st.error(
                f"Não foi possível carregar status das Consultas do Xano: {error}"
            )
        else:
            if statuses:
                st.dataframe(
                    [
                        {
                            "id": status["id"],
                            "nome": status["nome"],
                            "created_at": status["created_at"],
                        }
                        for status in statuses
                    ],
                    hide_index=True,
                    width="stretch",
                )
            else:
                st.info("Nenhum status de Consulta retornado pelo Xano.")
    else:
        st.info("A leitura de Status das Consultas no Xano está desabilitada.")

    if api_enabled():
        try:
            patients = client.list_records("pacientes")
        except XanoError as error:
            st.error(f"Não foi possível carregar Pacientes do Xano: {error}")
        try:
            professionals = client.list_records("profissionais")
        except XanoError as error:
            st.error(f"Não foi possível carregar Profissionais do Xano: {error}")
    else:
        st.info("Habilite a leitura Xano de Pacientes e Profissionais para usar os formulários.")

    if specialties_api_enabled():
        try:
            specialties = client.list_specialties()
        except XanoError as error:
            st.error(f"Não foi possível carregar Especialidades do Xano: {error}")
    else:
        st.info("A leitura de Especialidades no Xano está desabilitada.")

    patient_names = _catalog_names(patients or [])
    professional_names = _catalog_names(professionals or [])
    specialty_names = _catalog_names(specialties or [])
    status_names = _catalog_names(statuses or [])

    if specialties is not None:
        st.warning(
            "O catálogo de Especialidades foi carregado do Xano, mas a API "
            "disponível não confirma o vínculo Profissional–Especialidade. "
            "O campo textual especialidade do Profissional não será usado "
            "como identificador; a seleção permanece bloqueada."
        )

    if consultations:
        table_rows = []
        invalid_timestamp = False
        for consultation in consultations:
            try:
                local_datetime = consultation_timestamp_to_local_datetime(
                    consultation["data_e_hora_do_agendamento"]
                )
            except ValueError:
                invalid_timestamp = True
                break
            status_id = consultation["status_consulta_id"]
            status_label = status_names.get(
                status_id,
                f"ID {status_id} (sem correspondência no catálogo carregado)",
            )
            table_rows.append(
                {
                    "ID": consultation["id"],
                    "Paciente (ID)": consultation["paciente_id"],
                    "Profissional (ID)": consultation["profissional_id"],
                    "Especialidade (ID)": consultation["especialidade_id"],
                    "Data e hora": local_datetime.strftime("%d/%m/%Y %H:%M"),
                    "Status": status_label,
                }
            )
        if invalid_timestamp:
            st.error(
                "A lista do Xano contém um timestamp de Consulta incompatível; "
                "os registros não foram exibidos."
            )
        elif table_rows:
            st.dataframe(table_rows, hide_index=True, width="stretch")

    if consultations is not None and not consultations:
        st.info("Nenhuma consulta retornada pelo Xano.")

    st.subheader("Preparar consulta")
    if consultations_api_enabled():
        with st.form("xano_create_consultation"):
            st.caption(
                "O formulário usa somente referências carregadas do Xano. "
                "IDs zero não são oferecidos."
            )
            patient_id = st.selectbox(
                "Paciente *",
                options=list(patient_names),
                index=None,
                placeholder="Selecione uma opção",
                format_func=lambda item_id: (
                    f"{patient_names[item_id]} (#{item_id})"
                ),
                key="xano_create_patient",
            )
            professional_id = st.selectbox(
                "Profissional *",
                options=list(professional_names),
                index=None,
                placeholder="Selecione uma opção",
                format_func=lambda item_id: (
                    f"{professional_names[item_id]} (#{item_id})"
                ),
                key="xano_create_professional",
            )
            specialty_id = st.selectbox(
                "Especialidade *",
                options=[],
                index=None,
                placeholder="Vínculo não confirmado",
                disabled=True,
                format_func=lambda item_id: (
                    f"{specialty_names[item_id]} (#{item_id})"
                ),
                key="xano_create_specialty",
            )
            status_id = st.selectbox(
                "Status *",
                options=list(status_names),
                index=None,
                placeholder="Selecione uma opção",
                format_func=lambda item_id: (
                    f"{status_names[item_id]} (#{item_id})"
                ),
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
            st.caption(
                "Prévia do timestamp Xano (Unix, ms): "
                f"{consultation_datetime_to_unix_ms(appointment_date, appointment_time)}"
            )
            st.text_area(
                "Observações (opcional)",
                key="xano_create_observacoes",
            )
            st.form_submit_button("Cadastrar consulta", disabled=True)

        st.warning(
            "A gravação permanece desabilitada: a relação Profissional–"
            "Especialidade e as regras de conflito/duração ainda não estão "
            "confirmadas. O contrato remoto recebe um único timestamp."
        )
    else:
        st.info("A API de Consultas está desabilitada; o formulário remoto não está disponível.")

    st.subheader("Editar ou excluir consulta")
    consultation_ids = [
        consultation["id"]
        for consultation in consultations or []
        if consultation["id"] > 0
    ]
    if consultations is not None and consultation_ids:
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
            st.session_state.pop("xano_consultation_edit", None)
            try:
                record = client.get_consultation(consultation_id)
                st.session_state["xano_consultation_edit"] = record
            except XanoError as error:
                st.error(f"Não foi possível carregar a Consulta: {error}")
            else:
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
            if "observacoes" not in record:
                st.caption("A resposta do Xano não incluiu o campo observacoes.")
            elif record["observacoes"] is None:
                st.caption("O campo observacoes está null no registro do Xano.")
            with st.form("xano_edit_consultation"):
                st.selectbox(
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
                st.selectbox(
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
                st.selectbox(
                    "Especialidade *",
                    options=[],
                    index=None,
                    placeholder="Vínculo não confirmado",
                    disabled=True,
                    format_func=lambda item_id: (
                        f"{specialty_names[item_id]} (#{item_id})"
                    ),
                    key="xano_edit_specialty",
                )
                st.selectbox(
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
                st.date_input(
                    "Data da consulta *",
                    value=local_datetime.date(),
                    key="xano_edit_date",
                )
                st.time_input(
                    "Horário da consulta *",
                    value=local_datetime.time().replace(tzinfo=None),
                    key="xano_edit_time",
                )
                st.text_area(
                    "Observações (opcional)",
                    value=record.get("observacoes") or "",
                    key="xano_edit_observacoes",
                )
                st.form_submit_button("Salvar alterações", disabled=True)
            st.button("Excluir consulta", disabled=True, key="xano_delete_consultation")
            st.caption(
                "Edição e exclusão remotas ficam desabilitadas até a validação "
                "final do CRUD. Os filtros PATCH para valores nulos/vazios "
                "ainda precisam de confirmação."
            )
    elif consultations is not None:
        st.info("Não há IDs de Consulta válidos para carregar.")

    st.caption(
        "A página não usa SQLite como fallback. Referências são selecionadas "
        "em catálogos Xano, mas sua integridade e conflitos precisam de "
        "validação no backend."
    )
    st.stop()

pacientes = database.list_patients()
profissionais = database.list_professionals()

if not pacientes:
    st.info("Cadastre ao menos um paciente antes de agendar consultas.")
if not profissionais:
    st.info("Cadastre ao menos um profissional antes de agendar consultas.")

if pacientes and profissionais:
    patient_names = {
        int(patient["id"]): str(patient["nome"]) for patient in pacientes
    }
    professional_names = {
        int(professional["id"]): str(professional["nome"])
        for professional in profissionais
    }
    professional_id = st.selectbox(
        "Profissional *",
        options=list(professional_names),
        index=None,
        placeholder="Selecione uma opção",
        format_func=lambda item_id: professional_names[item_id],
        label_visibility="visible",
    )
    professional_specialties = (
        database.list_professional_specialties(professional_id)
        if professional_id is not None
        else []
    )
    specialty_names = {
        int(specialty["id"]): str(specialty["nome"])
        for specialty in database.list_specialties()
    }
    available_specialties = [
        specialty_id
        for specialty_id in professional_specialties
        if specialty_id in specialty_names
    ]

    if professional_id is None:
        st.info("Selecione um profissional para consultar suas especialidades.")
    elif not available_specialties:
        st.warning(
            "Vincule uma especialidade ao profissional antes de agendar uma consulta."
        )
    else:
        with st.form("cadastro_consulta", clear_on_submit=True):
            st.caption("* Campos obrigatórios.")
            patient_id = st.selectbox(
                "Paciente *",
                options=[int(patient["id"]) for patient in pacientes],
                index=None,
                placeholder="Selecione uma opção",
                format_func=lambda item_id: patient_names[item_id],
                label_visibility="visible",
            )
            specialty_id = st.selectbox(
                "Especialidade *",
                options=available_specialties,
                index=None,
                placeholder="Selecione uma opção",
                format_func=lambda item_id: specialty_names[item_id],
                label_visibility="visible",
            )
            appointment_date = st.date_input(
                "Data da consulta *",
                value=date.today(),
                label_visibility="visible",
            )
            start_time = st.time_input(
                "Horário de início *",
                value=time(9, 0),
                label_visibility="visible",
            )
            end_time = st.time_input(
                "Horário de término *",
                value=time(9, 30),
                label_visibility="visible",
            )
            cadastrar = st.form_submit_button(
                "Agendar consulta",
                type="primary",
                icon=":material/event_available:",
            )

        if cadastrar:
            try:
                database.create_appointment(
                    patient_id,
                    professional_id,
                    specialty_id,
                    appointment_date,
                    start_time,
                    end_time,
                )
                st.success("Consulta agendada.")
                st.rerun()
            except database.ValidationError as error:
                st.error(str(error))
            except database.ScheduleConflictError as error:
                st.error(str(error))
            except database.DatabaseError as error:
                st.error(f"Não foi possível agendar a consulta: {error}")
else:
    professional_id = None

st.divider()
st.subheader("Consultas cadastradas")
consultas = database.list_appointments()
if consultas:
    table_rows = [
        {
            "ID": consultation["id"],
            "Data e hora inicial": database.format_local_timestamp(
                str(consultation["inicio_em"])
            ),
            "Data e hora final": database.format_local_timestamp(
                str(consultation["fim_em"])
            ),
            "Paciente": consultation["paciente_nome"],
            "Profissional": consultation["profissional_nome"],
            "Especialidade": consultation["especialidade_nome"],
            "Status": consultation["status_nome"],
        }
        for consultation in consultas
    ]
    st.dataframe(table_rows, hide_index=True, use_container_width=True)

    status_options = database.get_statuses()
    status_codes = [str(status["codigo"]) for status in status_options]
    status_names = {
        str(status["codigo"]): str(status["nome"]) for status in status_options
    }
    st.subheader("Atualizar status")
    consultation_ids = [int(item["id"]) for item in consultas]
    consultation_labels = {
        int(item["id"]): (
            f"#{item['id']} · {item['paciente_nome']} · "
            f"{database.format_local_timestamp(str(item['inicio_em']))}"
        )
        for item in consultas
    }
    with st.form("atualizar_status_consulta"):
        consultation_id = st.selectbox(
            "Consulta *",
            options=consultation_ids,
            index=None,
            placeholder="Selecione uma opção",
            format_func=lambda item_id: consultation_labels[item_id],
            label_visibility="visible",
        )
        new_status = st.selectbox(
            "Status *",
            options=status_codes,
            index=None,
            placeholder="Selecione uma opção",
            format_func=lambda code: status_names[code],
            label_visibility="visible",
        )
        atualizar = st.form_submit_button("Atualizar status")

    if atualizar:
        try:
            database.update_appointment_status(consultation_id, new_status)
            st.success("Status da consulta atualizado.")
            st.rerun()
        except database.ScheduleConflictError as error:
            st.error(str(error))
        except database.DatabaseError as error:
            st.error(f"Não foi possível atualizar o status: {error}")
else:
    st.info("Nenhuma consulta cadastrada neste banco SQLite local.")
