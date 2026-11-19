import os
import unittest
from datetime import date, datetime, time
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from services import dashboard
from services.xano_cache import clear_xano_read_caches
from services.xano import XanoHTTPError
from streamlit.testing.v1 import AppTest


LOCAL_TZ = ZoneInfo("America/Sao_Paulo")
STATUSES = [
    {"codigo": "agendada", "nome": "Agendada"},
    {"codigo": "confirmada", "nome": "Confirmada"},
    {"codigo": "realizada", "nome": "Realizada"},
    {"codigo": "cancelada", "nome": "Cancelada"},
    {"codigo": "nao_compareceu", "nome": "Não compareceu"},
]
FRONTEND = Path(__file__).resolve().parents[1]


class DashboardServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_xano_read_caches()

    def tearDown(self) -> None:
        clear_xano_read_caches()

    def test_load_dashboard_reads_xano_consultations(self) -> None:
        environment = {
            "XANO_CONSULTAS_API_ENABLED": "true",
            "XANO_CONSULTAS_BASE_URL": "https://consultations.example.invalid/api",
            "XANO_STATUS_CONSULTA_API_ENABLED": "true",
            "XANO_STATUS_CONSULTA_BASE_URL": "https://statuses.example.invalid/api",
        }
        appointments = [
            {
                "id": 1,
                "paciente_id": 11,
                "profissional_id": 21,
                "especialidade_id": 31,
                "data_e_hora_do_agendamento": 1898780400000,
                "status_consulta_id": 41,
                "observacoes": None,
            }
        ]
        statuses = [{"id": 41, "nome": "Agendada", "created_at": 1}]

        with patch.dict(os.environ, environment, clear=True), patch(
            "services.dashboard.load_consultations",
            return_value=appointments,
        ), patch(
            "services.dashboard.load_consultation_statuses",
            return_value=statuses,
        ):
            data = dashboard.load_dashboard(
                today=date(2030, 5, 20),
                now=datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
            )

        self.assertEqual(data.consultations.state, "available")
        self.assertEqual(data.consultations.total, 1)
        self.assertEqual(data.consultations.status_counts["Agendada"], 1)

    def test_summarizes_local_consultations_without_personal_data(self) -> None:
        appointments = [
            {
                "inicio_em": "2030-05-20T09:00:00-03:00",
                "status_codigo": "agendada",
                "status_nome": "Agendada",
                "paciente_nome": "Nome que não deve aparecer",
            },
            {
                "inicio_em": "2030-05-20T10:00:00-03:00",
                "status_codigo": "cancelada",
                "status_nome": "Cancelada",
                "paciente_nome": "Outro nome privado",
            },
            {
                "inicio_em": "2030-05-21T08:30:00-03:00",
                "status_codigo": "confirmada",
                "status_nome": "Confirmada",
            },
            {
                "inicio_em": "2030-05-20T07:00:00-03:00",
                "status_codigo": "realizada",
                "status_nome": "Realizada",
            },
        ]

        summary = dashboard.build_consultation_summary(
            appointments,
            STATUSES,
            date(2030, 5, 20),
            datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
        )

        self.assertEqual(summary.total, 4)
        self.assertEqual(summary.today, 3)
        self.assertEqual(
            summary.status_counts,
            {
                "Agendada": 1,
                "Confirmada": 1,
                "Realizada": 1,
                "Cancelada": 1,
                "Não compareceu": 0,
            },
        )
        self.assertEqual(summary.next_seven_days["20/05"], 3)
        self.assertEqual(summary.next_seven_days["21/05"], 1)
        self.assertEqual(
            summary.upcoming,
            [
                {"Data": "20/05/2030", "Horário": "09:00", "Status": "Agendada"},
                {
                    "Data": "21/05/2030",
                    "Horário": "08:30",
                    "Status": "Confirmada",
                },
            ],
        )
        self.assertNotIn("paciente_nome", str(summary.upcoming))
        self.assertNotIn("Nome que não deve aparecer", str(summary.upcoming))

    def test_empty_consultations_produce_zero_counts_and_empty_schedule(self) -> None:
        summary = dashboard.build_consultation_summary(
            [],
            STATUSES,
            date(2030, 5, 20),
            datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
        )

        self.assertEqual(summary.total, 0)
        self.assertEqual(summary.today, 0)
        self.assertTrue(all(value == 0 for value in summary.status_counts.values()))
        self.assertTrue(all(value == 0 for value in summary.next_seven_days.values()))
        self.assertEqual(summary.upcoming, [])

    def test_xano_counts_stay_unavailable_without_explicit_authorized_config(self) -> None:
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("XANO_")
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(
            dashboard.XanoClient, "list_records"
        ) as list_records, patch(
            "services.dashboard.load_consultations"
        ) as list_consultations:
            data = dashboard.load_dashboard(
                today=date(2030, 5, 20),
                now=datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
            )

        list_records.assert_not_called()
        list_consultations.assert_not_called()
        self.assertEqual(data.patients.state, "unavailable")
        self.assertEqual(data.professionals.state, "unavailable")
        self.assertEqual(data.specialties.state, "unavailable")
        self.assertEqual(data.consultations.total, 0)

    def test_xano_counts_use_only_configured_resources_and_report_failures(self) -> None:
        environment = {
            "XANO_API_ENABLED": "true",
            "XANO_PACIENTES_BASE_URL": "https://patients.example.invalid/api",
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(
            dashboard.XanoClient,
            "list_records",
            side_effect=[[{"id": 1}, {"id": 2}], XanoHTTPError(403)],
        ) as list_records:
            data = dashboard.load_dashboard(
                today=date(2030, 5, 20),
                now=datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
            )

        self.assertEqual(data.patients.value, 2)
        self.assertEqual(data.patients.state, "available")
        self.assertEqual(data.professionals.state, "unavailable")
        self.assertEqual(data.specialties.state, "unavailable")
        self.assertEqual(list_records.call_args_list[0].args, ("pacientes",))
        self.assertEqual(list_records.call_count, 1)

        clear_xano_read_caches()
        with patch.dict(
            os.environ,
            {
                **environment,
                "XANO_PROFISSIONAIS_BASE_URL": "https://professionals.example.invalid/api",
            },
            clear=True,
        ), patch.object(
            dashboard.XanoClient,
            "list_records",
            side_effect=[[], XanoHTTPError(403)],
        ):
            failed_data = dashboard.load_dashboard(
                today=date(2030, 5, 20),
                now=datetime(2030, 5, 20, 8, 0, tzinfo=LOCAL_TZ),
            )

        self.assertEqual(failed_data.patients.value, 0)
        self.assertEqual(failed_data.professionals.state, "error")
        self.assertIn("HTTP 403", failed_data.professionals.message or "")

    def test_dashboard_renders_consultations_without_names_or_http(self) -> None:
        synthetic_data = dashboard.DashboardData(
            patients=dashboard.Metric(
                None, "unavailable", "Xano", "A URL da API não está configurada."
            ),
            professionals=dashboard.Metric(
                None, "error", "Xano", "Falha ao consultar o Xano: HTTP 403."
            ),
            specialties=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            consultations=dashboard.ConsultationSummary(
                total=1,
                today=1,
                status_counts={"Agendada": 1},
                next_seven_days={"09/11": 1},
                upcoming=[
                    {
                        "Data": "09/11/2026",
                        "Horário": "14:00",
                        "Status": "Agendada",
                    }
                ],
            ),
        )
        with patch.object(
            dashboard, "load_dashboard", return_value=synthetic_data
        ), patch("requests.Session.request") as request:
            page = AppTest.from_file(
                str(FRONTEND / "app.py"), default_timeout=30
            ).run()

        request.assert_not_called()
        self.assertEqual(len(page.exception), 0)
        self.assertTrue(any("APIs Xano" in item.value for item in page.caption))
        self.assertTrue(any("HTTP 403" in item.value for item in page.error))
        self.assertTrue(any("Próximas consultas" in item.value for item in page.subheader))
        self.assertTrue(any("Especialidades" in item.value for item in page.subheader))
        self.assertEqual(len(page.page_link), 4)
        self.assertNotIn("nome", str(page.dataframe[0].value).lower())
        self.assertNotIn("paciente", str(page.dataframe[0].value).lower())

    def test_dashboard_shows_empty_states_without_consultation_samples(self) -> None:
        empty_data = dashboard.DashboardData(
            patients=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            professionals=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            specialties=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            consultations=dashboard.ConsultationSummary(
                total=0,
                today=0,
                status_counts={"Agendada": 0, "Confirmada": 0},
                next_seven_days={"09/11": 0, "10/11": 0},
                upcoming=[],
            ),
        )
        with patch.object(dashboard, "load_dashboard", return_value=empty_data):
            page = AppTest.from_file(
                str(FRONTEND / "app.py"), default_timeout=10
            ).run()

        self.assertEqual(len(page.exception), 0)
        self.assertTrue(
            any("Nenhuma consulta cadastrada no Xano" in item.value for item in page.info)
        )
        self.assertTrue(
            any("Não há próximas consultas ativas no Xano" in item.value for item in page.info)
        )

    def test_dashboard_accepts_consultation_summary_without_status_attributes(self) -> None:
        class LegacyConsultationSummary:
            total = 1
            today = 1
            status_counts = {"Agendada": 1}
            next_seven_days = {"09/11": 1}
            upcoming = [
                {
                    "Data": "09/11/2026",
                    "Horário": "14:00",
                    "Status": "Agendada",
                }
            ]

        legacy_data = dashboard.DashboardData(
            patients=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            professionals=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            specialties=dashboard.Metric(
                None, "unavailable", "Xano", "Integração indisponível."
            ),
            consultations=LegacyConsultationSummary(),
        )
        with patch.object(dashboard, "load_dashboard", return_value=legacy_data):
            page = AppTest.from_file(
                str(FRONTEND / "app.py"), default_timeout=10
            ).run()

        self.assertEqual(len(page.exception), 0)
        consult_metrics = [
            metric for metric in page.metric
            if metric.label in {"Consultas", "Consultas do dia"}
        ]
        self.assertTrue(
            any(metric.value == "1" for metric in consult_metrics)
        )


if __name__ == "__main__":
    unittest.main()
