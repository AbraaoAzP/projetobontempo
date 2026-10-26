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

## Configuração das listagens

As URLs completas são fornecidas por configuração externa:

- `XANO_PACIENTES_URL`
- `XANO_PROFISSIONAIS_URL`

As páginas leem essas configurações do ambiente do processo. Não coloque URLs
operacionais, credenciais ou tokens no código versionado.

As chamadas ao Xano ficam desabilitadas por padrão. Não basta configurar as
URLs para ativá-las. A variável `XANO_LISTAGENS_ENABLED` deve permanecer ausente
ou diferente de `true` até que o grupo confirme que os registros são
exclusivamente fictícios, verifique que o acesso aos endpoints está
adequadamente restrito e autorize explicitamente a habilitação. Esse sinalizador
é somente uma trava operacional do frontend; não substitui controles de acesso
no Xano nem comprova que eles existem.

Somente depois dessas verificações e autorização, a execução poderá receber
`XANO_LISTAGENS_ENABLED=true` junto das duas URLs. Em PowerShell, configure
valores aprovados para o ambiente antes de iniciar o Streamlit:

```powershell
$env:XANO_PACIENTES_URL = "<URL GET aprovada para pacientes>"
$env:XANO_PROFISSIONAIS_URL = "<URL GET aprovada para profissionais>"
$env:XANO_LISTAGENS_ENABLED = "true"
python -m streamlit run frontend/app.py
```

Não use endpoints reais enquanto a verificação de segurança estiver pendente.

Quando habilitada, cada listagem usa exclusivamente GET, tem timeout de cinco
segundos e cache de até 60 segundos. O botão “Atualizar” solicita nova leitura
e invalida apenas o cache da página correspondente. Cadastro e busca continuam
desabilitados. Erros de configuração, HTTP, conexão, timeout ou formato são
apresentados sem dados de fallback.

## Testes

Execute os testes com transporte HTTP simulado, a partir da pasta `frontend`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes não enviam requisições à rede e usam somente registros sintéticos.
