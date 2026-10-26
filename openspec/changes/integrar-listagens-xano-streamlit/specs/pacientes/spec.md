## MODIFIED Requirements

### Requirement: Consultar pacientes

O sistema SHALL permitir listar pacientes cadastrados e consultar um paciente individualmente pelo identificador.

As respostas SHALL incluir somente os dados necessários ao consumidor da API:

- identificador;
- nome;
- telefone;
- e-mail.

Campos internos ou não destinados ao consumidor da API SHALL ser omitidos das respostas. Nesta Change, o frontend SHALL consumir somente a listagem por HTTP GET; a consulta individual permanece fora do escopo de implementação desta integração.

#### Scenario: Listar pacientes cadastrados

- **WHEN** uma solicitação GET válida pede a lista de pacientes
- **THEN** o sistema retorna os pacientes cadastrados com os campos básicos permitidos, incluindo uma lista vazia quando não houver registros

#### Scenario: Consultar paciente existente

- **WHEN** uma solicitação válida informa o identificador de um paciente existente
- **THEN** o sistema retorna os dados básicos permitidos daquele paciente

#### Scenario: Consultar paciente inexistente

- **WHEN** uma solicitação informa um identificador sem paciente correspondente
- **THEN** o sistema retorna um erro de não encontrado sem expor dados de outros pacientes

#### Scenario: Integrar somente a listagem no frontend

- **WHEN** esta Change carrega pacientes para a página Streamlit
- **THEN** usa exclusivamente o endpoint GET de coleção confirmado e mapeia `id`, `nome`, `telefone` e `email`, sem executar consulta individual ou operação de escrita
