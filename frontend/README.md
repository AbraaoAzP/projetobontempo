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
python -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8502
```

O servidor fica limitado à máquina local e não escuta na rede.

## Configuração das listagens

O cliente HTTP somente GET existente continua disponível para uma integração futura,
mas as páginas deste MVP usam exclusivamente o modo de demonstração SQLite. O modo
local não lê as URLs de Xano e não faz requisições HTTP.

O modo de demonstração é identificado na barra lateral. Os dados são salvos em
`frontend/data/bontempo_demo.sqlite3`, arquivo ignorado pelo Git.

Use o botão **Carregar exemplos fictícios** para inserir registros sintéticos.
Essa ação só funciona quando as tabelas funcionais estão vazias; em bancos com
dados, a operação é recusada e nenhum registro existente é substituído.

O cliente Xano permanece desabilitado por padrão. Não defina
`XANO_LISTAGENS_ENABLED=true` para esta demonstração. Uma habilitação futura
depende de revisão de segurança e autorização próprias; configurar URLs não
ativa as páginas SQLite como consumidoras do Xano.

Consultas usam `America/Sao_Paulo` como fuso da interface e persistem instantes
em UTC. Agendamentos e confirmações ocupam horário; intervalos adjacentes são
permitidos e consultas canceladas/realizadas/não comparecidas liberam o horário.

## Testes

Execute os testes locais SQLite e os testes do cliente HTTP com transporte
simulado, a partir da pasta `frontend`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes não enviam requisições à rede e usam somente registros sintéticos.
