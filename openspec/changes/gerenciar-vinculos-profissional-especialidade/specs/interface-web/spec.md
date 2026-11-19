## ADDED Requirements

### Requirement: Gerenciar vínculos na página de Profissionais

A página de Profissionais SHALL permitir visualizar, criar e remover vínculos
Profissional–Especialidade por meio das APIs Xano confirmadas.

As operações SHALL permanecer desabilitadas quando a base do recurso não estiver
configurada, a leitura estiver desabilitada ou a escrita estiver desabilitada.

#### Scenario: Exibir vínculos existentes

- **WHEN** o profissional selecionado possui vínculos existentes
- **THEN** a página apresenta esses vínculos com as Especialidades existentes

#### Scenario: Não há especialidades disponíveis para vincular

- **WHEN** todas as Especialidades existentes já estão vinculadas ao profissional
- **THEN** a página informa que não há novo vínculo disponível e não envia POST

#### Scenario: Escrita desabilitada

- **WHEN** a integração de vínculos está desabilitada ou a configuração está ausente
- **THEN** os controles de criação e remoção permanecem indisponíveis e nenhuma
  requisição de mutação é enviada

#### Scenario: Atualizar vínculos após operação

- **WHEN** uma criação ou exclusão recebe resposta compatível de sucesso
- **THEN** o cache de vínculos é invalidado e a interface recarrega o estado atual

#### Scenario: Falha de transporte ou HTTP

- **WHEN** POST ou DELETE falha por transporte, resposta incompatível ou status
  HTTP de erro
- **THEN** o sistema apresenta o erro sem declarar sucesso ou alterar
  artificialmente a coleção local

### Requirement: Preservar integração de Consultas

A página de Consultas SHALL continuar usando o GET da coleção
`profissional_especialidade` como fonte autoritativa dos pares válidos.

Criar ou remover vínculos SHALL NOT alterar o campo textual legado nem migrar
dados automaticamente.

#### Scenario: Consultar especialidades vinculadas após alteração

- **WHEN** uma pessoa altera os vínculos de um profissional e abre Consultas
- **THEN** as Especialidades disponíveis passam a refletir a coleção atualizada
  sem inferir especialidade pelo campo textual legado

#### Scenario: Remover último vínculo

- **WHEN** um profissional perde todos os vínculos com o catálogo
- **THEN** a página de Consultas não oferece nenhuma Especialidade para esse
  profissional até que exista um novo vínculo confirmado
