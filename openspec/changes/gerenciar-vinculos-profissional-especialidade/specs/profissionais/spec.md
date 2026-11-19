## ADDED Requirements

### Requirement: Gerenciar vínculos entre profissionais e especialidades

A interface SHALL permitir criar e remover vínculos relacionais entre um
Profissional existente e uma Especialidade existente, usando o contrato Xano
confirmado de `profissional_especialidade`.

O vínculo SHALL ser representado por um identificador próprio e pelos IDs
inteiros positivos do profissional e da especialidade.

#### Scenario: Criar vínculo válido

- **WHEN** uma pessoa seleciona um profissional e uma especialidade existente
  ainda não vinculada e autoriza a operação
- **THEN** o sistema envia os dois IDs para o POST confirmado e apresenta o
  vínculo criado somente após resposta compatível

#### Scenario: Bloquear vínculo duplicado

- **WHEN** o par profissional-especialidade já existe na coleção carregada
- **THEN** o sistema não envia uma segunda criação e informa que o vínculo já
  está cadastrado

#### Scenario: Rejeitar referência inexistente

- **WHEN** o profissional ou a especialidade não existe no catálogo carregado
- **THEN** o sistema não envia o POST e informa a referência inválida

#### Scenario: Remover vínculo confirmado

- **WHEN** uma pessoa confirma a remoção de um vínculo existente
- **THEN** o sistema envia o identificador inteiro desse vínculo ao DELETE
  confirmado e atualiza a interface somente após resposta 2xx

#### Scenario: Cancelar remoção

- **WHEN** uma pessoa não confirma a remoção
- **THEN** nenhuma solicitação DELETE é enviada

### Requirement: Preservar especialidade textual legada

O gerenciamento relacional SHALL NOT substituir automaticamente nem migrar o
campo textual legado `profissional.especialidade`.

O sistema SHALL NOT inferir vínculos relacionais comparando ou convertendo o
conteúdo desse campo.

#### Scenario: Profissional possui campo textual legado

- **WHEN** um profissional possui `especialidade` como texto e o catálogo
  possui especialidades relacionais
- **THEN** o campo legado continua preservado sem criar vínculos implícitos

#### Scenario: Valor textual não corresponde ao catálogo

- **WHEN** o campo textual não corresponde inequivocamente a uma especialidade
- **THEN** o sistema não realiza correspondência automática nem atribui vínculo

### Requirement: Validar integridade ainda não confirmada no backend

As validações locais SHALL bloquear entradas inválidas visíveis, mas SHALL NOT
ser apresentadas como prova de unicidade composta ou integridade referencial no
Xano.

Restrições físicas como índice composto, chaves estrangeiras e exclusão
considerando vínculos dependentes permanecem pendentes de confirmação.

#### Scenario: Backend rejeita uma criação

- **WHEN** o frontend envia um par aparentemente válido e o Xano rejeita o POST
- **THEN** o sistema apresenta o erro e não declara o vínculo criado

#### Scenario: Backend rejeita uma exclusão

- **WHEN** o Xano rejeita o DELETE de um vínculo
- **THEN** o sistema apresenta o erro e mantém o vínculo na interface
