# especialidades Specification

## Purpose

Define o comportamento observável para gerenciar o catálogo de especialidades médicas pela interface Streamlit e por APIs Xano confirmadas, preservando a integridade de vínculos existentes e o uso temporário do SQLite por Consultas.

## Requirements

### Requirement: Consultar especialidades

O sistema SHALL permitir listar especialidades e consultar uma especialidade individual por identificador usando o contrato confirmado da API Xano. Uma lista vazia SHALL ser tratada como resultado válido; falhas de transporte, resposta incompatível e registro inexistente SHALL ser informados como erros, sem simular sucesso ou recorrer ao SQLite.

#### Scenario: Listar especialidades existentes

- **WHEN** a API confirmada retorna uma lista de especialidades
- **THEN** a interface apresenta os registros retornados sem consultar diretamente o banco de dados

#### Scenario: Listar catálogo vazio

- **WHEN** a API confirmada retorna uma lista vazia
- **THEN** a interface informa que não há especialidades cadastradas, sem apresentar erro ou dados fictícios

#### Scenario: Consultar especialidade existente

- **WHEN** a pessoa solicita uma especialidade pelo identificador e a API confirma sua existência
- **THEN** o sistema apresenta os dados permitidos pelo contrato confirmado

#### Scenario: Consultar especialidade inexistente ou indisponível

- **WHEN** a API informa que o identificador não existe ou a consulta falha
- **THEN** a interface comunica a falha sem criar um registro, ocultar o erro ou apresentar dados locais como se fossem atuais

### Requirement: Cadastrar e editar especialidades

O sistema SHALL permitir cadastrar e editar o nome de uma especialidade por meio das operações confirmadas no Xano. O nome SHALL ser obrigatório e ter espaços externos removidos. Antes de gravar, o frontend SHALL rejeitar nomes equivalentes após trim e comparação sem distinção de caixa contra o catálogo carregado, preservando acentos. Respostas de erro do Xano SHALL ser apresentadas sem serem convertidas em sucesso. Essa validação do frontend não SHALL ser apresentada como garantia de unicidade concorrente do backend.

#### Scenario: Cadastrar nome válido

- **WHEN** uma pessoa envia um nome não vazio e ainda não cadastrado após normalização
- **THEN** o frontend envia somente o campo `nome` e informa sucesso somente após resposta HTTP de sucesso e registro compatível com `id` e `nome`

#### Scenario: Rejeitar nome vazio

- **WHEN** uma pessoa envia um nome vazio ou formado somente por espaços
- **THEN** o sistema informa a validação e não envia uma gravação inválida à API

#### Scenario: Rejeitar nome duplicado

- **WHEN** uma pessoa cadastra ou altera o nome para um valor equivalente a outro após trim e normalização sem distinção de caixa
- **THEN** o frontend bloqueia a gravação antes da chamada e informa a duplicidade com base no catálogo carregado

#### Scenario: O Xano rejeita cadastro ou edição

- **WHEN** a API rejeita uma gravação, inclusive por duplicidade ou referência
- **THEN** o sistema apresenta o erro HTTP e não informa sucesso

#### Scenario: Editar especialidade existente

- **WHEN** uma pessoa salva um nome válido para uma especialidade existente
- **THEN** o backend atualiza o registro identificado e a interface apresenta os dados atualizados

#### Scenario: Editar especialidade inexistente ou com falha

- **WHEN** a API informa que o identificador não existe ou a gravação falha
- **THEN** o sistema comunica o erro e não apresenta a alteração como concluída

### Requirement: Excluir especialidade com confirmação explícita

O frontend SHALL enviar DELETE somente para o identificador selecionado após confirmação explícita. Em caso de erro HTTP, inclusive conflito por referência, SHALL informar a falha sem apresentar sucesso. Um teste remoto de exclusão SHALL usar exclusivamente um registro fictício criado para esse teste; os testes automatizados locais SHALL usar mocks e não SHALL excluir registros remotos.

#### Scenario: Excluir especialidade fictícia de teste

- **WHEN** a pessoa confirma a exclusão de uma especialidade fictícia criada especificamente para o teste remoto e o Xano responde com sucesso
- **THEN** a interface informa a exclusão e atualiza o catálogo

#### Scenario: API bloqueia exclusão

- **WHEN** a pessoa confirma a exclusão e o Xano rejeita a operação, por exemplo por referência
- **THEN** a interface apresenta o erro e não informa sucesso

#### Scenario: Cancelar ou não confirmar exclusão

- **WHEN** a pessoa não confirma a exclusão
- **THEN** nenhuma solicitação de exclusão é enviada

#### Scenario: Preservar registros existentes durante testes remotos

- **WHEN** uma validação remota de escrita é executada
- **THEN** somente o registro fictício criado para esse fim pode ser alterado ou excluído; registros preexistentes não são usados como dados de teste

### Requirement: Usar a integração Xano autorizada

O frontend SHALL consumir Especialidades somente pelas rotas informadas e autorizadas pelo usuário: GET/POST `/especialidade` e GET/PATCH/DELETE `/especialidade/{especialidade_id}`. A base URL SHALL ser sobrescrevível por configuração externa. A integração ficará habilitada por padrão e poderá ser desabilitada pelas flags do módulo. A indicação `Public` não SHALL ser interpretada como prova de controles de segurança; esta Change não altera a segurança no Xano nem adiciona autenticação. Especialidades não SHALL usar SQLite como fallback.

#### Scenario: Operar com integração habilitada

- **WHEN** a página é acessada com a integração habilitada
- **THEN** as operações de Especialidades usam somente as APIs confirmadas e apresentam as respostas ou erros reais

#### Scenario: Integração desabilitada ou configuração ausente

- **WHEN** a integração está desabilitada ou a configuração externa é inválida
- **THEN** a interface informa a pendência e não envia requisições nem apresenta sucesso simulado

#### Scenario: Falha HTTP ou resposta incompatível

- **WHEN** uma operação recebe erro HTTP, falha de transporte ou resposta incompatível com o contrato
- **THEN** o erro é apresentado explicitamente e não é convertido em lista vazia ou sucesso

### Requirement: Preservar o escopo desta etapa

O gerenciamento de Especialidades SHALL NOT exigir login nem implementar autenticação ou separação de permissões Admin/Médico nesta etapa. A validação da interface SHALL NOT ser tratada como autorização do backend. A migração de Especialidades SHALL NOT remover a inicialização, o serviço ou o arquivo SQLite enquanto Consultas dependerem deles.

#### Scenario: Usar o módulo sem implementar perfis

- **WHEN** uma pessoa acessa a funcionalidade de Especialidades nesta etapa
- **THEN** a interface não solicita login nem apresenta uma separação de capacidades Admin/Médico como mecanismo de segurança

#### Scenario: Consultas ainda dependem do SQLite

- **WHEN** Especialidades passa a consumir APIs Xano
- **THEN** o serviço e a inicialização SQLite necessários a Consultas permanecem disponíveis e a migração de Especialidades não altera o arquivo de dados local
