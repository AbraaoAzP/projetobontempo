import os
import unittest
from pathlib import Path
from typing import ContextManager
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.xano import XanoClient


FRONTEND = Path(__file__).resolve().parents[1]
SPECIALTY = {"id": 7, "nome": "Cardiologia"}


class SpecialtyPageTests(unittest.TestCase):
    def _environment(
        self, *, api_enabled: str = "true", write_enabled: str = "true"
    ) -> ContextManager[object]:
        values = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("XANO_")
        }
        values["XANO_ESPECIALIDADES_API_ENABLED"] = api_enabled
        values["XANO_ESPECIALIDADES_WRITE_ENABLED"] = write_enabled
        return patch.dict(
            os.environ,
            values,
            clear=True,
        )

    def _run_page(self) -> AppTest:
        page_path = FRONTEND / "pages" / "3_Especialidades.py"
        return AppTest.from_file(str(page_path), default_timeout=10).run()

    def test_api_disabled_does_not_read_or_write(self) -> None:
        with self._environment(api_enabled="false"), patch.object(
            XanoClient, "list_specialties"
        ) as list_specialties, patch.object(
            XanoClient, "create_specialty"
        ) as create, patch.object(
            XanoClient, "update_specialty"
        ) as update, patch.object(
            XanoClient, "delete_specialty"
        ) as delete, patch(
            "requests.Session.request"
        ) as request:
            page = self._run_page()

        list_specialties.assert_not_called()
        create.assert_not_called()
        update.assert_not_called()
        delete.assert_not_called()
        request.assert_not_called()
        self.assertTrue(any("desabilitada" in item.value for item in page.info))
        self.assertEqual(len(page.exception), 0)

    def test_enabled_read_displays_catalog_and_empty_state(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_specialties", return_value=[]
        ) as list_specialties:
            page = self._run_page()

        list_specialties.assert_called_once_with()
        self.assertTrue(
            any("Nenhuma especialidade cadastrada" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_create_submits_trimmed_name(self) -> None:
        created = {"id": 8, "nome": "Neurologia"}
        with self._environment(), patch.object(
            XanoClient, "list_specialties", return_value=[]
        ), patch.object(
            XanoClient, "create_specialty", return_value=created
        ) as create:
            page = self._run_page()
            page.text_input(key="specialty_create_name").set_value(" Neurologia ")
            page.button(
                key="FormSubmitter:create_specialty-Cadastrar especialidade"
            ).click()
            page.run()

        create.assert_called_once_with({"nome": "Neurologia"})
        self.assertTrue(any("cadastrada" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_create_rejects_empty_or_duplicate_name_without_request(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_specialties", return_value=[SPECIALTY]
        ), patch.object(XanoClient, "create_specialty") as create:
            page = self._run_page()
            page.button(
                key="FormSubmitter:create_specialty-Cadastrar especialidade"
            ).click()
            page.run()
            self.assertTrue(any("obrigatório" in item.value for item in page.error))

            page.text_input(key="specialty_create_name").set_value(" cardiologia ")
            page.button(
                key="FormSubmitter:create_specialty-Cadastrar especialidade"
            ).click()
            page.run()

        create.assert_not_called()
        self.assertTrue(
            any("Já existe uma especialidade" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)

    def test_load_and_edit_use_item_and_patch_endpoints(self) -> None:
        updated = {"id": 7, "nome": "Cardiologia pediátrica"}
        with self._environment(), patch.object(
            XanoClient, "list_specialties", return_value=[SPECIALTY]
        ), patch.object(
            XanoClient, "get_specialty", return_value=SPECIALTY
        ) as get_specialty, patch.object(
            XanoClient, "update_specialty", return_value=updated
        ) as update:
            page = self._run_page()
            page.button(key="specialty_load").click()
            page.run()
            get_specialty.assert_called_once_with(7)

            page.text_input(key="specialty_edit_name_7").set_value(
                "Cardiologia pediátrica"
            )
            page.button(
                key="FormSubmitter:edit_specialty_7-Salvar alterações"
            ).click()
            page.run()

        update.assert_called_once_with(7, {"nome": "Cardiologia pediátrica"})
        self.assertTrue(any("atualizada" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_delete_requires_confirmation_and_reports_success(self) -> None:
        with self._environment(), patch.object(
            XanoClient,
            "list_specialties",
            return_value=[SPECIALTY],
        ), patch.object(XanoClient, "delete_specialty") as delete:
            page = self._run_page()
            delete_button = page.button(key="specialty_delete_7")
            self.assertTrue(delete_button.disabled)
            delete.assert_not_called()

            page.checkbox(key="specialty_delete_confirm_7").check()
            page.run()
            self.assertFalse(page.button(key="specialty_delete_7").disabled)
            delete.assert_not_called()

            page.button(key="specialty_delete_7").click()
            page.run()

        delete.assert_called_once_with(7)
        self.assertTrue(any("excluída" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_api_errors_are_shown_without_success(self) -> None:
        from services.xano import XanoHTTPError

        with self._environment(), patch.object(
            XanoClient, "list_specialties", side_effect=XanoHTTPError(503)
        ):
            page = self._run_page()

        self.assertTrue(
            any("HTTP 503" in item.value for item in page.error)
        )
        self.assertEqual(len(page.success), 0)
        self.assertEqual(len(page.exception), 0)


if __name__ == "__main__":
    unittest.main()
