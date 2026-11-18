import os
import unittest
from datetime import date, time
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.xano import (
    XanoClient,
    XanoConfigurationError,
    XanoHTTPError,
    XanoResponseError,
)
from services.xano_cache import clear_xano_read_caches


FRONTEND = Path(__file__).resolve().parents[1]
CONSULTATION = {
    "id": 52,
    "paciente_id": 11,
    "profissional_id": 21,
    "especialidade_id": 31,
    "data_e_hora_do_agendamento": 1768480200000,
    "status_consulta_id": 41,
    "observacoes": "nota sintética",
}
PATIENTS = [
    {"id": 0, "nome": "Referência padrão"},
    {"id": 11, "nome": "Paciente sintético"},
]
PROFESSIONALS = [
    {"id": 0, "nome": "Referência padrão"},
    {
        "id": 21,
        "nome": "Profissional sintético",
        "especialidade": "Especialidade sintética",
    },
]
SPECIALTIES = [
    {"id": 0, "nome": "Referência padrão"},
    {"id": 31, "nome": "Especialidade sintética"},
]


class ConsultationsPageTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_xano_read_caches()

    def tearDown(self) -> None:
        clear_xano_read_caches()

    def _environment(
        self,
        *,
        consultations_enabled: str = "false",
        statuses_enabled: str = "false",
        catalogs_enabled: str = "false",
    ):
        values = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("XANO_")
        }
        values["XANO_CONSULTAS_API_ENABLED"] = consultations_enabled
        values["XANO_STATUS_CONSULTA_API_ENABLED"] = statuses_enabled
        values["XANO_API_ENABLED"] = catalogs_enabled
        values["XANO_ESPECIALIDADES_API_ENABLED"] = catalogs_enabled
        values["XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED"] = "false"
        return patch.dict(os.environ, values, clear=True)

    def _run_page(self) -> AppTest:
        page_path = FRONTEND / "pages" / "4_Consultas.py"
        return AppTest.from_file(str(page_path), default_timeout=10).run()

    def test_xano_mode_shows_empty_consultations_and_confirmed_status_fields(self):
        status = {"id": 5, "nome": "Agendada", "created_at": 1700000000}
        with self._environment(
            consultations_enabled="true",
            statuses_enabled="true",
            catalogs_enabled="true",
        ), patch.object(
            XanoClient, "list_consultations", return_value=[]
        ) as list_consultations, patch.object(
            XanoClient, "list_consultation_statuses", return_value=[status]
        ) as list_statuses, patch(
            "services.xano.XanoClient.list_records",
            side_effect=lambda resource: {
                "pacientes": PATIENTS,
                "profissionais": PROFESSIONALS,
            }[resource],
        ) as list_records, patch.object(
            XanoClient, "list_specialties", return_value=SPECIALTIES
        ) as list_specialties, patch(
            "services.database.list_patients"
        ) as list_patients, patch(
            "services.database.list_professionals"
        ) as list_professionals, patch(
            "services.database.list_appointments"
        ) as list_appointments:
            page = self._run_page()

        list_consultations.assert_called_once_with()
        list_statuses.assert_called_once_with()
        self.assertEqual(list_records.call_count, 2)
        list_specialties.assert_called_once_with()
        list_patients.assert_not_called()
        list_professionals.assert_not_called()
        list_appointments.assert_not_called()
        self.assertTrue(
            any("Nenhuma consulta retornada pelo Xano" in item.value for item in page.info)
        )
        self.assertEqual(len(page.dataframe), 1)
        self.assertEqual(
            page.dataframe[0].value.to_dict("records"),
            [{"id": 5, "nome": "Agendada", "created_at": 1700000000}],
        )
        self.assertEqual(
            page.selectbox(key="xano_create_patient").options,
            ["Paciente sintético (#11)"],
        )
        self.assertEqual(
            page.selectbox(key="xano_create_professional").options,
            ["Profissional sintético (#21)"],
        )
        self.assertEqual(
            page.selectbox(key="xano_create_specialty").options,
            [],
        )
        self.assertTrue(page.selectbox(key="xano_create_specialty").disabled)
        self.assertTrue(
            any(
                "campo textual especialidade do Profissional não será usado"
                in item.value
                for item in page.warning
            )
        )
        self.assertEqual(
            page.selectbox(key="xano_create_status").options,
            ["Agendada (#5)"],
        )
        self.assertTrue(
            page.button(
                key="FormSubmitter:xano_create_consultation-Cadastrar consulta"
            ).disabled
        )
        self.assertEqual(len(page.exception), 0)

    def test_nonempty_consultations_are_not_rendered_with_unconfirmed_fields(self):
        private_note = "conteudo-sintetico-nao-exibir"
        with self._environment(consultations_enabled="true"), patch.object(
            XanoClient,
            "list_consultations",
            return_value=[{**CONSULTATION, "observacoes": private_note}],
        ), patch.object(
            XanoClient, "list_consultation_statuses", return_value=[]
        ), patch(
            "services.database.list_patients"
        ) as list_patients, patch(
            "services.database.list_appointments"
        ) as list_appointments:
            page = self._run_page()

        list_patients.assert_not_called()
        list_appointments.assert_not_called()
        self.assertTrue(
            any(
                "1 consulta(s) retornada(s)" in item.value
                for item in page.info
            )
        )
        self.assertFalse(
            any(private_note in str(item.value) for item in page.dataframe)
        )
        self.assertEqual(len(page.dataframe), 1)
        self.assertEqual(len(page.exception), 0)

    def test_status_only_integration_uses_exclusive_xano_mode(self):
        with self._environment(statuses_enabled="true"), patch.object(
            XanoClient, "list_consultations"
        ) as list_consultations, patch.object(
            XanoClient, "list_consultation_statuses", return_value=[]
        ) as list_statuses, patch(
            "services.database.list_patients"
        ) as list_patients:
            page = self._run_page()

        list_consultations.assert_not_called()
        list_statuses.assert_called_once_with()
        list_patients.assert_not_called()
        self.assertTrue(
            any("leitura de Consultas no Xano está desabilitada" in item.value for item in page.info)
        )
        self.assertTrue(
            any("Nenhum status de Consulta retornado pelo Xano" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_xano_error_is_visible_without_local_fallback(self):
        with self._environment(
            consultations_enabled="true", catalogs_enabled="true"
        ), patch.object(
            XanoClient,
            "list_consultations",
            side_effect=XanoHTTPError(503),
        ), patch.object(
            XanoClient, "list_consultation_statuses", return_value=[]
        ), patch.object(
            XanoClient,
            "list_records",
            side_effect=XanoHTTPError(502),
        ), patch.object(
            XanoClient,
            "list_specialties",
            side_effect=XanoHTTPError(501),
        ), patch(
            "services.database.list_patients"
        ) as list_patients, patch(
            "services.database.list_professionals"
        ) as list_professionals, patch(
            "services.database.list_appointments"
        ) as list_appointments:
            page = self._run_page()

        list_patients.assert_not_called()
        list_professionals.assert_not_called()
        list_appointments.assert_not_called()
        self.assertTrue(any("HTTP 503" in item.value for item in page.error))
        self.assertTrue(any("HTTP 502" in item.value for item in page.error))
        self.assertTrue(any("HTTP 501" in item.value for item in page.error))
        self.assertFalse(
            any("Nenhuma consulta retornada pelo Xano" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_configuration_and_incompatible_response_errors_are_visible(self):
        with self._environment(
            consultations_enabled="true", statuses_enabled="true"
        ), patch.object(
            XanoClient,
            "list_consultations",
            side_effect=XanoConfigurationError("URL de Consultas ausente."),
        ), patch.object(
            XanoClient,
            "list_consultation_statuses",
            side_effect=XanoResponseError("Resposta de Status incompatível."),
        ), patch(
            "services.database.list_patients"
        ) as list_patients:
            page = self._run_page()

        list_patients.assert_not_called()
        self.assertTrue(
            any("URL de Consultas ausente" in item.value for item in page.error)
        )
        self.assertTrue(
            any("Resposta de Status incompatível" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)

    def test_disabled_xano_preserves_existing_local_page(self):
        with self._environment(), patch(
            "services.database.list_patients", return_value=[]
        ) as list_patients, patch(
            "services.database.list_professionals", return_value=[]
        ) as list_professionals, patch(
            "services.database.list_appointments", return_value=[]
        ) as list_appointments, patch.object(
            XanoClient, "list_consultations"
        ) as list_consultations, patch.object(
            XanoClient, "list_consultation_statuses"
        ) as list_statuses:
            page = self._run_page()

        list_patients.assert_called_once_with()
        list_professionals.assert_called_once_with()
        list_appointments.assert_called_once_with()
        list_consultations.assert_not_called()
        list_statuses.assert_not_called()
        self.assertTrue(
            any("Nenhuma consulta cadastrada neste banco SQLite local" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_loading_consultation_uses_get_by_id_and_populates_edit_form(self):
        with self._environment(
            consultations_enabled="true",
            statuses_enabled="true",
            catalogs_enabled="true",
        ), patch.object(
            XanoClient, "list_consultations", return_value=[CONSULTATION]
        ), patch.object(
            XanoClient,
            "list_consultation_statuses",
            return_value=[{"id": 41, "nome": "Agendada", "created_at": 2}],
        ), patch.object(
            XanoClient,
            "list_records",
            side_effect=lambda resource: {
                "pacientes": PATIENTS[1:],
                "profissionais": PROFESSIONALS[1:],
            }[resource],
        ), patch.object(
            XanoClient, "list_specialties", return_value=SPECIALTIES[1:]
        ), patch.object(
            XanoClient, "get_consultation", return_value=CONSULTATION
        ) as get_consultation, patch.object(
            XanoClient, "create_consultation"
        ) as create, patch.object(
            XanoClient, "update_consultation"
        ) as update, patch.object(
            XanoClient, "delete_consultation"
        ) as delete:
            page = self._run_page()
            page.selectbox(key="xano_edit_consultation_id").set_value(52)
            page.run()
            page.button(key="xano_load_consultation").click()
            page.run()

        get_consultation.assert_called_once_with(52)
        self.assertEqual(
            page.date_input(key="xano_edit_date").value,
            date(2026, 1, 15),
        )
        self.assertEqual(
            page.time_input(key="xano_edit_time").value,
            time(9, 30),
        )
        self.assertEqual(
            page.selectbox(key="xano_edit_specialty").options,
            [],
        )
        self.assertTrue(page.selectbox(key="xano_edit_specialty").disabled)
        self.assertTrue(
            page.button(
                key="FormSubmitter:xano_edit_consultation-Salvar alterações"
            ).disabled
        )
        self.assertTrue(page.button(key="xano_delete_consultation").disabled)
        create.assert_not_called()
        update.assert_not_called()
        delete.assert_not_called()
        self.assertEqual(len(page.exception), 0)

    def test_specialties_follow_selected_professional_associations(self):
        associations = [
            {"id": 61, "profissional_id": 21, "especialidade_id": 31}
        ]
        with self._environment(
            consultations_enabled="true",
            statuses_enabled="true",
            catalogs_enabled="true",
        ), patch.dict(
            os.environ,
            {"XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED": "true"},
        ), patch.object(
            XanoClient, "list_consultations", return_value=[]
        ), patch.object(
            XanoClient, "list_consultation_statuses", return_value=[]
        ), patch(
            "services.xano.XanoClient.list_records",
            side_effect=lambda resource: {
                "pacientes": PATIENTS[1:],
                "profissionais": PROFESSIONALS[1:],
            }[resource],
        ), patch.object(
            XanoClient, "list_specialties", return_value=SPECIALTIES[1:]
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=associations,
        ) as list_associations:
            page = self._run_page()
            page.selectbox(key="xano_create_professional").set_value(21)
            page.run()

        self.assertGreaterEqual(list_associations.call_count, 1)
        self.assertEqual(
            page.selectbox(key="xano_create_specialty").options,
            ["Especialidade sintética (#31)"],
        )
        self.assertFalse(page.selectbox(key="xano_create_specialty").disabled)
        self.assertEqual(len(page.exception), 0)
        self.assertEqual(list_associations.call_count, 1)

    def test_professional_specialty_429_is_explicit_and_not_repeated_on_rerun(self):
        with self._environment(
            consultations_enabled="true",
            statuses_enabled="true",
            catalogs_enabled="true",
        ), patch.dict(
            os.environ,
            {"XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED": "true"},
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            side_effect=XanoHTTPError(429),
        ) as list_associations:
            page = self._run_page()
            page.run()

        list_associations.assert_called_once_with()
        self.assertTrue(
            any("HTTP 429" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)


if __name__ == "__main__":
    unittest.main()
