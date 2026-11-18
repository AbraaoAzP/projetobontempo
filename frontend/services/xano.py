from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal, Mapping, Protocol
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import requests


XANO_PACIENTES_BASE_URL_ENV = "XANO_PACIENTES_BASE_URL"
XANO_PROFISSIONAIS_BASE_URL_ENV = "XANO_PROFISSIONAIS_BASE_URL"
XANO_PACIENTES_WRITE_ENABLED_ENV = "XANO_PACIENTES_WRITE_ENABLED"
XANO_PROFISSIONAIS_WRITE_ENABLED_ENV = "XANO_PROFISSIONAIS_WRITE_ENABLED"
XANO_ESPECIALIDADES_BASE_URL_ENV = "XANO_ESPECIALIDADES_BASE_URL"
XANO_CONSULTAS_BASE_URL_ENV = "XANO_CONSULTAS_BASE_URL"
XANO_STATUS_CONSULTA_BASE_URL_ENV = "XANO_STATUS_CONSULTA_BASE_URL"
XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL_ENV = (
    "XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL"
)
XANO_PROFISSIONAIS_ESPECIALIDADES_BASE_URL_ENV = (
    "XANO_PROFISSIONAIS_ESPECIALIDADES_BASE_URL"
)
XANO_PRONTUARIOS_BASE_URL_ENV = "XANO_PRONTUARIOS_BASE_URL"
XANO_AUTHORIZATION_ENV = "XANO_AUTHORIZATION"
XANO_API_ENABLED_ENV = "XANO_API_ENABLED"
XANO_ESPECIALIDADES_API_ENABLED_ENV = "XANO_ESPECIALIDADES_API_ENABLED"
XANO_ESPECIALIDADES_WRITE_ENABLED_ENV = "XANO_ESPECIALIDADES_WRITE_ENABLED"
XANO_CONSULTAS_API_ENABLED_ENV = "XANO_CONSULTAS_API_ENABLED"
XANO_STATUS_CONSULTA_API_ENABLED_ENV = "XANO_STATUS_CONSULTA_API_ENABLED"
XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV = (
    "XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED"
)
XANO_CONSULTAS_WRITE_ENABLED_ENV = "XANO_CONSULTAS_WRITE_ENABLED"
DEFAULT_PACIENTES_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:consultorio-cadastro-pacientes"
)

DEFAULT_PROFISSIONAIS_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:consultorio-cadastro-profissionais"
)

DEFAULT_ESPECIALIDADES_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:Cv9TB_MS"
)
REQUEST_TIMEOUT_SECONDS = 5

ResourceName = Literal["pacientes", "profissionais"]
XanoResourceName = Literal[
    "pacientes",
    "profissionais",
    "especialidades",
    "consultas",
    "status_consulta",
    "profissional_especialidade",
]

CONSULTATION_PAYLOAD_FIELDS = (
    "paciente_id",
    "profissional_id",
    "especialidade_id",
    "data_e_hora_do_agendamento",
    "status_consulta_id",
    "observacoes",
)
CONSULTATION_INTEGER_FIELDS = frozenset(
    {
        "paciente_id",
        "profissional_id",
        "especialidade_id",
        "status_consulta_id",
    }
)
CONSULTATION_REQUIRED_FIELDS = (
    "paciente_id",
    "profissional_id",
    "especialidade_id",
    "data_e_hora_do_agendamento",
    "status_consulta_id",
)
CONSULTATION_TIMEZONE = ZoneInfo("America/Sao_Paulo")
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

RESOURCE_FIELDS: dict[ResourceName, tuple[str, ...]] = {
    "pacientes": ("id", "nome", "telefone", "email"),
    "profissionais": ("id", "nome", "telefone", "email", "especialidade"),
}
RESOURCE_PAYLOAD_FIELDS: dict[ResourceName, tuple[str, ...]] = {
    "pacientes": ("nome", "telefone", "email"),
    "profissionais": ("nome", "telefone", "email", "especialidade"),
}
OPTIONAL_RESOURCE_FIELDS = frozenset({"telefone", "email", "especialidade"})


def api_enabled() -> bool:
    return os.getenv(XANO_API_ENABLED_ENV, "").strip().lower() == "true"


def patients_write_enabled() -> bool:
    return (
        os.getenv(XANO_PACIENTES_WRITE_ENABLED_ENV, "").strip().lower()
        == "true"
    )


