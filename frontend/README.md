# Frontend Streamlit

## Requisitos

- Python 3.12 (versão verificada: 3.12.4)

## Executar localmente

Na raiz do repositório, crie e ative um ambiente virtual:

```powershell
python -m venv frontend/.venv
.\frontend\.venv\Scripts\Activate.ps1
```

Instale as dependências e inicie a aplicação:

```powershell
python -m pip install -r frontend/requirements.txt
python -m streamlit run frontend/app.py
```

Esta versão apresenta somente a estrutura e a navegação. As páginas não fazem chamadas HTTP ao Xano e não precisam de URL ou credenciais configuradas.
