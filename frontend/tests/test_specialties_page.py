import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest


FRONTEND = Path(__file__).resolve().parents[1]


class SpecialtyPageTests(unittest.TestCase):
    def test_disabled_integration_does_not_read_sqlite_or_network(self) -> None:
        page_path = FRONTEND / "pages" / "3_Especialidades.py"
        with (
            patch.dict(os.environ, {"XANO_ESPECIALIDADES_API_ENABLED": ""}),
            patch("services.database.list_specialties") as list_specialties,
            patch("services.database.create_specialty") as create_specialty,
            patch("services.xano.XanoClient.list_specialties") as list_xano,
            patch("requests.Session.request") as request,
        ):
            page = AppTest.from_file(
                str(page_path), default_timeout=10
            ).run()

        list_specialties.assert_not_called()
        create_specialty.assert_not_called()
        list_xano.assert_not_called()
        request.assert_not_called()
        self.assertTrue(
            any(
                "leitura do catálogo Xano está desabilitada" in item.value
                for item in page.info
            )
        )
        self.assertTrue(
            any("Consultas continua usando" in item.value for item in page.warning)
        )
        self.assertEqual(len(page.exception), 0)
        self.assertEqual(len(page.button), 0)
        self.assertEqual(len(page.text_input), 0)

    def test_enabled_read_displays_raw_response_without_parsing(self) -> None:
        page_path = FRONTEND / "pages" / "3_Especialidades.py"
        with (
            patch.dict(
                os.environ, {"XANO_ESPECIALIDADES_API_ENABLED": "true"}
            ),
            patch(
                "services.xano.XanoClient.list_specialties",
                return_value=Mock(text='{"items": [{"id": 7, "nome": "Fictícia"}]}'),
            ) as list_xano,
        ):
            page = AppTest.from_file(
                str(page_path), default_timeout=10
            ).run()

        list_xano.assert_called_once_with()
        self.assertTrue(
            any("Resposta da API" in item.value for item in page.subheader)
        )
        self.assertTrue(
            any(
                "nenhum formato de resposta foi presumido" in item.value
                for item in page.caption
            )
        )
        self.assertTrue(
            any('"id": 7' in item.value for item in page.code)
        )
        self.assertEqual(len(page.exception), 0)
        self.assertEqual(len(page.button), 0)


if __name__ == "__main__":
    unittest.main()