def professionals_write_enabled() -> bool:
    return (
        os.getenv(XANO_PROFISSIONAIS_WRITE_ENABLED_ENV, "").strip().lower()
        == "true"
    )


def specialties_api_enabled() -> bool:
    return (
        os.getenv(XANO_ESPECIALIDADES_API_ENABLED_ENV, "").strip().lower()
        == "true"
    )


def specialties_write_enabled() -> bool:
    return (
        os.getenv(XANO_ESPECIALIDADES_WRITE_ENABLED_ENV, "").strip().lower()
        == "true"
    )


class XanoError(Exception):
    """Erro esperado ao comunicar com as APIs do Xano."""


class XanoConfigurationError(XanoError):
    """Configuração externa da API ausente ou inválida."""


class XanoHTTPError(XanoError):
    """A API do Xano respondeu com um status HTTP de erro."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        if status_code == 429:
            message = (
                "O Xano limitou temporariamente a requisição (HTTP 429). "
                "Nenhuma nova tentativa foi enviada; consulte a listagem antes "
                "de repetir para evitar duplicidade."
            )
        else:
            message = f"O Xano respondeu com erro HTTP {status_code}."
        super().__init__(message)


class XanoTimeoutError(XanoError):
    """A requisição ao Xano excedeu o tempo limite."""


class XanoConnectionError(XanoError):
    """Não foi possível estabelecer conexão com o Xano."""


class XanoTransportError(XanoError):
    """O transporte HTTP encontrou uma falha inesperada."""


class XanoResponseError(XanoError):
    """A resposta do Xano não corresponde ao contrato configurado."""


@dataclass(frozen=True)
class ResourceEndpoints:
    collection_path: str | None = None
    item_path: str | None = None
    create_path: str | None = None
    update_path: str | None = None
    delete_path: str | None = None
    identifier_parameter: str = "id"


@dataclass(frozen=True)
class XanoSettings:
    patients_base_url: str | None = DEFAULT_PACIENTES_BASE_URL
    professionals_base_url: str | None = DEFAULT_PROFISSIONAIS_BASE_URL
    patients: ResourceEndpoints = ResourceEndpoints()
    professionals: ResourceEndpoints = ResourceEndpoints()
    authorization: str | None = None
    specialties_base_url: str | None = DEFAULT_ESPECIALIDADES_BASE_URL
    specialties: ResourceEndpoints = ResourceEndpoints()
    consultations_base_url: str | None = None
    consultations: ResourceEndpoints = ResourceEndpoints(
        collection_path="consulta",
        item_path="consulta/{consulta_id}",
        create_path="consulta",
        update_path="consulta/{consulta_id}",
        delete_path="consulta/{consulta_id}",
        identifier_parameter="consulta_id",
    )
    statuses_base_url: str | None = None
    statuses: ResourceEndpoints = ResourceEndpoints(
        collection_path="status_consulta"
    )
    professional_specialties_base_url: str | None = None
    professional_specialties: ResourceEndpoints = ResourceEndpoints(
        collection_path="profissional_especialidade"
    )

    @classmethod
    def from_environment(cls) -> XanoSettings:
        return cls(
            patients_base_url=os.getenv(
                XANO_PACIENTES_BASE_URL_ENV, DEFAULT_PACIENTES_BASE_URL
            ),
            professionals_base_url=os.getenv(
                XANO_PROFISSIONAIS_BASE_URL_ENV,
                DEFAULT_PROFISSIONAIS_BASE_URL,
            ),
            specialties_base_url=os.getenv(
                XANO_ESPECIALIDADES_BASE_URL_ENV,
                DEFAULT_ESPECIALIDADES_BASE_URL,
            ),
            consultations_base_url=os.getenv(XANO_CONSULTAS_BASE_URL_ENV),
            statuses_base_url=os.getenv(XANO_STATUS_CONSULTA_BASE_URL_ENV),
            professional_specialties_base_url=os.getenv(
                XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL_ENV,
                os.getenv(XANO_PROFISSIONAIS_ESPECIALIDADES_BASE_URL_ENV),
            ),
            patients=_endpoints_from_environment(
                "PACIENTES",
                ResourceEndpoints(
                    collection_path="pacientes",
                    item_path="paciente/{paciente_id}",
                    create_path="pacientes",
                    update_path="paciente/{paciente_id}",
                    delete_path="paciente/{paciente_id}",
                    identifier_parameter="paciente_id",
                ),
            ),
            professionals=_endpoints_from_environment(
                "PROFISSIONAIS",
                ResourceEndpoints(
                    collection_path="profissionais",
                    item_path="profissional/{profissional_id}",
                    create_path="profissionais",
                    update_path="profissional/{profissional_id}",
                    delete_path="profissional/{profissional_id}",
                    identifier_parameter="profissional_id",
                ),
            ),
            specialties=_endpoints_from_environment(
                "ESPECIALIDADES",
                ResourceEndpoints(
                    collection_path="especialidade",
                    item_path="especialidade/{especialidade_id}",
                    create_path="especialidade",
                    update_path="especialidade/{especialidade_id}",
                    delete_path="especialidade/{especialidade_id}",
                    identifier_parameter="especialidade_id",
                ),
            ),
            consultations=ResourceEndpoints(
                collection_path="consulta",
                item_path="consulta/{consulta_id}",
                create_path="consulta",
                update_path="consulta/{consulta_id}",
                delete_path="consulta/{consulta_id}",
                identifier_parameter="consulta_id",
            ),
            statuses=ResourceEndpoints(
                collection_path="status_consulta"
            ),
            professional_specialties=ResourceEndpoints(
                collection_path="profissional_especialidade"
            ),
            authorization=os.getenv(XANO_AUTHORIZATION_ENV),
        )

    def endpoints_for(self, resource: XanoResourceName) -> ResourceEndpoints:
        if resource == "pacientes":
            return self.patients
        if resource == "profissionais":
            return self.professionals
        if resource == "especialidades":
            return self.specialties
        if resource == "consultas":
            return self.consultations
        if resource == "status_consulta":
            return self.statuses
        if resource == "profissional_especialidade":
            return self.professional_specialties
        raise ValueError(f"Recurso Xano não suportado: {resource}")

    def base_url_for(self, resource: XanoResourceName) -> str | None:
        if resource == "pacientes":
            return self.patients_base_url
        if resource == "profissionais":
            return self.professionals_base_url
        if resource == "especialidades":
            return self.specialties_base_url
        if resource == "consultas":
            return self.consultations_base_url
        if resource == "status_consulta":
            return self.statuses_base_url
        if resource == "profissional_especialidade":
            return self.professional_specialties_base_url
        raise ValueError(f"Recurso Xano não suportado: {resource}")


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float,
    ) -> requests.Response: ...


class XanoClient:
    def __init__(
        self,
        settings: XanoSettings | None = None,
        transport: HttpTransport | None = None,
    ) -> None:
        self._settings = settings or XanoSettings.from_environment()
        self._transport = transport or requests.Session()

    def list_records(self, resource: ResourceName) -> list[dict[str, Any]]:
        endpoints = self._settings.endpoints_for(resource)
        response = self._send(resource, "GET", endpoints.collection_path)
        data = _parse_json(response)
        if not isinstance(data, list):
            raise XanoResponseError("A resposta do Xano não é uma lista.")
        return [_validate_record(resource, item) for item in data]

    def get_record(self, resource: ResourceName, record_id: int) -> dict[str, Any]:
        endpoints = self._settings.endpoints_for(resource)
        path = _format_item_path(
            endpoints.item_path, record_id, endpoints.identifier_parameter
        )
        return _validate_record(
            resource, _parse_json(self._send(resource, "GET", path))
        )

    def create_record(
        self,
        resource: ResourceName,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        _require_resource_writes_enabled(resource)
        endpoints = self._settings.endpoints_for(resource)
        clean_payload = _validate_payload(
            resource,
            payload,
            require_name=True,
            trim_text=True,
        )
        response = self._send(
            resource, "POST", endpoints.create_path, clean_payload
        )
        return _validate_record(resource, _parse_json(response))

    def update_record(
        self,
        resource: ResourceName,
        record_id: int,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        _require_resource_writes_enabled(resource)
        endpoints = self._settings.endpoints_for(resource)
        path = _format_item_path(
            endpoints.update_path, record_id, endpoints.identifier_parameter
        )
        clean_payload = _validate_payload(resource, payload, require_name=False)
        response = self._send(resource, "PATCH", path, clean_payload)
        return _validate_record(resource, _parse_json(response))

    def delete_record(self, resource: ResourceName, record_id: int) -> None:
        _require_resource_writes_enabled(resource)
        endpoints = self._settings.endpoints_for(resource)
        path = _format_item_path(
            endpoints.delete_path, record_id, endpoints.identifier_parameter
        )
        response = self._send(resource, "DELETE", path)
        result = _parse_json(response)
        if not isinstance(result, dict) or result.get("success") is not True:
            raise XanoResponseError(
                "A resposta de exclusão do Xano não confirmou o sucesso."
            )

    def list_specialties(self) -> list[dict[str, Any]]:
        _require_specialties_api_enabled()
        endpoints = self._settings.endpoints_for("especialidades")
        response = self._send("especialidades", "GET", endpoints.collection_path)
        data = _parse_json(response)
        if not isinstance(data, list):
            raise XanoResponseError("A resposta do Xano não é uma lista.")
        return [_validate_specialty_record(item) for item in data]

    def get_specialty(self, specialty_id: int) -> dict[str, Any]:
        _require_specialties_api_enabled()
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.item_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        return _validate_specialty_record(
            _parse_json(self._send("especialidades", "GET", path))
        )

    def create_specialty(
        self, payload: Mapping[str, Any]
    ) -> dict[str, Any]:
        endpoints = self._settings.endpoints_for("especialidades")
        clean_payload = _validate_specialty_payload(payload)
        _require_specialty_writes_enabled()
        response = self._send(
            "especialidades", "POST", endpoints.create_path, clean_payload
        )
        return _validate_specialty_record(_parse_json(response))

    def update_specialty(
        self, specialty_id: int, payload: Mapping[str, Any]
    ) -> dict[str, Any]:
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.update_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        clean_payload = _validate_specialty_payload(payload)
        _require_specialty_writes_enabled()
        response = self._send(
            "especialidades", "PATCH", path, clean_payload
        )
        return _validate_specialty_record(_parse_json(response))

    def delete_specialty(self, specialty_id: int) -> None:
        _require_specialty_writes_enabled()
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.delete_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        self._send("especialidades", "DELETE", path)

    def list_consultations(self) -> list[dict[str, Any]]:
        _require_consultations_api_enabled()
        endpoints = self._settings.endpoints_for("consultas")
        data = _parse_json(
            self._send("consultas", "GET", endpoints.collection_path)
        )
        if not isinstance(data, list):
            raise XanoResponseError(
                "A resposta de Consultas do Xano não é uma lista."
            )
        return [_validate_consultation_record(item) for item in data]

    def get_consultation(self, consultation_id: int) -> dict[str, Any]:
        _require_consultations_api_enabled()
        endpoints = self._settings.endpoints_for("consultas")
        path = _format_consultation_path(
            endpoints.item_path,
            consultation_id,
            endpoints.identifier_parameter,
        )
        response = self._send("consultas", "GET", path)
        record = _validate_consultation_record(_parse_json(response))
        if record["id"] != consultation_id:
            raise XanoResponseError(
                "O Xano retornou uma Consulta diferente do ID solicitado."
            )
        return record

    def list_consultation_statuses(self) -> list[dict[str, Any]]:
        _require_status_consulta_api_enabled()
        endpoints = self._settings.endpoints_for("status_consulta")
        data = _parse_json(
            self._send(
                "status_consulta",
                "GET",
                endpoints.collection_path,
            )
        )
        if not isinstance(data, list):
            raise XanoResponseError(
                "A resposta de Status da Consulta do Xano não é uma lista."
            )
        return [_validate_consultation_status(item) for item in data]

    def list_professional_specialties(self) -> list[dict[str, int]]:
        _require_professional_specialties_api_enabled()
        endpoints = self._settings.endpoints_for("profissional_especialidade")
        data = _parse_json(
            self._send(
                "profissional_especialidade",
                "GET",
                endpoints.collection_path,
            )
        )
        if not isinstance(data, list):
            raise XanoResponseError(
                "A resposta de vínculos Profissional–Especialidade "
                "do Xano não é uma lista."
            )
        records = [_validate_professional_specialty(item) for item in data]
        pairs = {(item["profissional_id"], item["especialidade_id"]) for item in records}
        if len(pairs) != len(records):
            raise XanoResponseError(
                "A resposta do Xano contém vínculos Profissional–Especialidade duplicados."
            )
        return records

    def create_consultation(
        self, payload: Mapping[str, Any]
    ) -> Any:
        _require_consultation_writes_enabled()
        endpoints = self._settings.endpoints_for("consultas")
        clean_payload = _validate_consultation_payload(
            payload,
            require_complete=True,
        )
        response = self._send(
            "consultas",
            "POST",
            endpoints.create_path,
            clean_payload,
        )
        return _parse_json(response)

    def update_consultation(
        self,
        consultation_id: int,
        payload: Mapping[str, Any],
    ) -> Any:
        _require_consultation_writes_enabled()
        endpoints = self._settings.endpoints_for("consultas")
        path = _format_consultation_path(
            endpoints.update_path,
            consultation_id,
            endpoints.identifier_parameter,
        )
        clean_payload = _validate_consultation_payload(payload)
        response = self._send("consultas", "PATCH", path, clean_payload)
        return _parse_json(response)

    def delete_consultation(self, consultation_id: int) -> None:
        _require_consultation_writes_enabled()
        endpoints = self._settings.endpoints_for("consultas")
        path = _format_consultation_path(
            endpoints.delete_path,
            consultation_id,
            endpoints.identifier_parameter,
        )
        self._send("consultas", "DELETE", path)

    def _send(
        self,
        resource: XanoResourceName,
        method: str,
        path: str | None,
        payload: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        base_url_env = {
            "pacientes": XANO_PACIENTES_BASE_URL_ENV,
            "profissionais": XANO_PROFISSIONAIS_BASE_URL_ENV,
            "especialidades": XANO_ESPECIALIDADES_BASE_URL_ENV,
            "consultas": XANO_CONSULTAS_BASE_URL_ENV,
            "status_consulta": XANO_STATUS_CONSULTA_BASE_URL_ENV,
            "profissional_especialidade": (
                XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL_ENV
            ),
        }[resource]
        url = _build_url(
            self._settings.base_url_for(resource), path, base_url_env
        )
        headers = (
            {"Authorization": self._settings.authorization}
            if self._settings.authorization
            else None
        )
        if headers and any(
            character in headers["Authorization"] for character in "\r\n"
        ):
            raise XanoConfigurationError(
                "A configuração de autorização contém caracteres inválidos."
            )
        try:
            response = self._transport.request(
                method,
                url,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.Timeout as error:
            raise XanoTimeoutError("A requisição ao Xano excedeu o tempo limite.") from error
        except requests.ConnectionError as error:
            raise XanoConnectionError("Não foi possível conectar ao Xano.") from error
        except requests.RequestException as error:
            raise XanoTransportError("Falha ao consultar o Xano.") from error

        if not 200 <= response.status_code < 300:
            raise XanoHTTPError(response.status_code)
        return response


def _endpoints_from_environment(
    prefix: str,
    defaults: ResourceEndpoints = ResourceEndpoints(),
) -> ResourceEndpoints:
    return ResourceEndpoints(
        collection_path=os.getenv(f"XANO_{prefix}_COLLECTION_PATH")
        or defaults.collection_path,
        item_path=os.getenv(f"XANO_{prefix}_ITEM_PATH") or defaults.item_path,
        create_path=os.getenv(f"XANO_{prefix}_CREATE_PATH")
        or defaults.create_path,
        update_path=os.getenv(f"XANO_{prefix}_UPDATE_PATH")
        or defaults.update_path,
        delete_path=os.getenv(f"XANO_{prefix}_DELETE_PATH")
        or defaults.delete_path,
        identifier_parameter=defaults.identifier_parameter,
    )


def _build_url(
    base_url: str | None,
    path: str | None,
    base_url_env: str,
) -> str:
    if not base_url or not base_url.strip():
        raise XanoConfigurationError(
            f"A configuração {base_url_env} não foi definida."
        )
    if not path or not path.strip():
        raise XanoConfigurationError("O caminho desta operação Xano não foi configurado.")

    base = urlsplit(base_url.strip())
    if (
        base.scheme != "https"
        or not base.netloc
        or base.username is not None
        or base.password is not None
        or base.query
        or base.fragment
    ):
        raise XanoConfigurationError("A URL base do Xano é inválida.")

    endpoint = urlsplit(path.strip())
    if endpoint.scheme or endpoint.netloc or endpoint.fragment:
        raise XanoConfigurationError("O caminho Xano deve ser relativo à URL base.")

    return urljoin(base_url.rstrip("/") + "/", path.strip().lstrip("/"))


def _format_item_path(
    path_template: str | None,
    record_id: int,
    identifier_parameter: str,
) -> str:
    if isinstance(record_id, bool) or not isinstance(record_id, int) or record_id < 1:
        raise ValueError("O identificador do registro deve ser um inteiro positivo.")
    marker = "{" + identifier_parameter + "}"
    if not path_template or marker not in path_template:
        raise XanoConfigurationError(
            f"O caminho do recurso deve conter o marcador {marker}."
        )
    formatted_path = path_template.replace(marker, str(record_id))
    if "{" in formatted_path or "}" in formatted_path:
        raise XanoConfigurationError("O caminho do recurso contém marcadores inválidos.")
    return formatted_path


def _validate_payload(
    resource: ResourceName,
    payload: Mapping[str, Any],
    *,
    require_name: bool,
    trim_text: bool = False,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise XanoResponseError("Os dados enviados precisam ser um objeto.")
    allowed_fields = RESOURCE_PAYLOAD_FIELDS[resource]
    unknown_fields = set(payload).difference(allowed_fields)
    if unknown_fields:
        raise XanoResponseError("Os dados enviados contêm campos não permitidos.")
    if require_name and not str(payload.get("nome", "")).strip():
        raise XanoResponseError("O campo nome é obrigatório.")

    clean_payload = {
        field: value.strip() if trim_text and isinstance(value, str) else value
        for field, value in payload.items()
    }
    for field, value in clean_payload.items():
        if field == "nome" and (not isinstance(value, str) or not value.strip()):
            raise XanoResponseError("O campo nome deve conter texto não vazio.")
        if field in OPTIONAL_RESOURCE_FIELDS and value is not None and not isinstance(value, str):
            raise XanoResponseError(f"O campo {field} deve ser texto ou nulo.")
    return clean_payload


def _validate_specialty_payload(
    payload: Mapping[str, Any],
) -> dict[str, str]:
    if not isinstance(payload, Mapping):
        raise XanoResponseError("Os dados enviados precisam ser um objeto.")
    if set(payload).difference({"nome"}):
        raise XanoResponseError("Os dados enviados contêm campos não permitidos.")

    if "nome" not in payload:
        raise XanoResponseError("O campo nome é obrigatório.")

    name = payload["nome"]
    if not isinstance(name, str) or not name.strip():
        raise XanoResponseError("O campo nome deve conter texto não vazio.")
    return {"nome": name.strip()}


def _validate_specialty_record(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise XanoResponseError("O registro retornado pelo Xano não é um objeto.")

    record_id = value.get("id")
    name = value.get("nome")
    if isinstance(record_id, bool) or not isinstance(record_id, int) or record_id < 1:
        raise XanoResponseError("O identificador da especialidade é inválido.")
    if not isinstance(name, str) or not name.strip():
        raise XanoResponseError("O nome da especialidade retornado pelo Xano é inválido.")

    return {"id": record_id, "nome": name}


def _require_specialties_api_enabled() -> None:
    if not specialties_api_enabled():
        raise XanoConfigurationError(
            "A API de Especialidades está desabilitada pela configuração "
            "XANO_ESPECIALIDADES_API_ENABLED."
        )


def _require_resource_writes_enabled(resource: ResourceName) -> None:
    if resource == "pacientes":
        enabled = patients_write_enabled()
        environment_name = XANO_PACIENTES_WRITE_ENABLED_ENV
    else:
        enabled = professionals_write_enabled()
        environment_name = XANO_PROFISSIONAIS_WRITE_ENABLED_ENV
    if not enabled:
        raise XanoConfigurationError(
            f"As gravações remotas de {resource} estão desabilitadas pela "
            f"configuração {environment_name}."
        )


def _require_specialty_writes_enabled() -> None:
    if not specialties_write_enabled():
        raise XanoConfigurationError(
            "As gravações de Especialidades estão desabilitadas pela configuração "
            "XANO_ESPECIALIDADES_WRITE_ENABLED."
        )


def _validate_consultation_payload(
    payload: Mapping[str, Any],
    *,
    require_complete: bool = False,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise XanoResponseError("Os dados enviados precisam ser um objeto.")
    if set(payload).difference(CONSULTATION_PAYLOAD_FIELDS):
        raise XanoResponseError(
            "Os dados enviados contêm campos não permitidos."
        )
    if require_complete:
        missing_fields = set(CONSULTATION_REQUIRED_FIELDS).difference(payload)
        if missing_fields:
            raise XanoResponseError(
                "Os dados enviados não contêm todos os campos obrigatórios."
            )
    elif not payload:
        raise XanoResponseError(
            "Informe ao menos um campo para atualizar a consulta."
        )

    for field, value in payload.items():
        if field in CONSULTATION_INTEGER_FIELDS and (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise XanoResponseError(
                f"O campo {field} deve ser um inteiro positivo."
            )
        if field == "data_e_hora_do_agendamento" and (
            isinstance(value, bool) or not isinstance(value, int)
        ):
            raise XanoResponseError(
                "O campo data_e_hora_do_agendamento deve ser um timestamp "
                "Unix em milissegundos."
            )
        if field == "observacoes" and value is not None and not isinstance(
            value, str
        ):
            raise XanoResponseError(
                "O campo observacoes deve ser texto ou nulo."
            )

    return dict(payload)


def _validate_consultation_record(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise XanoResponseError(
            "O registro de Consulta retornado pelo Xano não é um objeto."
        )
    required_fields = {"id", *CONSULTATION_REQUIRED_FIELDS}
    if required_fields.difference(value):
        raise XanoResponseError(
            "O registro de Consulta não contém os campos esperados."
        )

    record_id = value["id"]
    if isinstance(record_id, bool) or not isinstance(record_id, int):
        raise XanoResponseError("O identificador da Consulta é inválido.")
    for field in CONSULTATION_INTEGER_FIELDS:
        field_value = value[field]
        if isinstance(field_value, bool) or not isinstance(field_value, int):
            raise XanoResponseError(
                f"O campo {field} retornado pela Consulta é inválido."
            )
    timestamp = value["data_e_hora_do_agendamento"]
    if isinstance(timestamp, bool) or not isinstance(timestamp, int):
        raise XanoResponseError(
            "O timestamp da Consulta retornado pelo Xano é inválido."
        )
    try:
        consultation_timestamp_to_local_datetime(timestamp)
    except ValueError as error:
        raise XanoResponseError(
            "O timestamp da Consulta está fora do intervalo renderizável."
        ) from error
    if "observacoes" in value and value["observacoes"] is not None and not isinstance(
        value["observacoes"], str
    ):
        raise XanoResponseError(
            "O campo observacoes retornado pela Consulta é inválido."
        )

    record = {
        field: value[field]
        for field in ("id", *CONSULTATION_REQUIRED_FIELDS)
    }
    if "observacoes" in value:
        record["observacoes"] = value["observacoes"]
    return record


def consultation_datetime_to_unix_ms(
    appointment_date: date,
    appointment_time: time,
) -> int:
    if isinstance(appointment_date, datetime) or not isinstance(
        appointment_date, date
    ):
        raise ValueError("A data da Consulta é inválida.")
    if not isinstance(appointment_time, time) or appointment_time.tzinfo is not None:
        raise ValueError("O horário da Consulta deve ser um horário local sem fuso.")

    local_datetime = datetime.combine(
        appointment_date,
        appointment_time,
    ).replace(tzinfo=CONSULTATION_TIMEZONE)
    delta = local_datetime.astimezone(timezone.utc) - UNIX_EPOCH
    return (
        delta.days * 86_400_000
        + delta.seconds * 1_000
        + delta.microseconds // 1_000
    )


def consultation_timestamp_to_local_datetime(timestamp_ms: int) -> datetime:
    if isinstance(timestamp_ms, bool) or not isinstance(timestamp_ms, int):
        raise ValueError("O timestamp da Consulta deve ser inteiro em milissegundos.")
    try:
        utc_datetime = UNIX_EPOCH + timedelta(milliseconds=timestamp_ms)
    except OverflowError as error:
        raise ValueError("O timestamp da Consulta está fora do intervalo válido.") from error
    return utc_datetime.astimezone(CONSULTATION_TIMEZONE)


def _validate_consultation_status(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise XanoResponseError(
            "O registro de Status da Consulta não é um objeto."
        )

    record_id = value.get("id")
    name = value.get("nome")
    created_at = value.get("created_at")
    if isinstance(record_id, bool) or not isinstance(record_id, int):
        raise XanoResponseError(
            "O identificador do Status da Consulta é inválido."
        )
    if not isinstance(name, str):
        raise XanoResponseError(
            "O nome do Status da Consulta é inválido."
        )
    if isinstance(created_at, bool) or not isinstance(created_at, int):
        raise XanoResponseError(
            "A data de criação do Status da Consulta é inválida."
        )
    return {"id": record_id, "nome": name, "created_at": created_at}


def _validate_professional_specialty(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        raise XanoResponseError(
            "O vínculo Profissional–Especialidade retornado pelo Xano "
            "não é um objeto."
        )
    association_id = value.get("id")
    professional_id = value.get("profissional_id")
    specialty_id = value.get("especialidade_id")
    for field, field_value in (
        ("id", association_id),
        ("profissional_id", professional_id),
        ("especialidade_id", specialty_id),
    ):
        if (
            isinstance(field_value, bool)
            or not isinstance(field_value, int)
            or field_value < 1
        ):
            raise XanoResponseError(
                f"O campo {field} do vínculo Profissional–Especialidade "
                "é inválido."
            )
    return {
        "id": association_id,
        "profissional_id": professional_id,
        "especialidade_id": specialty_id,
    }


def _format_consultation_path(
    path_template: str | None,
    consultation_id: int,
    identifier_parameter: str,
) -> str:
    if isinstance(consultation_id, bool) or not isinstance(
        consultation_id, int
    ):
        raise ValueError("O identificador da consulta deve ser um inteiro.")
    marker = "{" + identifier_parameter + "}"
    if not path_template or marker not in path_template:
        raise XanoConfigurationError(
            f"O caminho da consulta deve conter o marcador {marker}."
        )
    formatted_path = path_template.replace(marker, str(consultation_id))
    if "{" in formatted_path or "}" in formatted_path:
        raise XanoConfigurationError(
            "O caminho da consulta contém marcadores inválidos."
        )
    return formatted_path


def consultations_api_enabled() -> bool:
    return (
        os.getenv(XANO_CONSULTAS_API_ENABLED_ENV, "").strip().lower()
        == "true"
    )


def consultation_status_api_enabled() -> bool:
    return (
        os.getenv(XANO_STATUS_CONSULTA_API_ENABLED_ENV, "")
        .strip()
        .lower()
        == "true"
    )


def professional_specialties_api_enabled() -> bool:
    return (
        os.getenv(
            XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV, ""
        ).strip().lower()
        == "true"
    )


def consultations_write_enabled() -> bool:
    return (
        os.getenv(XANO_CONSULTAS_WRITE_ENABLED_ENV, "")
        .strip()
        .lower()
        == "true"
    )


def _require_consultations_api_enabled() -> None:
    if not consultations_api_enabled():
        raise XanoConfigurationError(
            "A API de Consultas está desabilitada pela configuração "
            f"{XANO_CONSULTAS_API_ENABLED_ENV}."
        )


def _require_status_consulta_api_enabled() -> None:
    if not consultation_status_api_enabled():
        raise XanoConfigurationError(
            "A API de Status da Consulta está desabilitada pela configuração "
            f"{XANO_STATUS_CONSULTA_API_ENABLED_ENV}."
        )


def _require_professional_specialties_api_enabled() -> None:
    if not professional_specialties_api_enabled():
        raise XanoConfigurationError(
            "A API de vínculos Profissional–Especialidade está desabilitada "
            "pela configuração "
            f"{XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV}."
        )


def _require_consultation_writes_enabled() -> None:
    _require_consultations_api_enabled()
    if not consultations_write_enabled():
        raise XanoConfigurationError(
            "As gravações de Consultas estão desabilitadas pela configuração "
            f"{XANO_CONSULTAS_WRITE_ENABLED_ENV}."
        )


def _parse_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError as error:
        raise XanoResponseError("O Xano retornou um JSON inválido.") from error


def _validate_record(resource: ResourceName, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise XanoResponseError("O registro retornado pelo Xano não é um objeto.")

    fields = RESOURCE_FIELDS[resource]
    if any(field not in value for field in fields):
        raise XanoResponseError("O registro retornado não contém os campos esperados.")

    record_id = value["id"]
    if isinstance(record_id, bool) or not isinstance(record_id, int) or record_id < 1:
        raise XanoResponseError("O identificador retornado pelo Xano é inválido.")
    if not isinstance(value["nome"], str):
        raise XanoResponseError("O nome retornado pelo Xano é inválido.")
    for field in OPTIONAL_RESOURCE_FIELDS.intersection(fields):
        if value[field] is not None and not isinstance(value[field], str):
            raise XanoResponseError(f"O campo {field} retornado pelo Xano é inválido.")

    return {field: value[field] for field in fields}
