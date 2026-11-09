## Purpose

Define o comportamento observável para gerenciar o catálogo de especialidades médicas pela interface Streamlit e por APIs Xano confirmadas, preservando a integridade de vínculos existentes e o uso temporário do SQLite por Consultas.

## ADDED Requirements

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

O sistema SHALL permitir cadastrar e editar o nome de uma especialidade por meio das operações confirmadas no Xano. O nome SHALL ser obrigatório, ter espaços externos removidos e ser único após normalização sem distinção de caixa, preservando acentos. O backend SHALL aplicar a unicidade e rejeitar entradas inválidas sem persistência parcial. O mapeamento entre o modelo local conhecido e os campos de API SHALL ser estabelecido pela confirmação do contrato, não presumido pela interface.

#### Scenario: Cadastrar nome válido

- **WHEN** uma pessoa envia um nome não vazio e ainda não cadastrado após normalização
- **THEN** o backend persiste a especialidade e a interface informa o sucesso somente após uma resposta válida da API

#### Scenario: Rejeitar nome vazio

- **WHEN** uma pessoa envia um nome vazio ou formado somente por espaços
- **THEN** o sistema informa a validação e não envia uma gravação inválida à API

#### Scenario: Rejeitar nome duplicado

- **WHEN** uma pessoa cadastra ou altera o nome para um valor equivalente a outro após trim e normalização sem distinção de caixa
- **THEN** o backend rejeita a operação e mantém os registros existentes sem alteração parcial

#### Scenario: Editar especialidade existente

- **WHEN** uma pessoa salva um nome válido para uma especialidade existente
- **THEN** o backend atualiza o registro identificado e a interface apresenta os dados atualizados

#### Scenario: Editar especialidade inexistente ou com falha

- **WHEN** a API informa que o identificador não existe ou a gravação falha
- **THEN** o sistema comunica o erro e não apresenta a alteração como concluída

### Requirement: Bloquear exclusão até garantir integridade referencial

Enquanto as relações de Especialidades com profissionais e consultas não estiverem implementadas com proteção referencial verificável, a operação DELETE SHALL retornar conflito sem alterar ou remover qualquer registro. Depois que as relações existirem e a proteção for verificada, o backend poderá excluir apenas uma especialidade sem referências e SHALL rejeitar a exclusão de registros referenciados sem cascata. A interface SHALL exigir confirmação explícita e informar o resultado real da API.

#### Scenario: Exclusão bloqueada enquanto referências não podem ser verificadas

- **WHEN** a operação DELETE é chamada antes de existirem as relações e a proteção referencial verificável
- **THEN** o backend retorna conflito e mantém a especialidade e todos os demais registros inalterados

#### Scenario: Excluir especialidade sem referências após habilitar integridade

- **WHEN** as relações e salvaguardas foram implementadas e verificadas, a pessoa confirma a exclusão e não há referências à especialidade
- **THEN** o backend remove somente a especialidade identificada e a interface atualiza a listagem

#### Scenario: Excluir especialidade referenciada após habilitar integridade

- **WHEN** as relações e salvaguardas foram implementadas e verificadas e a pessoa confirma a exclusão de uma especialidade referenciada
- **THEN** o backend rejeita a operação sem cascata e preserva todos os registros relacionados

#### Scenario: Cancelar ou não confirmar exclusão

- **WHEN** a pessoa não confirma a exclusão
- **THEN** nenhuma solicitação de exclusão é enviada

#### Scenario: Excluir especialidade inexistente ou com falha

- **WHEN** a API informa que a especialidade não existe ou a exclusão falha
- **THEN** o sistema comunica o erro e não informa sucesso

### Requirement: Restringir a integração ao contrato Xano confirmado

O frontend SHALL consumir Especialidades somente por APIs HTTP Xano cujo método, rota, parâmetros, campos, respostas e requisitos de autorização tenham sido confirmados. URLs e credenciais necessárias SHALL vir de configuração externa. Quando configuração, contrato ou habilitação estiverem ausentes, o sistema SHALL informar o bloqueio e não SHALL chamar rotas presumidas nem usar SQLite como fallback para Especialidades.

#### Scenario: Operar com integração confirmada e habilitada

- **WHEN** existe contrato confirmado e a configuração externa habilita a integração
- **THEN** as operações de Especialidades usam somente as APIs confirmadas e apresentam as respostas ou erros reais

#### Scenario: Contrato ou configuração pendente

- **WHEN** o contrato, a configuração externa ou a habilitação não está disponível
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
