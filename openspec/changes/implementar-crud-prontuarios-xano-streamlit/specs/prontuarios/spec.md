## Purpose

Define um MVP acadêmico de gerenciamento de Prontuários por APIs Xano
confirmadas, sem SQLite, autenticação ou Registro de Atendimento nesta Change.

## ADDED Requirements

### Requirement: Consultar Prontuários

O sistema SHALL consultar Prontuários somente pelas rotas confirmadas
`GET /prontuario` e `GET /prontuario/{prontuario_id}`.

Uma coleção vazia SHALL ser apresentada como vazia. Erros HTTP, transporte,
registro inexistente e respostas incompatíveis SHALL ser apresentados como
falha sem fallback SQLite.

#### Scenario: Listar Prontuários existentes

- **WHEN** a API habilitada retorna uma coleção compatível
- **THEN** a interface apresenta os registros permitidos pelo contrato

#### Scenario: Coleção vazia

- **WHEN** a API retorna uma lista vazia
- **THEN** a interface informa que não há Prontuários cadastrados

#### Scenario: Consultar Prontuário por identificador

- **WHEN** a pessoa solicita um identificador inteiro positivo existente
- **THEN** o sistema consulta o GET individual e apresenta o registro recebido

#### Scenario: Registro inexistente ou consulta indisponível

- **WHEN** o identificador não existe ou a API falha
- **THEN** o sistema apresenta não encontrado ou erro sem criar registro local

### Requirement: Cadastrar e editar Prontuários

A interface SHALL cadastrar e editar Prontuários pelas operações confirmadas
POST `/prontuario` e PATCH `/prontuario/{prontuario_id}`.

Os payloads SHALL conter somente campos confirmados pelo contrato. Paciente e
Profissional SHALL ser representados por IDs positivos presentes nos catálogos
carregados. O sistema SHALL NOT declarar obrigatoriedade física ou unicidade
não confirmadas pelo backend.

#### Scenario: Cadastrar Prontuário válido

- **WHEN** uma pessoa envia paciente e profissional existentes, com os campos
  opcionais compatíveis
- **THEN** o sistema envia o POST somente com escrita habilitada e apresenta
  sucesso somente após resposta compatível

#### Scenario: Rejeitar referência inválida

- **WHEN** paciente ou profissional não existe nos catálogos carregados
- **THEN** o sistema não envia o POST ou PATCH e informa a referência inválida

#### Scenario: Editar Prontuário existente

- **WHEN** uma pessoa altera campos compatíveis de um Prontuário existente
- **THEN** o sistema envia PATCH parcial somente com os campos alterados

#### Scenario: Xano rejeita cadastro ou edição

- **WHEN** a API rejeita POST ou PATCH
- **THEN** o sistema apresenta o erro HTTP sem declarar sucesso

### Requirement: Excluir Prontuários com confirmação

O frontend SHALL enviar DELETE somente após confirmação explícita e escrita
habilitada, usando o identificador inteiro selecionado.

#### Scenario: Cancelar exclusão

- **WHEN** a pessoa não confirma a exclusão
- **THEN** nenhuma operação DELETE é enviada

#### Scenario: Excluir Prontuário existente

- **WHEN** a pessoa confirma a exclusão e o Xano responde com sucesso compatível
- **THEN** o sistema informa sucesso e atualiza a coleção

#### Scenario: API bloqueia exclusão

- **WHEN** o Xano rejeita DELETE por referência ou outro erro
- **THEN** o sistema apresenta a falha sem declarar sucesso

### Requirement: Proteger o escopo desta Change

O MVP SHALL NOT implementar Registro de Atendimento, autenticação, perfis,
autoria clínica derivada de sessão ou autorização por perfil.

O frontend SHALL NOT depender do SQLite nem usar dados locais como alternativa
ao Xano.

#### Scenario: Acessar Prontuários sem autenticação

- **WHEN** a página é acessada nesta Change
- **THEN** ela não afirma que há login ou controle de acesso implementado

#### Scenario: Operação remota desabilitada

- **WHEN** a escrita ou a integração está desabilitada
- **THEN** os controles remotos ficam indisponíveis e nenhuma mutação é enviada

#### Scenario: Dados clínicos não confirmados

- **WHEN** o contrato não fornece uma entidade ou campos de Registro de
  Atendimento
- **THEN** o sistema não cria página, endpoint ou campo fictício para eles
