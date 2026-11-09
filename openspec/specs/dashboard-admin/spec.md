# dashboard-admin Specification

## Purpose

Oferece à equipe administrativa uma visão resumida e honesta da atividade do consultório, distinguindo dados locais de informações realmente integradas ao Xano.

## Requirements

### Requirement: Exibir indicadores administrativos com origem identificada

A página administrativa SHALL apresentar totais de consultas locais e consultas do dia, além dos totais de pacientes, profissionais e especialidades somente quando obtidos de integrações Xano já existentes, explicitamente configuradas e autorizadas. Cada valor SHALL identificar sua fonte. Os totais de pacientes, profissionais e especialidades SHALL NOT ser lidos do SQLite nem receber fallback de outra fonte. Enquanto não houver integração Xano disponível e autorizada, esses indicadores SHALL ser apresentados como indisponíveis, sem números inventados.

#### Scenario: Exibir indicadores locais de consultas

- **WHEN** a base SQLite local está disponível
- **THEN** a página apresenta os totais reais de consultas e consultas do dia com identificação explícita de que são dados locais e não sincronizados

#### Scenario: Exibir totais remotos autorizados

- **WHEN** as APIs Xano existentes de Pacientes e Profissionais estão explicitamente configuradas e autorizadas e respondem com sucesso
- **THEN** a página apresenta a quantidade de registros retornada por cada API, identificada como dado Xano, sem exibir os registros pessoais

#### Scenario: Integrações remotas não configuradas ou indisponíveis

- **WHEN** uma API não está configurada e autorizada, ou retorna erro
- **THEN** o indicador correspondente é apresentado como indisponível ou com erro, sem valor SQLite substituto

#### Scenario: Especialidades sem integração Xano confirmada

- **WHEN** não há uma integração Xano de Especialidades confirmada e configurada
- **THEN** o indicador de Especialidades é apresentado como indisponível, sem leitura SQLite e sem rota presumida

### Requirement: Exibir distribuição e próximas consultas locais

A página SHALL apresentar a distribuição das consultas locais por status, uma visualização temporal para os sete dias seguintes e uma lista das próximas consultas ativas ordenada por data e horário. Os itens da agenda SHALL limitar os dados exibidos a data, horário e status, sem expor nomes ou observações clínicas.

#### Scenario: Há consultas locais futuras

- **WHEN** existem consultas ativas futuras na base SQLite local
- **THEN** a página apresenta uma lista ordenada com data, horário e status, identificada como agenda local

#### Scenario: Não há consultas futuras

- **WHEN** não existem consultas ativas futuras na base SQLite local
- **THEN** a página informa que não há próximas consultas locais sem criar itens de exemplo

#### Scenario: Distribuição ou série temporal sem consultas

- **WHEN** a base local não contém consultas no período representado
- **THEN** a visualização indica ausência de dados e não apresenta valores fictícios

### Requirement: Sinalizar indisponibilidade de integrações

Quando indicadores ou listagens do Xano não puderem ser consultados por ausência de integração confirmada e autorizada, a página SHALL indicar essa indisponibilidade claramente. A aplicação SHALL NOT inventar endpoints, tratar falhas como sucesso nem usar dados locais como fallback silencioso para números apresentados como dados do Xano.

#### Scenario: Integração Xano pendente

- **WHEN** a integração Xano para uma entidade ainda não está confirmada e autorizada
- **THEN** a página identifica essa fonte como indisponível ou pendente, separadamente dos indicadores locais

#### Scenario: Falha ao obter dados de uma fonte

- **WHEN** uma fonte habilitada falha ao fornecer dados
- **THEN** a página comunica a falha e não substitui os dados por valores fictícios ou por outra fonte sem identificar a substituição

### Requirement: Oferecer atalhos administrativos

A página SHALL oferecer navegação para os módulos administrativos existentes sem indicar como operacionais módulos que estejam indisponíveis.

#### Scenario: Abrir um módulo disponível

- **WHEN** a pessoa seleciona um atalho de módulo existente
- **THEN** a aplicação navega para a página correspondente, mantendo a navegação principal disponível

#### Scenario: Módulo ainda indisponível

- **WHEN** um módulo ainda não está implementado ou integrado
- **THEN** o dashboard apresenta seu estado pendente ou indisponível e não simula uma operação
