import os

import streamlit as st

from services.listagens import (
    ConfiguracaoAusenteError,
    ErroHttpError,
    ErroTransporteError,
    ListagemError,
    RespostaInvalidaError,
    XANO_PACIENTES_URL_ENV,
    integracao_habilitada,
    invalidar_cache_pacientes,
    listar_pacientes,
)
from ui import apply_styles, show_page_header


apply_styles()
show_page_header(
    "Pacientes",
    "Consulte e organize as informações dos pacientes do consultório.",
    "👥",
)

search_column, button_column = st.columns([3, 1])
with search_column:
    st.text_input(
        "Buscar paciente",
        placeholder="Busca disponível após a integração",
        disabled=True,
    )
with button_column:
    st.write("")
    st.button(
        "Novo paciente",
        icon=":material/person_add:",
        disabled=True,
        use_container_width=True,
    )
    atualizar = st.button(
        "Atualizar",
        icon=":material/refresh:",
        use_container_width=True,
    )

if atualizar:
    invalidar_cache_pacientes()

carregamento_concluido = False
if not integracao_habilitada():
    st.warning(
        "Integração com Xano desabilitada. Ela permanecerá bloqueada até a "
        "verificação de segurança e autorização explícita."
    )
    pacientes = []
else:
    try:
        with st.spinner("Carregando pacientes..."):
            pacientes = listar_pacientes(os.getenv(XANO_PACIENTES_URL_ENV))
        carregamento_concluido = True
    except ConfiguracaoAusenteError as erro:
        st.warning(str(erro))
        pacientes = []
    except ErroHttpError as erro:
        st.error(f"Não foi possível carregar pacientes: {erro}")
        pacientes = []
    except ErroTransporteError as erro:
        st.error(f"Não foi possível carregar pacientes: {erro}")
        pacientes = []
    except RespostaInvalidaError as erro:
        st.error(f"A resposta de pacientes é inesperada: {erro}")
        pacientes = []
    except ListagemError as erro:
        st.error(f"Não foi possível carregar pacientes: {erro}")
        pacientes = []

if carregamento_concluido and not pacientes:
    st.info("Nenhum paciente cadastrado.")

st.dataframe(
    {
        "ID": [paciente["id"] for paciente in pacientes],
        "Nome": [paciente["nome"] for paciente in pacientes],
        "Telefone": [paciente["telefone"] for paciente in pacientes],
        "E-mail": [paciente["email"] for paciente in pacientes],
    },
    hide_index=True,
    use_container_width=True,
    height=220,
)
