import os
import unittest
from datetime import date, datetime, time
from unittest.mock import Mock, call, patch
from zoneinfo import ZoneInfo

import requests

from services.xano import (
    DEFAULT_ESPECIALIDADES_BASE_URL,
    DEFAULT_PACIENTES_BASE_URL,
    DEFAULT_PROFISSIONAIS_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    XANO_API_ENABLED_ENV,
    XANO_CONSULTAS_API_ENABLED_ENV,
    XANO_CONSULTAS_BASE_URL_ENV,
    XANO_CONSULTAS_WRITE_ENABLED_ENV,
    XANO_ESPECIALIDADES_API_ENABLED_ENV,
    XANO_ESPECIALIDADES_BASE_URL_ENV,
    XANO_ESPECIALIDADES_WRITE_ENABLED_ENV,
    XANO_PACIENTES_BASE_URL_ENV,
    XANO_PROFISSIONAIS_BASE_URL_ENV,
    XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV,
    XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL_ENV,
    XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED_ENV,
    XANO_STATUS_CONSULTA_API_ENABLED_ENV,
    XANO_STATUS_CONSULTA_BASE_URL_ENV,
    XANO_PRONTUARIOS_API_ENABLED_ENV,
    XANO_PRONTUARIOS_BASE_URL_ENV,
    XANO_PRONTUARIOS_WRITE_ENABLED_ENV,
    ResourceEndpoints,
    XanoClient,
    XanoConfigurationError,
    XanoConnectionError,
    XanoHTTPError,
    XanoResponseError,
    XanoSettings,
    XanoTimeoutError,
    XanoTransportError,
    api_enabled,
    consultation_status_api_enabled,
    consultation_datetime_to_unix_ms,
    consultation_timestamp_to_local_datetime,
    consultations_api_enabled,
    consultations_write_enabled,
    professional_specialties_api_enabled,
    professional_specialties_write_enabled,
    prontuarios_api_enabled,
    prontuarios_write_enabled,
    specialties_api_enabled,
    specialties_write_enabled,
)


