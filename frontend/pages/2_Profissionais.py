import os

import streamlit as st

from services.listagens import (
    ConfiguracaoAusenteError,
    ErroHttpError,
    ErroTransporteError,
    ListagemError,
    RespostaInvalidaError,
    XANO_PROFISSIONAIS_URL_ENV,
    integracao_habilitada,
    invalidar_cache_profissionais,
    listar_profissionais,
)
from ui import apply_styles, show_page_header


apply_styles()
show_page_header(
    "Profissionais",
    "Consulte os profissionais e suas áreas de atuação no consultório.",
    "🩺",
)

search_column, button_column = st.columns([3, 1])
with search_column:
    st.text_input(
        "Buscar profissional",
        placeholder="Busca disponível após a integração",
        disabled=True,
    )
with button_column:
    st.write("")
    st.button(
        "Novo profissional",
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
    invalidar_cache_profissionais()

carregamento_concluido = False
if not integracao_habilitada():
    st.warning(
        "Integração com Xano desabilitada. Ela permanecerá bloqueada até a "
        "verificação de segurança e autorização explícita."
    )
    profissionais = []
else:
    try:
        with st.spinner("Carregando profissionais..."):
            profissionais = listar_profissionais(os.getenv(XANO_PROFISSIONAIS_URL_ENV))
        carregamento_concluido = True
    except ConfiguracaoAusenteError as erro:
        st.warning(str(erro))
        profissionais = []
    except ErroHttpError as erro:
        st.error(f"Não foi possível carregar profissionais: {erro}")
        profissionais = []
    except ErroTransporteError as erro:
        st.error(f"Não foi possível carregar profissionais: {erro}")
        profissionais = []
    except RespostaInvalidaError as erro:
        st.error(f"A resposta de profissionais é inesperada: {erro}")
        profissionais = []
    except ListagemError as erro:
        st.error(f"Não foi possível carregar profissionais: {erro}")
        profissionais = []

if carregamento_concluido and not profissionais:
    st.info("Nenhum profissional cadastrado.")

st.dataframe(
    {
        "ID": [profissional["id"] for profissional in profissionais],
        "Nome": [profissional["nome"] for profissional in profissionais],
        "Especialidade": [
            profissional["especialidade"] for profissional in profissionais
        ],
    },
    hide_index=True,
    use_container_width=True,
    height=220,
)
