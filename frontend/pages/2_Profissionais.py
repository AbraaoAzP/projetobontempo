import streamlit as st


st.markdown(
    """
    <style>
        .stApp {
            background-color: #f3f8fb;
            color: #123b52;
        }
        h1, h2, h3 {
            color: #0f4c81;
        }
        .card {
            background: #ffffff;
            border: 1px solid #dfeaf3;
            border-radius: 16px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 4px 14px rgba(15, 76, 129, 0.08);
            margin-top: 1rem;
        }
        .card-title {
            color: #0f4c81;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }
        .card-text {
            color: #3d5d72;
            line-height: 1.7;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("Profissionais")
st.markdown(
    """
    <div class='card'>
        <div class='card-title'>Módulo de profissionais</div>
        <div class='card-text'>
            Esta área será desenvolvida em uma etapa futura. O objetivo será organizar o cadastro e a gestão
            dos profissionais, respeitando as regras e os módulos do consultório em evolução.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
