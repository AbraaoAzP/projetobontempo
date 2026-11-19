import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.xano import XanoClient, XanoHTTPError
from services.xano_cache import clear_xano_read_caches


FRONTEND = Path(__file__).resolve().parents[1]
PATIENT = {"id": 11, "nome": "Paciente sintético"}
PROFESSIONAL = {"id": 21, "nome": "Profissional sintético"}
PRONTUARIO = {
    "id": 71,
    "created_at": 1762700000,
    "paciente_id": 11,
    "profissional_id": 21,
    "numero_prontuario": "P-71",
    "observacoes": "Observação sintética",
    "data_da_atualizacao": 1762700100,
}


class ProntuarioPageTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_xano_read_caches()

    def tearDown(self) -> None:
        clear_xano_read_caches()
    def _environment(
        self,
        *,
        api_enabled: str = "false",
        write_enabled: str = "false",
    ):
        values = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("XANO_")
        }
        values["XANO_PRONTUARIOS_API_ENABLED"] = api_enabled
        values["XANO_PRONTUARIOS_WRITE_ENABLED"] = write_enabled
        values["XANO_PRONTUARIOS_BASE_URL"] = (
            "https://prontuarios.example.invalid/api:prontuarios"
        )
        values["XANO_API_ENABLED"] = "true"
        values["XANO_PACIENTES_BASE_URL"] = (
            "https://patients.example.invalid/api"
        )
        values["XANO_PROFISSIONAIS_BASE_URL"] = (
            "https://professionals.example.invalid/api"
        )
        return patch.dict(os.environ, values, clear=True)

    def _run_page(self) -> AppTest:
        page_path = FRONTEND / "pages" / "5_Prontuarios.py"
        return AppTest.from_file(str(page_path), default_timeout=10).run()

    def test_disabled_read_does_not_send_requests(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_prontuarios"
        ) as list_prontuarios, patch.object(
            XanoClient, "create_prontuario"
        ) as create, patch.object(
            XanoClient, "update_prontuario"
        ) as update, patch.object(
            XanoClient, "delete_prontuario"
        ) as delete:
            page = self._run_page()

        list_prontuarios.assert_not_called()
        create.assert_not_called()
        update.assert_not_called()
        delete.assert_not_called()
        self.assertTrue(
            any("desabilitada" in item.value for item in page.warning)
        )
        self.assertEqual(len(page.exception), 0)

    def test_empty_collection_is_reported(self) -> None:
        with self._environment(api_enabled="true"), patch.object(
            XanoClient, "list_prontuarios", return_value=[]
        ), patch.object(
            XanoClient, "list_records",
            side_effect=lambda resource: (
                [PATIENT] if resource == "pacientes" else [PROFESSIONAL]
            ),
        ):
            page = self._run_page()

        self.assertTrue(
            any("Não há prontuários válidos" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_create_is_mocked_and_invalidates_cache(self) -> None:
        with self._environment(
            api_enabled="true",
            write_enabled="true",
        ), patch.object(
            XanoClient, "list_prontuarios", return_value=[]
        ), patch.object(
            XanoClient, "list_records",
            side_effect=lambda resource: (
                [PATIENT] if resource == "pacientes" else [PROFESSIONAL]
            ),
        ), patch.object(
            XanoClient,
            "create_prontuario",
            return_value=PRONTUARIO,
        ) as create, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.selectbox(
                key="xano_create_prontuario_patient"
            ).set_value(11)
            page.run()
            page.selectbox(
                key="xano_create_prontuario_professional"
            ).set_value(21)
            page.run()
            page.text_input(
                key="xano_create_prontuario_numero"
            ).set_value("P-71")
            page.text_area(
                key="xano_create_prontuario_observacoes"
            ).set_value("Observação sintética")
            page.button(
                key="FormSubmitter:xano_create_prontuario-Cadastrar prontuário"
            ).click()
            page.run()

        create.assert_called_once_with(
            {
                "paciente_id": 11,
                "profissional_id": 21,
                "numero_prontuario": "P-71",
                "observacoes": "Observação sintética",
            }
        )
        clear_cache.assert_called_once_with()
        self.assertTrue(
            any("cadastrado" in item.value for item in page.success)
        )
        self.assertEqual(len(page.exception), 0)

    def test_load_edit_and_delete_are_mocked(self) -> None:
        with self._environment(
            api_enabled="true",
            write_enabled="true",
        ), patch.object(
            XanoClient,
            "list_prontuarios",
            return_value=[PRONTUARIO],
        ), patch.object(
            XanoClient, "list_records",
            side_effect=lambda resource: (
                [PATIENT] if resource == "pacientes" else [PROFESSIONAL]
            ),
        ), patch.object(
            XanoClient, "get_prontuario", return_value=PRONTUARIO
        ) as get, patch.object(
            XanoClient,
            "update_prontuario",
            return_value={**PRONTUARIO, "observacoes": "Atualizada"},
        ) as update, patch.object(
            XanoClient, "delete_prontuario"
        ) as delete, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.selectbox(
                key="xano_edit_prontuario_id"
            ).set_value(71)
            page.run()
            page.button(
                key="xano_load_prontuario"
            ).click()
            page.run()

            page.text_area(
                key="xano_edit_prontuario_observacoes_71"
            ).set_value("Atualizada")
            page.button(
                key="FormSubmitter:xano_edit_prontuario_71-Salvar alterações"
            ).click()
            page.run()

        get.assert_called_once_with(71)
        update.assert_called_once_with(
            71,
            {"observacoes": "Atualizada"},
        )
        delete.assert_not_called()
        clear_cache.assert_called_once_with()
        self.assertTrue(
            any("atualizado" in item.value for item in page.success)
        )
        self.assertEqual(len(page.exception), 0)

    def test_delete_requires_confirmation_and_http_error_is_visible(
        self,
    ) -> None:
        with self._environment(
            api_enabled="true",
            write_enabled="true",
        ), patch.object(
            XanoClient,
            "list_prontuarios",
            return_value=[PRONTUARIO],
        ), patch.object(
            XanoClient, "list_records",
            side_effect=lambda resource: (
                [PATIENT] if resource == "pacientes" else [PROFESSIONAL]
            ),
        ), patch.object(
            XanoClient, "get_prontuario", return_value=PRONTUARIO
        ), patch.object(
            XanoClient,
            "delete_prontuario",
            side_effect=XanoHTTPError(409),
        ) as delete, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.selectbox(
                key="xano_edit_prontuario_id"
            ).set_value(71)
            page.run()
            page.button(
                key="xano_load_prontuario"
            ).click()
            page.run()

            delete_button = page.button(
                key="xano_delete_prontuario_71"
            )
            self.assertTrue(delete_button.disabled)
            delete.assert_not_called()

            page.checkbox(
                key="xano_delete_confirm_prontuario_71"
            ).check()
            page.run()
            page.button(
                key="xano_delete_prontuario_71"
            ).click()
            page.run()

        delete.assert_called_once_with(71)
        clear_cache.assert_not_called()
        self.assertTrue(
            any("Não foi possível excluir" in item.value for item in page.error)
        )
        self.assertTrue(
            any("HTTP 409" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)


if __name__ == "__main__":
    unittest.main()
