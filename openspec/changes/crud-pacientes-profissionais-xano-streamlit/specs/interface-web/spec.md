## MODIFIED Requirements

### Requirement: Preservar o escopo funcional da interface

A interface SHALL manter a página Início e os módulos existentes de Pacientes, Profissionais, Especialidades e Consultas. As páginas de Pacientes e Profissionais SHALL disponibilizar operações CRUD por APIs HTTP do Xano confirmadas. As páginas de Especialidades e Consultas poderão permanecer no modo SQLite durante a transição até que suas próprias integrações sejam especificadas e implementadas. O frontend SHALL NOT acessar diretamente o banco de dados do Xano nem exigir login como parte desta mudança.

As chamadas a APIs SHALL depender de configuração externa válida e usar somente URLs e operações confirmadas. Credenciais eventualmente exigidas SHALL ser fornecidas externamente; tokens e senhas SHALL NOT ser incluídos em arquivos versionados. A mudança SHALL NOT alterar autenticação, permissões ou credenciais do Xano.

#### Scenario: Operar Pacientes e Profissionais usando APIs confirmadas

- **WHEN** a pessoa usuária executa uma operação CRUD em Pacientes ou Profissionais com integração configurada
- **THEN** a página utiliza uma API HTTP confirmada do Xano, sem acessar diretamente seu banco de dados

#### Scenario: Manter outros módulos durante a transição

- **WHEN** a pessoa usuária navega para Especialidades ou Consultas antes da integração dessas capacidades com o Xano
- **THEN** essas páginas preservam seu comportamento local existente sem interferir nas operações remotas de Pacientes e Profissionais

#### Scenario: Configuração da API ausente

- **WHEN** a configuração necessária para uma operação Xano está ausente
- **THEN** a página informa que a operação não foi executada e não apresenta sucesso simulado

#### Scenario: Preservar configuração e segurança

- **WHEN** a aplicação é configurada para acessar o Xano
- **THEN** URLs e credenciais são lidas de configuração externa e nenhuma autenticação, permissão ou credencial remota é alterada por esta integração

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** uma pessoa navega pelas páginas existentes sem login ou sem configuração válida do Xano
- **THEN** a navegação permanece disponível, nenhuma chamada remota é executada sem configuração e a interface informa quando uma operação depende da integração

#### Scenario: Acessar a aplicação sem autenticação

- **WHEN** a pessoa inicia a aplicação sem autenticação configurada
- **THEN** a interface não afirma que há autenticação ou controle de acesso e não apresenta nomes ou observações clínicas das próximas consultas no dashboard

#### Scenario: Conferir o escopo do dashboard

- **WHEN** a pessoa utiliza o dashboard
- **THEN** pode consultar os indicadores locais identificados e navegar pelos módulos existentes, sem acessar um prontuário ou operação remota não autorizada

#### Scenario: Conferir o escopo das páginas

- **WHEN** esta mudança é implementada
- **THEN** somente Pacientes e Profissionais passam a oferecer CRUD via Xano, sem habilitar prontuários, consultas remotas, disponibilidade ou gerenciamento de usuários

#### Scenario: Acessar o módulo de Especialidades

- **WHEN** a pessoa seleciona Especialidades na navegação
- **THEN** a aplicação apresenta a página do módulo e oferece as operações definidas pela capability `especialidades`, respeitando configuração e disponibilidade do contrato Xano

#### Scenario: Preservar limites de escopo

- **WHEN** a funcionalidade de Especialidades é integrada
- **THEN** a aplicação não exige login, não separa perfis Admin/Médico, não migra Consultas e mantém a infraestrutura SQLite ainda necessária a esse módulo
