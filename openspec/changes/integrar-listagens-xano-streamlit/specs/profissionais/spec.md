## MODIFIED Requirements

### Requirement: Consultar profissionais

O sistema SHALL permitir listar profissionais cadastrados e consultar um profissional individualmente pelo identificador.

As respostas SHALL incluir somente os campos destinados ao consumidor da API: identificador, nome, telefone, e-mail e especialidade.

Campos internos ou não destinados ao consumidor SHALL ser omitidos. Nesta Change, o frontend SHALL consumir somente a listagem por HTTP GET e SHALL preservar `especialidade` como texto retornado pelo endpoint, sem implementar catálogo ou relacionamento.

#### Scenario: Listar profissionais cadastrados

- **WHEN** uma solicitação GET válida pede a lista de profissionais
- **THEN** o sistema retorna os profissionais cadastrados com os campos permitidos, incluindo uma lista vazia quando não houver registros

#### Scenario: Consultar profissional existente

- **WHEN** uma solicitação válida informa o identificador de um profissional existente
- **THEN** o sistema retorna os dados permitidos daquele profissional

#### Scenario: Consultar profissional inexistente

- **WHEN** uma solicitação informa um identificador sem profissional correspondente
- **THEN** o sistema retorna erro de não encontrado sem expor dados de outros profissionais

#### Scenario: Integrar somente a listagem no frontend

- **WHEN** esta Change carrega profissionais para a página Streamlit
- **THEN** usa exclusivamente o endpoint GET de coleção confirmado e mapeia `id`, `nome`, `telefone`, `email` e `especialidade` textual, sem executar consulta individual ou operação de escrita
