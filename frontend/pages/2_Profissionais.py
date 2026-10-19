import streamlit as st

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

st.dataframe(
    {"ID": [], "Nome": [], "Especialidade": []},
    hide_index=True,
    use_container_width=True,
    height=220,
)
st.info("Integração futura com Xano ainda não disponível.")
