from typing import Any

import streamlit as st

from services.database import (
    DemoDataRequiresEmptyDatabaseError,
    initialize_database,
    seed_demo_data,
)
from services import dashboard as dashboard_service
from services.dashboard import DashboardDataError, Metric
from ui import apply_styles, show_page_header


st.set_page_config(
    page_title="Sistema de Gestão de Consultório",
    page_icon=":hospital:",
    layout="wide",
)

apply_styles()


@st.cache_resource
def setup_local_database() -> None:
    initialize_database()


setup_local_database()

st.sidebar.info(
    "Modo demonstração local · SQLite\n\n"
    "Os dados são armazenados neste computador. A integração GET com Xano "
    "não é usada neste modo."
)
if st.sidebar.button("Carregar exemplos fictícios", use_container_width=True):
    try:
        inserted = seed_demo_data()
        st.sidebar.success(f"{inserted} registros de demonstração criados.")
    except DemoDataRequiresEmptyDatabaseError as error:
        st.sidebar.warning(str(error))


def show_home() -> None:
    show_page_header(
        "Visão administrativa",
        "Acompanhe os indicadores do consultório e acesse os módulos de gestão.",
        "🏥",
    )

    dashboard_data = None
    with st.spinner("Carregando indicadores..."):
        try:
            dashboard_data = dashboard_service.load_dashboard()
        except DashboardDataError as error:
            st.error(str(error))

    st.caption(
        "Consultas: dados do SQLite local, não sincronizados com o Xano. "
        "Os demais totais dependem de APIs Xano configuradas e autorizadas."
    )
    if dashboard_data is not None:
        metric_columns = st.columns(4)
        _show_metric(metric_columns[0], "Pacientes", dashboard_data.patients)
        _show_metric(
            metric_columns[1], "Profissionais", dashboard_data.professionals
        )
        _show_metric(
            metric_columns[2], "Especialidades", dashboard_data.specialties
        )
        with metric_columns[3].container(border=True):
            st.metric("Consultas", dashboard_data.consultations.total)
            st.caption("SQLite local · não sincronizado")

        with st.container(border=True):
            st.metric(
                "Consultas do dia",
                dashboard_data.consultations.today,
                help="Todas as consultas com início na data de hoje, no fuso de São Paulo.",
            )
            st.caption("Fonte: SQLite local · não sincronizado")

        left, right = st.columns(2)
        with left, st.container(border=True):
            st.subheader("Consultas por status")
            status_counts = dashboard_data.consultations.status_counts
            if sum(status_counts.values()):
                st.bar_chart(status_counts)
            else:
                st.info("Nenhuma consulta local cadastrada.")

        with right, st.container(border=True):
            st.subheader("Agenda · próximos 7 dias")
            daily_counts = dashboard_data.consultations.next_seven_days
            if sum(daily_counts.values()):
                st.bar_chart(daily_counts)
            else:
                st.info("Nenhuma consulta local nos próximos 7 dias.")

        with st.container(border=True):
            st.subheader("Próximas consultas")
            st.caption(
                "Agenda local. Dados pessoais e observações clínicas não são exibidos."
            )
            if dashboard_data.consultations.upcoming:
                st.dataframe(
                    dashboard_data.consultations.upcoming,
                    hide_index=True,
                    width="stretch",
                )
            else:
                st.info("Não há próximas consultas ativas na base local.")

    st.divider()
    st.subheader("Acesso rápido")
    columns = st.columns(2)
    for column, page, title, description, icon in (
        (
            columns[0],
            patients_page,
            "Pacientes",
            "Gestão de pacientes · integração Xano.",
            ":material/groups:",
        ),
        (
            columns[1],
            professionals_page,
            "Profissionais",
            "Gestão de profissionais · integração Xano.",
            ":material/medical_services:",
        ),
        (
            columns[0],
            specialties_page,
            "Especialidades",
            "Integração Xano ainda indisponível.",
            ":material/medical_information:",
        ),
        (
            columns[1],
            appointments_page,
            "Consultas",
            "Agenda local SQLite; integração Xano pendente.",
            ":material/calendar_month:",
        ),
    ):
        with column, st.container(border=True):
            st.subheader(title)
            st.write(description)
            st.page_link(page, label=f"Abrir {title.lower()}", icon=icon)

    with st.container(border=True):
        st.caption("Ambiente local de demonstração. Nenhuma alteração é enviada ao Xano.")


def _show_metric(column: Any, title: str, metric: Metric) -> None:
    with column.container(border=True):
        value = metric.value if metric.value is not None else "Indisponível"
        st.metric(title, value)
        if metric.message:
            if metric.state == "error":
                st.error(metric.message)
            else:
                st.caption(metric.message)


patients_page = st.Page("pages/1_Pacientes.py", title="Pacientes", icon=":material/groups:")
professionals_page = st.Page(
    "pages/2_Profissionais.py",
    title="Profissionais",
    icon=":material/medical_services:",
)
specialties_page = st.Page(
    "pages/3_Especialidades.py",
    title="Especialidades",
    icon=":material/medical_information:",
)
appointments_page = st.Page(
    "pages/4_Consultas.py",
    title="Consultas",
    icon=":material/calendar_month:",
)
pages = [
    st.Page(show_home, title="Início", icon=":material/home:", default=True),
    patients_page,
    professionals_page,
    specialties_page,
    appointments_page,
]

st.navigation(pages, position="sidebar").run()
