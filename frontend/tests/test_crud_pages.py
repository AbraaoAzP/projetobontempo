import os
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.xano import XanoClient, XanoHTTPError


FRONTEND = Path(__file__).resolve().parents[1]


class CrudPageTests:
    page_name: str
    resource: str
    prefix: str
    record: dict[str, object]

    @contextmanager
    def _environment(
        self,
        enabled: str = "true",
        *,
        relations_enabled: str = "false",
        relation_writes: str = "false",
    ) -> Iterator[None]:
        values = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("XANO_")
        }
        values["XANO_API_ENABLED"] = enabled
        values["XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED"] = relations_enabled
        values["XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED"] = relation_writes
        values["XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL"] = (
            "https://relations.example.invalid/api"
        )
        values["XANO_ESPECIALIDADES_API_ENABLED"] = "true"
        values["XANO_ESPECIALIDADES_BASE_URL"] = (
            "https://specialties.example.invalid/api"
        )
        with patch.dict(os.environ, values, clear=True):
            yield

    def _run_page(self) -> AppTest:
        page_path = FRONTEND / "pages" / self.page_name
        return AppTest.from_file(str(page_path), default_timeout=10).run()

    def test_create_submits_validated_payload(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", side_effect=[[], [self.record]]
        ), patch.object(
            XanoClient, "create_record", return_value=self.record
        ) as create:
            page = self._run_page()
            page.text_input(key=f"{self.prefix}_create_name").set_value(" Novo ")
            page.text_input(key=f"{self.prefix}_create_phone").set_value(" 11999999999 ")
            page.text_input(key=f"{self.prefix}_create_email").set_value("")
            if self.resource == "profissionais":
                page.text_input(key="professional_create_specialty").set_value(
                    " Clínica "
                )
            page.button(
                key=f"FormSubmitter:create_{self.prefix}-Cadastrar "
                + ("paciente" if self.resource == "pacientes" else "profissional")
            ).click()
            page.run()

        payload = create.call_args.args[1]
        self.assertEqual(payload["nome"], " Novo ")
        self.assertEqual(payload["telefone"], " 11999999999 ")
        self.assertIsNone(payload["email"])
        if self.resource == "profissionais":
            self.assertEqual(payload["especialidade"], " Clínica ")
        self.assertTrue(any("cadastrado" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_empty_collection_is_reported_as_success(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[]
        ) as list_records:
            page = self._run_page()

        list_records.assert_called_once_with(self.resource)
        expected = "Nenhum paciente" if self.resource == "pacientes" else "Nenhum profissional"
        self.assertTrue(any(expected in item.value for item in page.info))
        self.assertEqual(len(page.exception), 0)

    def test_api_disabled_does_not_read_or_write(self) -> None:
        with self._environment(enabled="false"), patch.object(
            XanoClient, "list_records"
        ) as list_records, patch.object(XanoClient, "create_record") as create:
            page = self._run_page()

        list_records.assert_not_called()
        create.assert_not_called()
        self.assertTrue(
            any("desabilitada" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_invalid_create_input_is_not_sent(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[]
        ), patch.object(XanoClient, "create_record") as create:
            page = self._run_page()
            page.button(
                key=f"FormSubmitter:create_{self.prefix}-Cadastrar "
                + ("paciente" if self.resource == "pacientes" else "profissional")
            ).click()
            page.run()

        create.assert_not_called()
        self.assertTrue(any("Informe o nome" in item.value for item in page.error))

    def test_invalid_email_is_not_sent(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[]
        ), patch.object(XanoClient, "create_record") as create:
            page = self._run_page()
            page.text_input(key=f"{self.prefix}_create_name").set_value("Nome")
            page.text_input(key=f"{self.prefix}_create_phone").set_value("11999999999")
            page.text_input(key=f"{self.prefix}_create_email").set_value("email-invalido")
            page.button(
                key=f"FormSubmitter:create_{self.prefix}-Cadastrar "
                + ("paciente" if self.resource == "pacientes" else "profissional")
            ).click()
            page.run()

        create.assert_not_called()
        self.assertTrue(any("email válido" in item.value for item in page.error))

    def test_invalid_phone_format_is_not_sent(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[]
        ), patch.object(XanoClient, "create_record") as create:
            page = self._run_page()
            page.text_input(key=f"{self.prefix}_create_name").set_value("Nome")
            page.text_input(key=f"{self.prefix}_create_phone").set_value("123-ABC")
            page.button(
                key=f"FormSubmitter:create_{self.prefix}-Cadastrar "
                + ("paciente" if self.resource == "pacientes" else "profissional")
            ).click()
            page.run()

        create.assert_not_called()
        self.assertTrue(any("telefone" in item.value.lower() for item in page.error))

    def test_load_and_edit_use_item_and_patch_endpoints(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "get_record", return_value=self.record
        ) as get_record, patch.object(
            XanoClient, "update_record", return_value=self.record
        ) as update:
            page = self._run_page()
            page.button(key=f"{self.prefix}_load").click()
            page.run()

            get_record.assert_called_once_with(
                self.resource, int(self.record["id"])
            )
            name_key = f"{self.prefix}_edit_name_{self.record['id']}"
            page.text_input(key=name_key).set_value("Nome atualizado")
            if self.resource == "profissionais":
                page.text_input(
                    key=f"professional_edit_specialty_{self.record['id']}"
                ).set_value("Especialidade atualizada")
            form_key = (
                f"FormSubmitter:edit_{self.prefix}_{self.record['id']}"
                "-Salvar alterações"
            )
            page.button(key=form_key).click()
            page.run()

        update.assert_called_once()
        self.assertEqual(
            update.call_args.args[2]["nome"], "Nome atualizado"
        )
        if self.resource == "profissionais":
            self.assertEqual(
                update.call_args.args[2]["especialidade"],
                "Especialidade atualizada",
            )
        self.assertTrue(any("atualizado" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_delete_requires_explicit_checkbox_confirmation(self) -> None:
        record_id = int(self.record["id"])
        with self._environment(), patch.object(
            XanoClient,
            "list_records",
            side_effect=[
                [self.record],
                [self.record],
                [self.record],
                [],
            ],
        ), patch.object(XanoClient, "delete_record") as delete:
            page = self._run_page()
            delete_button = page.button(key=f"{self.prefix}_delete_{record_id}")
            self.assertTrue(delete_button.disabled)
            delete.assert_not_called()

            page.checkbox(key=f"{self.prefix}_delete_confirm_{record_id}").check()
            page.run()
            self.assertFalse(
                page.button(key=f"{self.prefix}_delete_{record_id}").disabled
            )
            page.button(key=f"{self.prefix}_delete_{record_id}").click()
            page.run()

        delete.assert_called_once_with(self.resource, record_id)
        self.assertTrue(any("excluído" in item.value for item in page.success))
        expected_empty = "Nenhum paciente" if self.resource == "pacientes" else "Nenhum profissional"
        self.assertTrue(any(expected_empty in item.value for item in page.info))
        self.assertEqual(len(page.exception), 0)

    def test_http_failure_is_visible_and_not_reported_as_empty_list(self) -> None:
        with self._environment(), patch.object(
            XanoClient,
            "list_records",
            side_effect=XanoHTTPError(500),
        ) as list_records:
            page = self._run_page()

        list_records.assert_called_once_with(self.resource)
        self.assertTrue(any("HTTP 500" in item.value for item in page.error))
        self.assertFalse(
            any("Nenhum" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

    def test_create_rate_limit_is_reported_without_retry(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[]
        ), patch.object(
            XanoClient,
            "create_record",
            side_effect=XanoHTTPError(429),
        ) as create:
            page = self._run_page()
            page.text_input(key=f"{self.prefix}_create_name").set_value("Nome")
            page.text_input(key=f"{self.prefix}_create_phone").set_value(
                "11999999999"
            )
            page.button(
                key=f"FormSubmitter:create_{self.prefix}-Cadastrar "
                + ("paciente" if self.resource == "pacientes" else "profissional")
            ).click()
            page.run()

        create.assert_called_once_with(
            self.resource,
            {
                "nome": "Nome",
                "telefone": "11999999999",
                "email": None,
                **(
                    {"especialidade": None}
                    if self.resource == "profissionais"
                    else {}
                ),
            },
        )
        self.assertTrue(any("HTTP 429" in item.value for item in page.error))
        self.assertTrue(
            any("consulte a listagem" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)


class PatientPageTests(CrudPageTests, unittest.TestCase):
    page_name = "1_Pacientes.py"
    resource = "pacientes"
    prefix = "patient"
    record = {
        "id": 11,
        "nome": "Paciente sintético",
        "telefone": "11999999999",
        "email": "patient@example.invalid",
    }


class ProfessionalPageTests(CrudPageTests, unittest.TestCase):
    page_name = "2_Profissionais.py"
    resource = "profissionais"
    prefix = "professional"
    record = {
        "id": 21,
        "nome": "Profissional sintético",
        "telefone": "11888888888",
        "email": "professional@example.invalid",
        "especialidade": "Especialidade textual",
    }

    def test_professional_specialties_writes_remain_disabled_by_default(self) -> None:
        with self._environment(), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "create_professional_specialty"
        ) as create_link, patch.object(
            XanoClient, "delete_professional_specialty"
        ) as delete_link:
            page = self._run_page()

        create_link.assert_not_called()
        delete_link.assert_not_called()
        self.assertTrue(
            any(
                "XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED=true"
                in item.value
                for item in page.warning
            )
        )
        self.assertEqual(len(page.exception), 0)

    def test_add_professional_specialty_is_simulated_and_cached_reload(self) -> None:
        specialty = {"id": 31, "nome": "Cardiologia"}
        created = {
            "id": 61,
            "profissional_id": 21,
            "especialidade_id": 31,
        }
        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "list_specialties", return_value=[specialty]
        ), patch.object(
            XanoClient, "list_professional_specialties", return_value=[]
        ), patch.object(
            XanoClient,
            "create_professional_specialty",
            return_value=created,
        ) as create_link, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.button(
                key="professional_specialty_create"
            ).click()
            page.run()

        create_link.assert_called_once_with(21, 31)
        clear_cache.assert_called_once_with()
        self.assertTrue(any("Vínculo criado" in item.value for item in page.success))
        self.assertEqual(len(page.exception), 0)

    def test_remove_professional_specialty_cancel_success_and_http_failure(
        self,
    ) -> None:
        specialty = {"id": 31, "nome": "Cardiologia"}
        association = {
            "id": 61,
            "profissional_id": 21,
            "especialidade_id": 31,
        }

        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "list_specialties", return_value=[specialty]
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=[association],
        ), patch.object(
            XanoClient, "delete_professional_specialty"
        ) as delete_link:
            page = self._run_page()
            delete_button = page.button(
                key="professional_specialty_delete_61"
            )
            self.assertTrue(delete_button.disabled)
            delete_link.assert_not_called()

        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "list_specialties", return_value=[specialty]
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=[association],
        ), patch.object(
            XanoClient, "delete_professional_specialty"
        ) as delete_link, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.checkbox(
                key="professional_specialty_delete_confirm_61"
            ).check()
            page.run()
            page.button(
                key="professional_specialty_delete_61"
            ).click()
            page.run()

        delete_link.assert_called_once_with(61)
        clear_cache.assert_called_once_with()
        self.assertTrue(
            any("Vínculo removido" in item.value for item in page.success)
        )
        self.assertEqual(len(page.exception), 0)

        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "list_specialties", return_value=[specialty]
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=[association],
        ), patch.object(
            XanoClient,
            "delete_professional_specialty",
            side_effect=XanoHTTPError(409),
        ) as delete_link, patch(
            "services.xano_cache.clear_xano_read_caches"
        ) as clear_cache:
            page = self._run_page()
            page.checkbox(
                key="professional_specialty_delete_confirm_61"
            ).check()
            page.run()
            page.button(
                key="professional_specialty_delete_61"
            ).click()
            page.run()

        delete_link.assert_called_once_with(61)
        clear_cache.assert_not_called()
        self.assertTrue(
            any("não foi possível remover" in item.value.lower() for item in page.error)
        )
        self.assertTrue(
            any("HTTP 409" in item.value for item in page.error)
        )
        self.assertEqual(len(page.exception), 0)

    def test_duplicate_and_invalid_professional_specialty_references_are_blocked(
        self,
    ) -> None:
        specialties = [
            {"id": 31, "nome": "Cardiologia"},
            {"id": 32, "nome": "Neurologia"},
        ]
        association_32 = {
            "id": 61,
            "profissional_id": 21,
            "especialidade_id": 32,
        }
        association_31 = {
            "id": 63,
            "profissional_id": 21,
            "especialidade_id": 31,
        }
        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient, "list_specialties", return_value=specialties
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=[association_32, association_31],
        ), patch.object(
            XanoClient, "create_professional_specialty"
        ) as create_link:
            page = self._run_page()

        create_link.assert_not_called()
        self.assertTrue(
            any(
                "Não há nova especialidade disponível"
                in item.value
                for item in page.info
            )
        )
        self.assertEqual(len(page.exception), 0)

        invalid_association = {
            "id": 62,
            "profissional_id": 999,
            "especialidade_id": 31,
        }
        with self._environment(
            relations_enabled="true",
            relation_writes="true",
        ), patch.object(
            XanoClient, "list_records", return_value=[self.record]
        ), patch.object(
            XanoClient,
            "list_specialties",
            return_value=[{"id": 31, "nome": "Cardiologia"}],
        ), patch.object(
            XanoClient,
            "list_professional_specialties",
            return_value=[invalid_association],
        ), patch.object(
            XanoClient, "create_professional_specialty"
        ) as create_link:
            page = self._run_page()

        create_link.assert_not_called()
        self.assertTrue(
            any("Nenhuma especialidade vinculada" in item.value for item in page.info)
        )
        self.assertEqual(len(page.exception), 0)

if __name__ == "__main__":
    unittest.main()
