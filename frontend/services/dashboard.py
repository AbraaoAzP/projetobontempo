from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Literal, Mapping, Sequence
from zoneinfo import ZoneInfo

from services.xano_cache import (
    XanoReadRateLimit,
    load_consultations,
    load_consultation_statuses,
    load_records,
    load_specialties,
)
from services.xano import (
    XANO_CONSULTAS_BASE_URL_ENV,
    XANO_ESPECIALIDADES_BASE_URL_ENV,
    XANO_PACIENTES_BASE_URL_ENV,
    XANO_PROFISSIONAIS_BASE_URL_ENV,
    XANO_STATUS_CONSULTA_BASE_URL_ENV,
    ResourceName,
    XanoClient,
    XanoError,
    XanoSettings,
    api_enabled,
    consultation_timestamp_to_local_datetime,
    consultation_status_api_enabled,
    consultations_api_enabled,
    specialties_api_enabled,
)


MetricState = Literal["available", "unavailable", "error"]


@dataclass(frozen=True)
class Metric:
    value: int | None
    state: MetricState
    source: str
    message: str | None = None


@dataclass(frozen=True)
class ConsultationSummary:
    total: int
    today: int
    status_counts: dict[str, int]
    next_seven_days: dict[str, int]
    upcoming: list[dict[str, str]]
    state: MetricState = "available"
    message: str | None = None


@dataclass(frozen=True)
class DashboardData:
    patients: Metric
    professionals: Metric
    specialties: Metric
    consultations: ConsultationSummary


class DashboardDataError(Exception):
    """Consultation data could not be safely summarized."""


CLINIC_TIMEZONE = ZoneInfo("America/Sao_Paulo")
ACTIVE_STATUS_NAMES = frozenset({"agendada", "confirmada"})


def build_consultation_summary(
    appointments: Sequence[Mapping[str, Any]],
    statuses: Sequence[Mapping[str, Any]],
    today: date,
    now: datetime,
) -> ConsultationSummary:
    local_now = _as_local_datetime(now)
    status_names = _status_name_map(statuses)
    status_counts = {name: 0 for name in status_names.values()}
    day_counts = {
        (today + timedelta(days=offset)).isoformat(): 0
        for offset in range(7)
    }
    upcoming: list[tuple[datetime, dict[str, str]]] = []
    today_count = 0

    for appointment in appointments:
        start = _appointment_start(appointment)
        status_name = _appointment_status_name(appointment, status_names)
        status_counts.setdefault(status_name, 0)
        status_counts[status_name] += 1

        if start.date() == today:
            today_count += 1
        day_key = start.date().isoformat()
        if day_key in day_counts:
            day_counts[day_key] += 1

        if _normalized_status_name(status_name) in ACTIVE_STATUS_NAMES and start > local_now:
            upcoming.append(
                (
                    start,
                    {
                        "Data": start.strftime("%d/%m/%Y"),
                        "Horário": start.strftime("%H:%M"),
                        "Status": status_name,
                    },
                )
            )

    upcoming.sort(key=lambda item: item[0])
    return ConsultationSummary(
        total=len(appointments),
        today=today_count,
        status_counts=status_counts,
        next_seven_days={
            (today + timedelta(days=offset)).strftime("%d/%m"): day_counts[
                (today + timedelta(days=offset)).isoformat()
            ]
            for offset in range(7)
        },
        upcoming=[item[1] for item in upcoming[:8]],
    )


