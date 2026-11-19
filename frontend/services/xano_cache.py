from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from services.xano import XanoClient, XanoHTTPError, XanoSettings


XanoReadResource = Literal["pacientes", "profissionais"]


@dataclass(frozen=True)
class XanoReadRateLimit:
    status_code: int = 429


def _cache_429(operation):
    try:
        return operation()
    except XanoHTTPError as error:
        if error.status_code == 429:
            return XanoReadRateLimit()
        raise


@st.cache_data(ttl=60, show_spinner=False)
def load_records(resource: XanoReadResource, base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(lambda: XanoClient(settings).list_records(resource))


@st.cache_data(ttl=60, show_spinner=False)
def load_specialties(base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(lambda: XanoClient(settings).list_specialties())


@st.cache_data(ttl=60, show_spinner=False)
def load_professional_specialties(base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(
        lambda: XanoClient(settings).list_professional_specialties()
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_consultations(base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(lambda: XanoClient(settings).list_consultations())


@st.cache_data(ttl=60, show_spinner=False)
def load_consultation_statuses(base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(
        lambda: XanoClient(settings).list_consultation_statuses()
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_prontuarios(base_url: str, authorization: str | None):
    settings = XanoSettings.from_environment()
    return _cache_429(
        lambda: XanoClient(settings).list_prontuarios()
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_prontuario(
    prontuario_id: int,
    base_url: str,
    authorization: str | None,
):
    settings = XanoSettings.from_environment()
    return _cache_429(
        lambda: XanoClient(settings).get_prontuario(prontuario_id)
    )


def clear_xano_read_caches() -> None:
    load_records.clear()
    load_specialties.clear()
    load_professional_specialties.clear()
    load_consultations.clear()
    load_consultation_statuses.clear()
    load_prontuarios.clear()
    load_prontuario.clear()
