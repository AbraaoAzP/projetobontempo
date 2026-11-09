from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Literal, Mapping, Sequence

from services import database
from services.xano import (
    XANO_PACIENTES_BASE_URL_ENV,
    XANO_PROFISSIONAIS_BASE_URL_ENV,
    ResourceName,
    XanoClient,
    XanoError,
    XanoSettings,
    api_enabled,
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


@dataclass(frozen=True)
class DashboardData:
    patients: Metric
    professionals: Metric
    specialties: Metric
    consultations: ConsultationSummary


class DashboardDataError(Exception):
    """Local consultation data could not be safely summarized."""


def build_consultation_summary(
    appointments: Sequence[Mapping[str, Any]],
    statuses: Sequence[Mapping[str, Any]],
    today: date,
    now: datetime,
) -> ConsultationSummary:
    local_now = _as_local_datetime(now)
    status_names = {
        str(status["codigo"]): str(status["nome"])
        for status in statuses
    }
    status_counts = {name: 0 for name in status_names.values()}
    day_counts = {
        (today + timedelta(days=offset)).isoformat(): 0
        for offset in range(7)
    }
    upcoming: list[tuple[datetime, dict[str, str]]] = []
    today_count = 0

    for appointment in appointments:
        start = _as_local_datetime(
            _parse_datetime(appointment.get("inicio_em"))
        )
        status_code = str(appointment.get("status_codigo", ""))
        status_name = status_names.get(
            status_code,
            str(appointment.get("status_nome", "Status desconhecido")),
        )
        status_counts.setdefault(status_name, 0)
        status_counts[status_name] += 1

        if start.date() == today:
            today_count += 1
        day_key = start.date().isoformat()
        if day_key in day_counts:
            day_counts[day_key] += 1

        if status_code in database.ACTIVE_STATUS_CODES and start > local_now:
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
    local_today = today or datetime.now(database.CLINIC_TIMEZONE).date()
    local_now = now or datetime.now(database.CLINIC_TIMEZONE)

    try:
        appointments = database.list_appointment_summaries(db_path)
        statuses = database.get_statuses(db_path)
        consultation_summary = build_consultation_summary(
            appointments, statuses, local_today, local_now
        )
    except (database.DatabaseError, sqlite3.Error, ValueError, KeyError) as error:
        raise DashboardDataError(
            "Não foi possível calcular os indicadores de Consultas locais."
        ) from error

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
    specialties = Metric(
        value=None,
        state="unavailable",
        source="Xano",
        message="A integração Xano de Especialidades não está configurada.",
    )

    return DashboardData(
        patients=patients,
        professionals=professionals,
        specialties=specialties,
        consultations=consultation_summary,
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
    if not settings.authorization or not settings.authorization.strip():
        return _unavailable("A credencial de autorização Xano não está configurada.")

    try:
        records = XanoClient(settings).list_records(resource)
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


def _parse_datetime(value: object) -> datetime:
    if not isinstance(value, str):
        raise DashboardDataError("Uma consulta contém uma data/hora inválida.")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise DashboardDataError("Uma consulta não contém fuso horário.")
    return parsed


def _as_local_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise DashboardDataError("A data/hora atual precisa conter fuso horário.")
    return value.astimezone(database.CLINIC_TIMEZONE)