def load_dashboard(
    *,
    today: date | None = None,
    now: datetime | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> DashboardData:
    del db_path
    local_today = today or datetime.now(CLINIC_TIMEZONE).date()
    local_now = now or datetime.now(CLINIC_TIMEZONE)
    consultation_summary = _load_xano_consultation_summary(
        local_today,
        local_now,
    )

    settings = XanoSettings.from_environment()
    patients = _load_xano_count(
        "pacientes",
        settings,
        XANO_PACIENTES_BASE_URL_ENV,
    )
    professionals = _load_xano_count(
        "profissionais",
        settings,
        XANO_PROFISSIONAIS_BASE_URL_ENV,
    )
    specialties = _load_specialties_count(settings)

    return DashboardData(
        patients=patients,
        professionals=professionals,
        specialties=specialties,
        consultations=consultation_summary,
    )


def _load_xano_consultation_summary(
    today: date,
    now: datetime,
) -> ConsultationSummary:
    settings = XanoSettings.from_environment()
    if not consultations_api_enabled():
        return _unavailable_consultation_summary(
            "A integração Xano de Consultas não está configurada."
        )
    if not consultation_status_api_enabled():
        return _unavailable_consultation_summary(
            "A integração Xano de Status da Consulta não está configurada."
        )
    if not os.getenv(XANO_CONSULTAS_BASE_URL_ENV, "").strip():
        return _unavailable_consultation_summary(
            "A URL da API de Consultas não está configurada."
        )
    if not os.getenv(XANO_STATUS_CONSULTA_BASE_URL_ENV, "").strip():
        return _unavailable_consultation_summary(
            "A URL da API de Status da Consulta não está configurada."
        )

    try:
        consultations = load_consultations(
            settings.consultations_base_url or "",
            settings.authorization,
        )
        if isinstance(consultations, XanoReadRateLimit):
            raise XanoHTTPError(consultations.status_code)
        statuses = load_consultation_statuses(
            settings.statuses_base_url or "",
            settings.authorization,
        )
        if isinstance(statuses, XanoReadRateLimit):
            raise XanoHTTPError(statuses.status_code)
        summary = build_consultation_summary(
            consultations,
            statuses,
            today,
            now,
        )
    except (XanoError, DashboardDataError) as error:
        return ConsultationSummary(
            total=0,
            today=0,
            status_counts={},
            next_seven_days={
                (today + timedelta(days=offset)).strftime("%d/%m"): 0
                for offset in range(7)
            },
            upcoming=[],
            state="error",
            message=f"Falha ao consultar o Xano: {error}",
        )

    return ConsultationSummary(
        total=summary.total,
        today=summary.today,
        status_counts=summary.status_counts,
        next_seven_days=summary.next_seven_days,
        upcoming=summary.upcoming,
        state="available",
        message="API Xano configurada",
    )


def _unavailable_consultation_summary(message: str) -> ConsultationSummary:
    return ConsultationSummary(
        total=0,
        today=0,
        status_counts={},
        next_seven_days={},
        upcoming=[],
        state="unavailable",
        message=message,
    )


def _load_specialties_count(settings: XanoSettings) -> Metric:
    if not api_enabled():
        return _unavailable("A integração Xano está desabilitada.")
    if not specialties_api_enabled():
        return _unavailable("A integração Xano de Especialidades não está configurada.")
    if not os.getenv(XANO_ESPECIALIDADES_BASE_URL_ENV, "").strip():
        return _unavailable("A URL da API de Especialidades não está configurada.")

    try:
        records = load_specialties(
            settings.specialties_base_url or "",
            settings.authorization,
        )
        if isinstance(records, XanoReadRateLimit):
            raise XanoHTTPError(records.status_code)
    except XanoError as error:
        return Metric(
            value=None,
            state="error",
            source="Xano",
            message=f"Falha ao consultar o Xano: {error}",
        )
    return Metric(
        value=len(records),
        state="available",
        source="Xano",
        message="API Xano configurada",
    )


def _load_xano_count(
    resource: ResourceName,
    settings: XanoSettings,
    base_url_environment: str,
) -> Metric:
    if not api_enabled():
        return _unavailable("A integração Xano está desabilitada.")
    if not os.getenv(base_url_environment, "").strip():
        return _unavailable("A URL da API não está configurada.")
    try:
        base_url = settings.base_url_for(resource)
        records = load_records(
            resource,
            base_url or "",
            settings.authorization,
        )
        if isinstance(records, XanoReadRateLimit):
            raise XanoHTTPError(records.status_code)
    except XanoError as error:
        return Metric(
            value=None,
            state="error",
            source="Xano",
            message=f"Falha ao consultar o Xano: {error}",
        )
    return Metric(
        value=len(records),
        state="available",
        source="Xano",
        message="API Xano configurada",
    )


def _unavailable(message: str) -> Metric:
    return Metric(
        value=None,
        state="unavailable",
        source="Xano",
        message=message,
    )


def _status_name_map(statuses: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for status in statuses:
        status_id = status.get("id")
        name = status.get("nome")
        if isinstance(status_id, int) and not isinstance(status_id, bool) and isinstance(name, str):
            names[str(status_id)] = name
        elif isinstance(status.get("codigo"), str) and isinstance(status.get("nome"), str):
            names[str(status["codigo"])] = str(status["nome"])
    return names


def _appointment_start(appointment: Mapping[str, Any]) -> datetime:
    if "data_e_hora_do_agendamento" in appointment:
        timestamp = appointment["data_e_hora_do_agendamento"]
        if isinstance(timestamp, bool) or not isinstance(timestamp, int):
            raise DashboardDataError(
                "Uma consulta contém timestamp inválido."
            )
        try:
            return consultation_timestamp_to_local_datetime(timestamp)
        except ValueError as error:
            raise DashboardDataError(
                "Uma consulta contém timestamp fora do intervalo."
            ) from error

    value = appointment.get("inicio_em")
    if not isinstance(value, str):
        raise DashboardDataError("Uma consulta contém uma data/hora inválida.")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise DashboardDataError("Uma consulta não contém fuso horário.")
    return parsed.astimezone(CLINIC_TIMEZONE)


def _appointment_status_name(
    appointment: Mapping[str, Any],
    status_names: Mapping[str, str],
) -> str:
    if "status_consulta_id" in appointment:
        status_id = appointment["status_consulta_id"]
        if isinstance(status_id, int) and not isinstance(status_id, bool):
            return status_names.get(str(status_id), "Status desconhecido")
    status_code = appointment.get("status_codigo")
    if status_code is not None:
        return status_names.get(str(status_code), str(appointment.get("status_nome", "Status desconhecido")))
    return str(appointment.get("status_nome", "Status desconhecido"))


def _normalized_status_name(name: str) -> str:
    normalized = (
        name.strip()
        .lower()
        .replace("ã", "a")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    return normalized


def _as_local_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise DashboardDataError("A data/hora atual precisa conter fuso horário.")
    return value.astimezone(CLINIC_TIMEZONE)