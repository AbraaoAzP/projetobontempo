from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal, Mapping, Protocol
from urllib.parse import urljoin, urlsplit

import requests


XANO_PACIENTES_BASE_URL_ENV = "XANO_PACIENTES_BASE_URL"
XANO_PROFISSIONAIS_BASE_URL_ENV = "XANO_PROFISSIONAIS_BASE_URL"
XANO_ESPECIALIDADES_BASE_URL_ENV = "XANO_ESPECIALIDADES_BASE_URL"
XANO_AUTHORIZATION_ENV = "XANO_AUTHORIZATION"
XANO_API_ENABLED_ENV = "XANO_API_ENABLED"
XANO_ESPECIALIDADES_API_ENABLED_ENV = "XANO_ESPECIALIDADES_API_ENABLED"
XANO_ESPECIALIDADES_WRITE_ENABLED_ENV = "XANO_ESPECIALIDADES_WRITE_ENABLED"
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
XanoResourceName = Literal["pacientes", "profissionais", "especialidades"]

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
            authorization=os.getenv(XANO_AUTHORIZATION_ENV),
        )

    def endpoints_for(self, resource: XanoResourceName) -> ResourceEndpoints:
        if resource == "pacientes":
            return self.patients
        if resource == "profissionais":
            return self.professionals
        if resource == "especialidades":
            return self.specialties
        raise ValueError(f"Recurso Xano não suportado: {resource}")

    def base_url_for(self, resource: XanoResourceName) -> str | None:
        if resource == "pacientes":
            return self.patients_base_url
        if resource == "profissionais":
            return self.professionals_base_url
        if resource == "especialidades":
            return self.specialties_base_url
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
        endpoints = self._settings.endpoints_for(resource)
        path = _format_item_path(
            endpoints.update_path, record_id, endpoints.identifier_parameter
        )
        clean_payload = _validate_payload(resource, payload, require_name=False)
        response = self._send(resource, "PATCH", path, clean_payload)
        return _validate_record(resource, _parse_json(response))

    def delete_record(self, resource: ResourceName, record_id: int) -> None:
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

    def list_specialties(self) -> requests.Response:
        endpoints = self._settings.endpoints_for("especialidades")
        return self._send(
            "especialidades", "GET", endpoints.collection_path
        )

    def get_specialty(self, specialty_id: int) -> requests.Response:
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.item_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        return self._send("especialidades", "GET", path)

    def create_specialty(
        self, payload: Mapping[str, Any]
    ) -> requests.Response:
        endpoints = self._settings.endpoints_for("especialidades")
        clean_payload = _validate_specialty_payload(payload, require_name=True)
        _require_specialty_writes_enabled()
        return self._send(
            "especialidades", "POST", endpoints.create_path, clean_payload
        )

    def update_specialty(
        self, specialty_id: int, payload: Mapping[str, Any]
    ) -> requests.Response:
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.update_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        clean_payload = _validate_specialty_payload(
            payload, require_name=False
        )
        _require_specialty_writes_enabled()
        return self._send(
            "especialidades", "PATCH", path, clean_payload
        )

    def delete_specialty(self, specialty_id: int) -> requests.Response:
        _require_specialty_writes_enabled()
        endpoints = self._settings.endpoints_for("especialidades")
        path = _format_item_path(
            endpoints.delete_path,
            specialty_id,
            endpoints.identifier_parameter,
        )
        return self._send("especialidades", "DELETE", path)

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
    *,
    require_name: bool,
) -> dict[str, str]:
    if not isinstance(payload, Mapping):
        raise XanoResponseError("Os dados enviados precisam ser um objeto.")
    if set(payload).difference({"nome"}):
        raise XanoResponseError("Os dados enviados contêm campos não permitidos.")

    if require_name and "nome" not in payload:
        raise XanoResponseError("O campo nome é obrigatório.")
    if "nome" not in payload:
        return {}

    name = payload["nome"]
    if not isinstance(name, str) or not name.strip():
        raise XanoResponseError("O campo nome deve conter texto não vazio.")
    return {"nome": name.strip()}


def _require_specialty_writes_enabled() -> None:
    if not specialties_write_enabled():
        raise XanoConfigurationError(
            "As gravações de Especialidades estão desabilitadas até a "
            "confirmação dos controles de autorização."
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