class TestXanoClient(unittest.TestCase):
    def setUp(self) -> None:
        self._write_environment = patch.dict(
            os.environ,
            {
                "XANO_PACIENTES_WRITE_ENABLED": "true",
                "XANO_PROFISSIONAIS_WRITE_ENABLED": "true",
            },
        )
        self._write_environment.start()
        self.addCleanup(self._write_environment.stop)
        self.transport = Mock()
        self.settings = XanoSettings(
            patients_base_url="https://patients.example.invalid/api:patients",
            professionals_base_url=(
                "https://professionals.example.invalid/api:professionals"
            ),
            patients=ResourceEndpoints(
                collection_path="pacientes",
                item_path="paciente/{paciente_id}",
                create_path="pacientes",
                update_path="paciente/{paciente_id}",
                delete_path="paciente/{paciente_id}",
                identifier_parameter="paciente_id",
            ),
            professionals=ResourceEndpoints(
                collection_path="profissionais",
                item_path="profissional/{profissional_id}",
                create_path="profissionais",
                update_path="profissional/{profissional_id}",
                delete_path="profissional/{profissional_id}",
                identifier_parameter="profissional_id",
            ),
            specialties=ResourceEndpoints(
                collection_path="especialidade",
                item_path="especialidade/{especialidade_id}",
                create_path="especialidade",
                update_path="especialidade/{especialidade_id}",
                delete_path="especialidade/{especialidade_id}",
                identifier_parameter="especialidade_id",
            ),
            consultations_base_url=(
                "https://consultations.example.invalid/api:consultations"
            ),
            statuses_base_url=(
                "https://statuses.example.invalid/api:statuses"
            ),
            professional_specialties_base_url=(
                "https://associations.example.invalid/api:associations"
            ),
            professional_specialties=ResourceEndpoints(
                collection_path="profissional_especialidade",
                item_path="profissional_especialidade/{profissional_especialidade_id}",
                create_path="profissional_especialidade",
                update_path=None,
                delete_path="profissional_especialidade/{profissional_especialidade_id}",
                identifier_parameter="profissional_especialidade_id",
            ),
            prontuarios_base_url=(
                "https://prontuarios.example.invalid/api:prontuarios"
            ),
            prontuarios=ResourceEndpoints(
                collection_path="prontuario",
                item_path="prontuario/{prontuario_id}",
                create_path="prontuario",
                update_path="prontuario/{prontuario_id}",
                delete_path="prontuario/{prontuario_id}",
                identifier_parameter="prontuario_id",
            ),
        )
        self.client = XanoClient(self.settings, self.transport)
        self.patient = {
            "id": 11,
            "nome": "Paciente sintético",
            "telefone": "11999999999",
            "email": "patient@example.invalid",
            "extra": "não expor",
        }
        self.professional = {
            "id": 21,
            "nome": "Profissional sintético",
            "telefone": "11888888888",
            "email": None,
            "especialidade": "Especialidade textual",
        }
        self.consultation = {
            "id": 52,
            "paciente_id": 11,
            "profissional_id": 21,
            "especialidade_id": 31,
            "data_e_hora_do_agendamento": 1768480200000,
            "status_consulta_id": 41,
            "observacoes": None,
        }

    def _response(self, data: object, status_code: int = 200) -> Mock:
        response = Mock()
        response.status_code = status_code
        response.json.return_value = data
        return response

    def test_reads_collection_and_individual_records_with_resource_ids(self) -> None:
        self.transport.request.side_effect = [
            self._response([self.patient]),
            self._response(self.patient),
            self._response([self.professional]),
            self._response(self.professional),
        ]

        patient_list = self.client.list_records("pacientes")
        patient = self.client.get_record("pacientes", 11)
        professional_list = self.client.list_records("profissionais")
        professional = self.client.get_record("profissionais", 21)

        self.assertEqual(patient_list, [{key: value for key, value in self.patient.items() if key != "extra"}])
        self.assertEqual(patient, patient_list[0])
        self.assertEqual(professional_list, [self.professional])
        self.assertEqual(professional, self.professional)
        urls = [call.args[1] for call in self.transport.request.call_args_list]
        self.assertEqual(
            urls,
            [
                "https://patients.example.invalid/api:patients/pacientes",
                "https://patients.example.invalid/api:patients/paciente/11",
                "https://professionals.example.invalid/api:professionals/profissionais",
                "https://professionals.example.invalid/api:professionals/profissional/21",
            ],
        )
        self.assertTrue(
            all(
                call.kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS
                for call in self.transport.request.call_args_list
            )
        )

    def test_creates_and_updates_both_resources_with_trimmed_text_fields(self) -> None:
        self.transport.request.side_effect = [
            self._response(self.patient),
            self._response(self.professional),
            self._response(self.patient),
            self._response(self.professional),
        ]

        self.client.create_record(
            "pacientes",
            {
                "nome": " Paciente sintético ",
                "telefone": " 11999999999 ",
                "email": " patient@example.invalid ",
            },
        )
        self.client.create_record(
            "profissionais",
            {
                "nome": " Profissional sintético ",
                "telefone": " 11888888888 ",
                "email": "",
                "especialidade": " Clínica ",
            },
        )
        self.client.update_record("pacientes", 11, {"email": None})
        self.client.update_record(
            "profissionais",
            21,
            {"especialidade": "Clínica geral"},
        )

        calls = self.transport.request.call_args_list
        self.assertEqual(
            [call.args[0] for call in calls],
            ["POST", "POST", "PATCH", "PATCH"],
        )
        self.assertEqual(
            calls[0].kwargs["json"],
            {
                "nome": "Paciente sintético",
                "telefone": "11999999999",
                "email": "patient@example.invalid",
            },
        )
        self.assertEqual(
            calls[1].kwargs["json"],
            {
                "nome": "Profissional sintético",
                "telefone": "11888888888",
                "email": "",
                "especialidade": "Clínica",
            },
        )
        self.assertEqual(calls[2].kwargs["json"], {"email": None})
        self.assertEqual(
            calls[3].kwargs["json"], {"especialidade": "Clínica geral"}
        )

    def test_delete_requires_confirmed_success_response(self) -> None:
        self.transport.request.return_value = self._response({"success": True})

        self.client.delete_record("pacientes", 11)
        self.client.delete_record("profissionais", 21)

        self.assertEqual(
            [call.args[1] for call in self.transport.request.call_args_list],
            [
                "https://patients.example.invalid/api:patients/paciente/11",
                "https://professionals.example.invalid/api:professionals/profissional/21",
            ],
        )
        for invalid_response in ({}, {"success": False}, {"success": "true"}, []):
            with self.subTest(invalid_response=invalid_response):
                self.transport.request.return_value = self._response(invalid_response)
                with self.assertRaises(XanoResponseError):
                    self.client.delete_record("pacientes", 11)

    def test_http_errors_preserve_status_without_exposing_response_body(self) -> None:
        for status_code in (400, 401, 403, 404, 409, 429, 500):
            with self.subTest(status_code=status_code):
                self.transport.request.return_value = self._response(
                    {"private": "do not expose"}, status_code
                )
                with self.assertRaises(XanoHTTPError) as raised:
                    self.client.list_records("pacientes")
                self.assertEqual(raised.exception.status_code, status_code)
                self.assertNotIn("private", str(raised.exception))

    def test_rate_limit_is_not_retried_automatically(self) -> None:
        self.transport.request.return_value = self._response(
            {"error": "rate limited"}, 429
        )

        with self.assertRaises(XanoHTTPError) as raised:
            self.client.create_record(
                "profissionais", {"nome": "Profissional sintético"}
            )

        self.transport.request.assert_called_once()
        self.assertIn("HTTP 429", str(raised.exception))
        self.assertIn("consulte a listagem", str(raised.exception))
        self.assertNotIn("rate limited", str(raised.exception))

    def test_transport_failures_are_explicit(self) -> None:
        cases = (
            (requests.Timeout, XanoTimeoutError),
            (requests.ConnectionError, XanoConnectionError),
            (requests.RequestException, XanoTransportError),
        )
        for error_type, expected in cases:
            with self.subTest(error_type=error_type):
                self.transport.request.side_effect = error_type("synthetic")
                with self.assertRaises(expected):
                    self.client.list_records("pacientes")

    def test_invalid_json_shapes_fields_and_ids_are_rejected(self) -> None:
        invalid_json = self._response(None)
        invalid_json.json.side_effect = ValueError("invalid")
        self.transport.request.return_value = invalid_json
        with self.assertRaises(XanoResponseError):
            self.client.list_records("pacientes")

        for invalid in (
            {"id": 1},
            [{"id": 1}],
            [{**self.patient, "id": True}],
            [{**self.patient, "email": 12}],
        ):
            with self.subTest(invalid=invalid):
                self.transport.request.return_value = self._response(invalid)
                with self.assertRaises(XanoResponseError):
                    self.client.list_records("pacientes")

        with self.assertRaises(ValueError):
            self.client.get_record("pacientes", True)
        with self.assertRaises(ValueError):
            self.client.delete_record("pacientes", 0)

    def test_invalid_payloads_do_not_send_request(self) -> None:
        with self.assertRaises(XanoResponseError):
            self.client.create_record("pacientes", {"nome": " "})
        with self.assertRaises(XanoResponseError):
            self.client.create_record("pacientes", {"nome": "Nome", "id": 99})
        self.transport.request.assert_not_called()

    def test_default_routes_and_base_urls_match_confirmed_contract(self) -> None:
        settings = XanoSettings.from_environment()
        self.assertEqual(settings.patients_base_url, DEFAULT_PACIENTES_BASE_URL)
        self.assertEqual(
            settings.professionals_base_url, DEFAULT_PROFISSIONAIS_BASE_URL
        )
        self.assertEqual(settings.patients.item_path, "paciente/{paciente_id}")
        self.assertEqual(
            settings.professionals.item_path,
            "profissional/{profissional_id}",
        )
        self.transport.request.return_value = self._response({"success": True})
        XanoClient(settings, self.transport).delete_record("profissionais", 21)
        self.assertEqual(
            self.transport.request.call_args.args[1],
            f"{DEFAULT_PROFISSIONAIS_BASE_URL}/profissional/21",
        )

    def test_urls_can_be_overridden_externally_and_missing_values_fail_closed(self) -> None:
        with patch.dict(
            os.environ,
            {
                XANO_PACIENTES_BASE_URL_ENV: "",
                XANO_PROFISSIONAIS_BASE_URL_ENV: (
                    "https://custom.example.invalid/api:custom"
                ),
            },
            clear=True,
        ):
            settings = XanoSettings.from_environment()
            client = XanoClient(settings, self.transport)
            with self.assertRaises(XanoConfigurationError):
                client.list_records("pacientes")
            self.transport.request.return_value = self._response([])
            self.assertEqual(client.list_records("profissionais"), [])

        self.assertEqual(
            self.transport.request.call_args.args[1],
            "https://custom.example.invalid/api:custom/profissionais",
        )
        self.assertEqual(settings.patients_base_url, "")

    def test_specialty_crud_uses_confirmed_routes_and_validates_records(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = XanoSettings.from_environment()

        self.assertEqual(
            settings.specialties_base_url, DEFAULT_ESPECIALIDADES_BASE_URL
        )
        self.assertEqual(settings.specialties.collection_path, "especialidade")
        self.assertEqual(
            settings.specialties.item_path,
            "especialidade/{especialidade_id}",
        )

        specialty = {"id": 7, "created_at": 1762700000, "nome": "Fictícia"}
        list_response = self._response([specialty])
        item_response = self._response(specialty)
        create_response = self._response({"id": 8, "nome": "Nova"})
        update_response = self._response({"id": 7, "nome": "Outra fictícia"})
        delete_response = Mock(status_code=204)
        self.transport.request.side_effect = [
            list_response,
            item_response,
            create_response,
            update_response,
            delete_response,
        ]
        client = XanoClient(settings, self.transport)

        with patch.dict(
            os.environ,
            {XANO_ESPECIALIDADES_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            self.assertEqual(
                client.list_specialties(),
                [{"id": 7, "nome": "Fictícia"}],
            )
            self.assertEqual(
                client.get_specialty(7),
                {"id": 7, "nome": "Fictícia"},
            )
        with patch.dict(
            os.environ,
            {XANO_ESPECIALIDADES_WRITE_ENABLED_ENV: "true"},
            clear=True,
        ):
            self.assertEqual(
                client.create_specialty({"nome": "  Fictícia  "}),
                {"id": 8, "nome": "Nova"},
            )
            self.assertEqual(
                client.update_specialty(7, {"nome": "Outra fictícia"}),
                {"id": 7, "nome": "Outra fictícia"},
            )
            self.assertIsNone(client.delete_specialty(7))

        calls = self.transport.request.call_args_list
        self.assertEqual(
            [call.args[0] for call in calls],
            ["GET", "GET", "POST", "PATCH", "DELETE"],
        )
        self.assertEqual(
            [call.args[1] for call in calls],
            [
                f"{DEFAULT_ESPECIALIDADES_BASE_URL}/especialidade",
                f"{DEFAULT_ESPECIALIDADES_BASE_URL}/especialidade/7",
                f"{DEFAULT_ESPECIALIDADES_BASE_URL}/especialidade",
                f"{DEFAULT_ESPECIALIDADES_BASE_URL}/especialidade/7",
                f"{DEFAULT_ESPECIALIDADES_BASE_URL}/especialidade/7",
            ],
        )
        self.assertEqual(calls[2].kwargs["json"], {"nome": "Fictícia"})
        self.assertEqual(calls[3].kwargs["json"], {"nome": "Outra fictícia"})
        self.assertTrue(
            all(
                call.kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS
                for call in calls
            )
        )

    def test_specialty_payload_validation_blocks_invalid_requests(self) -> None:
        with self.assertRaises(XanoResponseError):
            self.client.create_specialty({"nome": "  "})
        with self.assertRaises(XanoResponseError):
            self.client.create_specialty({"nome": "Fictícia", "id": 7})
        with self.assertRaises(XanoResponseError):
            self.client.update_specialty(7, {"nome": 123})
        with self.assertRaises(XanoResponseError):
            self.client.update_specialty(7, {})
        self.transport.request.assert_not_called()

    def test_specialty_read_and_write_require_explicit_enablement(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(specialties_api_enabled())
            self.assertFalse(specialties_write_enabled())

        with patch.dict(
            os.environ,
            {
                XANO_ESPECIALIDADES_API_ENABLED_ENV: "false",
                XANO_ESPECIALIDADES_WRITE_ENABLED_ENV: "false",
            },
            clear=True,
        ):
            self.assertFalse(specialties_api_enabled())
            self.assertFalse(specialties_write_enabled())
            with self.assertRaises(XanoConfigurationError):
                self.client.create_specialty({"nome": "Fictícia"})
            with self.assertRaises(XanoConfigurationError):
                self.client.update_specialty(7, {"nome": "Fictícia"})
            with self.assertRaises(XanoConfigurationError):
                self.client.delete_specialty(7)
        self.transport.request.assert_not_called()

    def test_specialty_api_has_an_independent_read_gate(self) -> None:
        with patch.dict(
            os.environ,
            {
                XANO_API_ENABLED_ENV: "true",
                XANO_ESPECIALIDADES_API_ENABLED_ENV: "false",
            },
            clear=True,
        ):
            self.assertFalse(specialties_api_enabled())

        with patch.dict(
            os.environ,
            {XANO_ESPECIALIDADES_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            self.assertTrue(specialties_api_enabled())

    def test_specialty_base_url_can_be_overridden_and_empty_fails_closed(self) -> None:
        custom_url = "https://specialties.example.invalid/api:custom"
        with patch.dict(
            os.environ,
            {
                XANO_ESPECIALIDADES_API_ENABLED_ENV: "true",
                XANO_ESPECIALIDADES_BASE_URL_ENV: custom_url,
            },
            clear=True,
        ):
            settings = XanoSettings.from_environment()
            client = XanoClient(settings, self.transport)
            self.transport.request.return_value = self._response([])

            specialties = client.list_specialties()

        self.assertEqual(specialties, [])
        self.assertEqual(
            self.transport.request.call_args.args[1],
            f"{custom_url}/especialidade",
        )

        with patch.dict(
            os.environ, {XANO_ESPECIALIDADES_BASE_URL_ENV: ""}, clear=True
        ):
            client = XanoClient(XanoSettings.from_environment(), self.transport)
            with self.assertRaises(XanoConfigurationError):
                client.list_specialties()

        self.transport.request.assert_called_once()

    def test_api_is_disabled_unless_explicitly_enabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(api_enabled())
        with patch.dict(os.environ, {XANO_API_ENABLED_ENV: "false"}, clear=True):
            self.assertFalse(api_enabled())
        with patch.dict(os.environ, {XANO_API_ENABLED_ENV: "true"}, clear=True):
            self.assertTrue(api_enabled())

    def test_resource_writes_are_disabled_by_default(self) -> None:
        with patch.dict(
            os.environ,
            {
                "XANO_PACIENTES_WRITE_ENABLED": "false",
                "XANO_PROFISSIONAIS_WRITE_ENABLED": "false",
            },
            clear=True,
        ):
            with self.assertRaises(XanoConfigurationError):
                self.client.create_record(
                    "pacientes",
                    {"nome": "Fictício", "telefone": "11999999999"},
                )
            with self.assertRaises(XanoConfigurationError):
                self.client.update_record(
                    "profissionais",
                    21,
                    {"especialidade": "Clínica"},
                )
            with self.assertRaises(XanoConfigurationError):
                self.client.delete_record("pacientes", 11)
        self.transport.request.assert_not_called()

    def test_consultation_and_status_reads_use_confirmed_routes(self) -> None:
        with patch.dict(
            os.environ,
            {
                XANO_CONSULTAS_API_ENABLED_ENV: "true",
                XANO_STATUS_CONSULTA_API_ENABLED_ENV: "true",
                XANO_CONSULTAS_BASE_URL_ENV: (
                    "https://custom-consultations.example.invalid/api:group"
                ),
                XANO_STATUS_CONSULTA_BASE_URL_ENV: (
                    "https://custom-statuses.example.invalid/api:group"
                ),
            },
            clear=True,
        ):
            settings = XanoSettings.from_environment()
            client = XanoClient(settings, self.transport)
            self.transport.request.side_effect = [
                self._response([]),
                self._response(self.consultation),
                self._response(
                    [
                        {
                            "id": 31,
                            "nome": "Status sintético",
                            "created_at": 1762700000,
                        }
                    ]
                ),
            ]

            self.assertEqual(client.list_consultations(), [])
            self.assertEqual(client.get_consultation(52), self.consultation)
            self.assertEqual(
                client.list_consultation_statuses(),
                [
                    {
                        "id": 31,
                        "nome": "Status sintético",
                        "created_at": 1762700000,
                    }
                ],
            )

        calls = self.transport.request.call_args_list
        self.assertEqual(
            [call.args[0] for call in calls], ["GET", "GET", "GET"]
        )
        self.assertEqual(
            [call.args[1] for call in calls],
            [
                "https://custom-consultations.example.invalid/api:group/consulta",
                "https://custom-consultations.example.invalid/api:group/consulta/52",
                "https://custom-statuses.example.invalid/api:group/status_consulta",
            ],
        )
        self.assertTrue(
            all(
                call.kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS
                for call in calls
            )
        )

    def test_consultation_list_and_get_validate_confirmed_record_fields(self) -> None:
        self.transport.request.side_effect = [
            self._response([self.consultation]),
            self._response(self.consultation),
        ]
        client = XanoClient(self.settings, self.transport)

        with patch.dict(
            os.environ,
            {XANO_CONSULTAS_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            self.assertEqual(client.list_consultations(), [self.consultation])
            self.assertEqual(client.get_consultation(52), self.consultation)

        self.assertEqual(
            [call.args[1] for call in self.transport.request.call_args_list],
            [
                f"{self.settings.consultations_base_url}/consulta",
                f"{self.settings.consultations_base_url}/consulta/52",
            ],
        )
        self.transport.request.side_effect = None
        self.transport.request.return_value = self._response(
            {
                key: value
                for key, value in self.consultation.items()
                if key != "observacoes"
            }
        )
        with patch.dict(
            os.environ,
            {XANO_CONSULTAS_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            record_without_observations = client.get_consultation(52)
        self.assertNotIn("observacoes", record_without_observations)

        self.transport.request.return_value = self._response(
            {**self.consultation, "id": 53}
        )
        with patch.dict(
            os.environ,
            {XANO_CONSULTAS_API_ENABLED_ENV: "true"},
            clear=True,
        ), self.assertRaises(XanoResponseError):
            client.get_consultation(52)

        for invalid_record in (
            {"id": 52},
            {**self.consultation, "paciente_id": None},
            {**self.consultation, "data_e_hora_do_agendamento": "timestamp"},
            {**self.consultation, "observacoes": 42},
        ):
            with self.subTest(invalid_record=invalid_record):
                self.transport.request.return_value = self._response(
                    [invalid_record]
                )
                with patch.dict(
                    os.environ,
                    {XANO_CONSULTAS_API_ENABLED_ENV: "true"},
                    clear=True,
                ), self.assertRaises(XanoResponseError):
                    client.list_consultations()

    def test_professional_specialty_list_uses_confirmed_route_and_rejects_invalid_data(
        self,
    ) -> None:
        association = {
            "id": 61,
            "profissional_id": 21,
            "especialidade_id": 31,
            "created_at": 1762700000,
        }
        self.transport.request.return_value = self._response([association])
        client = XanoClient(self.settings, self.transport)

        with patch.dict(
            os.environ,
            {XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            self.assertEqual(
                client.list_professional_specialties(),
                [
                    {
                        "id": 61,
                        "profissional_id": 21,
                        "especialidade_id": 31,
                    }
                ],
            )

        self.assertEqual(
            self.transport.request.call_args.args[1],
            "https://associations.example.invalid/api:associations/"
            "profissional_especialidade",
        )
        for invalid_response in (
            [{"id": 61, "profissional_id": 0, "especialidade_id": 31}],
            [{"id": True, "profissional_id": 21, "especialidade_id": 31}],
            [
                association,
                {**association, "id": 62},
            ],
        ):
            with self.subTest(invalid_response=invalid_response):
                self.transport.request.return_value = self._response(
                    invalid_response
                )
                with patch.dict(
                    os.environ,
                    {XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV: "true"},
                    clear=True,
                ), self.assertRaises(XanoResponseError):
                    client.list_professional_specialties()

    def test_professional_specialty_create_and_delete_are_simulated(self) -> None:
        association = {
            "id": 61,
            "profissional_id": 21,
            "especialidade_id": 31,
        }
        client = XanoClient(self.settings, self.transport)

        with patch.dict(
            os.environ,
            {
                XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV: "true",
                XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            self.transport.request.return_value = self._response(association)
            self.assertEqual(
                client.create_professional_specialty(21, 31),
                association,
            )
            create_call = self.transport.request.call_args
            self.assertEqual(create_call.args[0], "POST")
            self.assertEqual(
                create_call.args[1],
                "https://associations.example.invalid/api:associations/"
                "profissional_especialidade",
            )
            self.assertEqual(
                create_call.kwargs["json"],
                {"profissional_id": 21, "especialidade_id": 31},
            )

            self.transport.request.return_value = self._response(None)
            client.delete_professional_specialty(61)
            delete_call = self.transport.request.call_args
            self.assertEqual(delete_call.args[0], "DELETE")
            self.assertEqual(
                delete_call.args[1],
                "https://associations.example.invalid/api:associations/"
                "profissional_especialidade/61",
            )

    def test_professional_specialty_mutations_reject_disabled_writes_and_invalid_ids(
        self,
    ) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(
            os.environ,
            {
                XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV: "true",
                XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED_ENV: "false",
            },
            clear=True,
        ):
            with self.assertRaises(XanoConfigurationError):
                client.create_professional_specialty(21, 31)
            with self.assertRaises(XanoConfigurationError):
                client.delete_professional_specialty(61)

        with patch.dict(
            os.environ,
            {
                XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED_ENV: "true",
                XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            with self.assertRaises(XanoResponseError):
                client.create_professional_specialty(0, 31)
            with self.assertRaises(XanoResponseError):
                client.create_professional_specialty(True, 31)
            with self.assertRaises(XanoResponseError):
                client.delete_professional_specialty(-1)

    def test_prontuario_crud_uses_confirmed_routes_and_simulated_transport(
        self,
    ) -> None:
        record = {
            "id": 71,
            "created_at": 1762700000,
            "paciente_id": 11,
            "profissional_id": 21,
            "numero_prontuario": "P-71",
            "observacoes": "Sintético",
            "data_da_atualizacao": 1762700100,
        }
        client = XanoClient(self.settings, self.transport)

        with patch.dict(
            os.environ,
            {
                XANO_PRONTUARIOS_API_ENABLED_ENV: "true",
                XANO_PRONTUARIOS_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            self.transport.request.return_value = self._response([record])
            self.assertEqual(client.list_prontuarios(), [record])
            self.assertEqual(
                self.transport.request.call_args.args[1],
                "https://prontuarios.example.invalid/api:prontuarios/prontuario",
            )

            self.transport.request.return_value = self._response(record)
            self.assertEqual(client.get_prontuario(71), record)

            self.transport.request.return_value = self._response(record)
            self.assertEqual(
                client.create_prontuario(
                    {
                        "paciente_id": 11,
                        "profissional_id": 21,
                        "numero_prontuario": " P-71 ",
                        "observacoes": None,
                    }
                ),
                record,
            )
            create_call = self.transport.request.call_args
            self.assertEqual(create_call.args[0], "POST")
            self.assertEqual(
                create_call.kwargs["json"],
                {
                    "paciente_id": 11,
                    "profissional_id": 21,
                    "numero_prontuario": "P-71",
                    "observacoes": None,
                },
            )

            updated = {**record, "observacoes": "Atualizado"}
            self.transport.request.return_value = self._response(updated)
            self.assertEqual(
                client.update_prontuario(
                    71,
                    {"observacoes": " Atualizado "},
                ),
                updated,
            )
            patch_call = self.transport.request.call_args
            self.assertEqual(patch_call.args[0], "PATCH")
            self.assertEqual(
                patch_call.args[1],
                "https://prontuarios.example.invalid/api:prontuarios/"
                "prontuario/71",
            )
            self.assertEqual(
                patch_call.kwargs["json"],
                {"observacoes": "Atualizado"},
            )

            self.transport.request.return_value = self._response({})
            client.delete_prontuario(71)
            delete_call = self.transport.request.call_args
            self.assertEqual(delete_call.args[0], "DELETE")
            self.assertEqual(
                delete_call.args[1],
                "https://prontuarios.example.invalid/api:prontuarios/"
                "prontuario/71",
            )

    def test_prontuario_writes_disabled_and_invalid_payloads(
        self,
    ) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(
            os.environ,
            {
                XANO_PRONTUARIOS_API_ENABLED_ENV: "true",
                XANO_PRONTUARIOS_WRITE_ENABLED_ENV: "false",
            },
            clear=True,
        ):
            with self.assertRaises(XanoConfigurationError):
                client.create_prontuario(
                    {"paciente_id": 11, "profissional_id": 21}
                )
            with self.assertRaises(XanoConfigurationError):
                client.update_prontuario(71, {"observacoes": "Teste"})
            with self.assertRaises(XanoConfigurationError):
                client.delete_prontuario(71)

        with patch.dict(
            os.environ,
            {
                XANO_PRONTUARIOS_API_ENABLED_ENV: "true",
                XANO_PRONTUARIOS_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            for payload in (
                {},
                {"paciente_id": 0, "profissional_id": 21},
                {"paciente_id": True, "profissional_id": 21},
                {"paciente_id": 11, "profissional_id": -1},
                {"observacoes": 123},
                {"campo_nao_confirmado": "valor"},
            ):
                with self.subTest(payload=payload):
                    with self.assertRaises(XanoResponseError):
                        client.create_prontuario(payload)
            with self.assertRaises(XanoResponseError):
                client.get_prontuario(0)
            with self.assertRaises(XanoResponseError):
                client.update_prontuario(71, {})
            with self.assertRaises(XanoResponseError):
                client.delete_prontuario(-1)

        self.transport.request.assert_not_called()

    def test_prontuario_read_requires_explicit_configuration(self) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(XanoConfigurationError):
                client.list_prontuarios()
            with self.assertRaises(XanoConfigurationError):
                client.get_prontuario(71)

    def test_prontuario_response_rejects_invalid_shapes(self) -> None:
        client = XanoClient(self.settings, self.transport)
        invalid_responses = (
            {},
            [{"id": 71, "paciente_id": 0, "profissional_id": 21}],
            [{"id": True, "paciente_id": 11, "profissional_id": 21}],
            [{"id": 71, "paciente_id": 11, "profissional_id": 21,
              "observacoes": 123}],
        )
        with patch.dict(
            os.environ,
            {XANO_PRONTUARIOS_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            for invalid_response in invalid_responses:
                with self.subTest(invalid_response=invalid_response):
                    self.transport.request.return_value = (
                        self._response(invalid_response)
                    )
                    with self.assertRaises(XanoResponseError):
                        client.list_prontuarios()

    def test_professional_specialty_read_requires_explicit_configuration(self) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(professional_specialties_api_enabled())
            with self.assertRaises(XanoConfigurationError):
                client.list_professional_specialties()
        self.transport.request.assert_not_called()

    def test_consultation_writes_use_confirmed_routes_and_preserve_inputs(self) -> None:
        create_payload = {
            "paciente_id": 11,
            "profissional_id": 21,
            "especialidade_id": 31,
            "data_e_hora_do_agendamento": 1762700000,
            "status_consulta_id": 41,
            "observacoes": "",
        }
        patch_payload = {
            "status_consulta_id": 41,
            "observacoes": None,
        }
        created_response = {
            "id": 52,
            "paciente_id": 11,
            "profissional_id": 21,
            "especialidade_id": 31,
            "data_e_hora_do_agendamento": 1762700000,
            "status_consulta_id": 41,
            "observacoes": "",
        }
        updated_response = {
            **created_response,
            "status_consulta_id": 41,
            "observacoes": None,
        }
        self.transport.request.side_effect = [
            self._response(created_response),
            self._response(updated_response),
            Mock(status_code=200),
        ]
        client = XanoClient(self.settings, self.transport)

        with patch.dict(
            os.environ,
            {
                XANO_CONSULTAS_API_ENABLED_ENV: "true",
                XANO_CONSULTAS_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            self.assertEqual(
                client.create_consultation(create_payload),
                created_response,
            )
            self.assertEqual(
                client.update_consultation(52, patch_payload),
                updated_response,
            )
            self.assertIsNone(client.delete_consultation(52))

        calls = self.transport.request.call_args_list
        self.assertEqual(
            [call.args[0] for call in calls],
            ["POST", "PATCH", "DELETE"],
        )
        self.assertEqual(
            [call.args[1] for call in calls],
            [
                f"{self.settings.consultations_base_url}/consulta",
                f"{self.settings.consultations_base_url}/consulta/52",
                f"{self.settings.consultations_base_url}/consulta/52",
            ],
        )
        self.assertEqual(calls[0].kwargs["json"], create_payload)
        self.assertEqual(calls[1].kwargs["json"], patch_payload)
        self.assertIsNone(calls[2].kwargs["json"])

    def test_consultation_writes_are_disabled_by_default(self) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(consultations_api_enabled())
            self.assertFalse(consultation_status_api_enabled())
            self.assertFalse(consultations_write_enabled())
            with self.assertRaises(XanoConfigurationError):
                client.list_consultations()
            with self.assertRaises(XanoConfigurationError):
                client.list_consultation_statuses()

        with patch.dict(
            os.environ,
            {XANO_CONSULTAS_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            with self.assertRaises(XanoConfigurationError):
                client.create_consultation({})
            with self.assertRaises(XanoConfigurationError):
                client.update_consultation(52, {})
            with self.assertRaises(XanoConfigurationError):
                client.delete_consultation(52)
        self.transport.request.assert_not_called()

    def test_consultation_bases_must_be_configured_externally(self) -> None:
        with patch.dict(
            os.environ,
            {
                XANO_CONSULTAS_API_ENABLED_ENV: "true",
                XANO_STATUS_CONSULTA_API_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            settings = XanoSettings.from_environment()
            client = XanoClient(settings, self.transport)
            self.transport.request.return_value = self._response([])

            with self.assertRaises(XanoConfigurationError):
                client.list_consultations()
            with self.assertRaises(XanoConfigurationError):
                client.list_consultation_statuses()

        self.transport.request.assert_not_called()

    def test_consultation_payload_validation_preserves_nullable_observation(self) -> None:
        client = XanoClient(self.settings, self.transport)
        with patch.dict(
            os.environ,
            {
                XANO_CONSULTAS_API_ENABLED_ENV: "true",
                XANO_CONSULTAS_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            consultation_response = {
                "id": 52,
                "paciente_id": 11,
                "profissional_id": 21,
                "especialidade_id": 31,
                "data_e_hora_do_agendamento": 1768480200000,
                "status_consulta_id": 41,
                "observacoes": None,
            }
            self.transport.request.return_value = self._response(
                consultation_response
            )
            client.update_consultation(52, {"status_consulta_id": 41})
            self.assertEqual(
                client.update_consultation(52, {"observacoes": None}),
                consultation_response,
            )
            self.assertEqual(
                [
                    call.kwargs["json"]
                    for call in self.transport.request.call_args_list
                ],
                [
                    {"status_consulta_id": 41},
                    {"observacoes": None},
                ],
            )
            for invalid_payload in (
                {"unexpected": "value"},
                {"paciente_id": True},
                {"paciente_id": 0},
                {"paciente_id": None},
                {"data_e_hora_do_agendamento": "timestamp"},
                {"observacoes": 42},
                {},
            ):
                with self.subTest(invalid_payload=invalid_payload):
                    with self.assertRaises(XanoResponseError):
                        client.update_consultation(52, invalid_payload)

    def test_consultation_create_requires_all_nonnullable_reference_fields(self) -> None:
        client = XanoClient(self.settings, self.transport)
        valid_payload = {
            "paciente_id": 11,
            "profissional_id": 21,
            "especialidade_id": 31,
            "data_e_hora_do_agendamento": 1768480200000,
            "status_consulta_id": 41,
        }
        with patch.dict(
            os.environ,
            {
                XANO_CONSULTAS_API_ENABLED_ENV: "true",
                XANO_CONSULTAS_WRITE_ENABLED_ENV: "true",
            },
            clear=True,
        ):
            for field in valid_payload:
                invalid_payload = dict(valid_payload)
                del invalid_payload[field]
                with self.subTest(field=field):
                    with self.assertRaises(XanoResponseError):
                        client.create_consultation(invalid_payload)
            consultation_response = {
                "id": 52,
                "paciente_id": 11,
                "profissional_id": 21,
                "especialidade_id": 31,
                "data_e_hora_do_agendamento": 1768480200000,
                "status_consulta_id": 41,
                "observacoes": None,
            }
            self.transport.request.return_value = self._response(
                consultation_response
            )
            self.assertEqual(client.create_consultation(
                {**valid_payload, "observacoes": None}
            ), consultation_response)

        self.assertEqual(self.transport.request.call_count, 1)
        self.assertEqual(
            self.transport.request.call_args.kwargs["json"],
            {**valid_payload, "observacoes": None},
        )

    def test_consultation_datetime_converts_using_sao_paulo_timezone(self) -> None:
        timestamp = consultation_datetime_to_unix_ms(
            date(2026, 1, 15),
            time(9, 30),
        )
        self.assertEqual(timestamp, 1768480200000)
        self.assertEqual(
            consultation_timestamp_to_local_datetime(timestamp),
            datetime(
                2026,
                1,
                15,
                9,
                30,
                tzinfo=ZoneInfo("America/Sao_Paulo"),
            ),
        )

        with self.assertRaises(ValueError):
            consultation_timestamp_to_local_datetime(True)
        with self.assertRaises(ValueError):
            consultation_timestamp_to_local_datetime("1768480200000")
        with self.assertRaises(ValueError):
            consultation_datetime_to_unix_ms("2026-01-15", time(9, 30))

    def test_consultation_status_response_requires_confirmed_fields_and_types(self) -> None:
        client = XanoClient(self.settings, self.transport)
        invalid_responses = (
            [{"id": 1, "nome": "Status", "created_at": "timestamp"}],
            [{"id": True, "nome": "Status", "created_at": 1}],
            [{"id": 1, "nome": 3, "created_at": 1}],
            [{"id": 1, "nome": "Status"}],
        )
        with patch.dict(
            os.environ,
            {XANO_STATUS_CONSULTA_API_ENABLED_ENV: "true"},
            clear=True,
        ):
            for invalid_response in invalid_responses:
                with self.subTest(invalid_response=invalid_response):
                    self.transport.request.return_value = self._response(
                        invalid_response
                    )
                    with self.assertRaises(XanoResponseError):
                        client.list_consultation_statuses()


if __name__ == "__main__":
    unittest.main()
