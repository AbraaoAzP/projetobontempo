## ADDED Requirements

### Requirement: Disponibilizar módulo Prontuários

A interface SHALL incluir uma página Prontuários na navegação principal e
integrá-la aos módulos administrativos existentes.

Quando a integração estiver desabilitada ou a configuração estiver ausente,
a página SHALL continuar navegável e informar indisponibilidade sem simular
dados ou sucesso.

#### Scenario: Navegar para Prontuários

- **WHEN** uma pessoa seleciona o módulo Prontuários
- **THEN** a aplicação apresenta o cabeçalho da página e o estado configurado
  da integração

### Requirement: Manter Prontuários exclusivamente no Xano

A página Prontuários SHALL obter dados e executar mutações somente pelas APIs
Xano confirmadas. SHALL NOT consultar SQLite, criar dados locais de fallback ou
combinar fontes.

#### Scenario: Integração habilitada

- **WHEN** a leitura do Xano está habilitada e configurada
- **THEN** a página apresenta somente registros retornados pela API remota

#### Scenario: Falha ou ausência de configuração

- **WHEN** falta configuração ou ocorre falha HTTP/transporte
- **THEN** a página apresenta indisponibilidade ou erro sem lista local fictícia

### Requirement: Invalidar cache após mutações

Após criação, edição ou exclusão bem-sucedida, a interface SHALL invalidar o
cache de Prontuários e recarregar o estado remoto.

#### Scenario: Mutação bem-sucedida

- **WHEN** POST, PATCH ou DELETE recebe resposta compatível de sucesso
- **THEN** o cache é invalidado e os dados são recarregados

#### Scenario: Mutação falha

- **WHEN** POST, PATCH ou DELETE falha
- **THEN** o cache não é invalidado como sucesso e o erro permanece visível
