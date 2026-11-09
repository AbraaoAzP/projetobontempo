import streamlit as st

from services.xano import (
    XanoClient,
    XanoError,
    XanoSettings,
    specialties_api_enabled,
)
from ui import apply_styles, show_page_header


apply_styles()
show_page_header(
    "Especialidades",
    "Consulta o catálogo Xano; gravações aguardam verificação de autorização.",
    ":material/medical_information:",
)

if specialties_api_enabled():
    client = XanoClient(XanoSettings.from_environment())
    try:
        response = client.list_specialties()
    except XanoError as error:
        st.error(f"Não foi possível consultar Especialidades no Xano: {error}")
    else:
        st.subheader("Resposta da API")
        st.caption(
            "Corpo bruto temporário; nenhum formato de resposta foi presumido."
        )
        st.code(response.text, language="json")
else:
    st.info(
        "A leitura do catálogo Xano está desabilitada. Defina "
        "XANO_ESPECIALIDADES_API_ENABLED=true somente após confirmar o "
        "destino e a política de acesso."
    )

st.caption(
    "Cadastro, edição e exclusão permanecem indisponíveis até confirmar os "
    "formatos de resposta, as regras de validação e os controles de autorização."
)
st.warning(
    "Consultas continua usando o catálogo SQLite local. Este módulo não consulta "
    "nem atualiza esse catálogo, e não há sincronização com o Xano."
)
