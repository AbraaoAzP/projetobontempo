## MODIFIED Requirements

### Requirement: Manter a primeira entrega sem integração HTTP

A aplicação SHALL manter Início, Pacientes, Profissionais, Especialidades e Consultas acessíveis sem depender da disponibilidade do Xano. A página Início SHALL consultar somente as APIs Xano existentes de Pacientes e Profissionais quando a integração estiver explicitamente habilitada, a URL base correspondente estiver configurada e uma credencial de autorização estiver configurada. Quando essas condições não forem satisfeitas, a navegação SHALL continuar disponível e os indicadores correspondentes SHALL ser apresentados como indisponíveis. Esta exceção aplica-se somente aos indicadores do dashboard e não amplia as operações remotas das páginas dos módulos.

#### Scenario: Acessar as páginas sem integração com o Xano

- **WHEN** uma pessoa inicia a aplicação e navega sem URL base ou credencial de autorização configurada, ou com a integração desabilitada
- **THEN** as páginas existentes são apresentadas, o dashboard marca indisponíveis os indicadores remotos sem configuração e não realiza requisições HTTP ao Xano

### Requirement: Apresentar informações institucionais na página Início

A página Início SHALL apresentar a identidade visual Bontempo e uma visão administrativa com totais de Consultas e consultas do dia obtidos do SQLite local, além de totais de Pacientes, Profissionais e Especialidades somente quando houver integrações Xano existentes, explicitamente configuradas e autorizadas.

Cada indicador SHALL identificar sua fonte. Indicadores de consultas locais SHALL ser identificados como não sincronizados. Indicadores de Pacientes, Profissionais ou Especialidades sem integração Xano disponível SHALL ser marcados indisponíveis, sem números locais de fallback. O dashboard SHALL apresentar distribuição por status, visualização temporal dos próximos sete dias e próximas consultas ativas limitadas a data, horário e status, sem nomes ou observações clínicas.

#### Scenario: Abrir a página Início com dados locais

- **WHEN** a pessoa abre Início e a base SQLite local está disponível
- **THEN** vê indicadores de Consultas com origem local explícita, indicadores Xano somente quando autorizados/configurados, indisponibilidades separadas e agenda sem nomes ou observações clínicas

#### Scenario: Abrir a página Início

- **WHEN** a pessoa abre Início
- **THEN** vê a apresentação do sistema, indicadores reais com a fonte identificada e atalhos administrativos, sem dados fictícios

#### Scenario: Abrir a página Início sem dados

- **WHEN** a pessoa abre Início e a base local não possui consultas ou registros de uma entidade
- **THEN** vê estados vazios para consultas locais sem registros e indicadores de entidades remotas indisponíveis ou com zero somente quando a API autorizada confirmar lista vazia

#### Scenario: Abrir a página Início com integração pendente

- **WHEN** a pessoa abre Início e a consulta correspondente ao Xano não está confirmada e autorizada
- **THEN** vê cada integração indicada como pendente ou indisponível, sem usar contagens SQLite para as entidades Xano

### Requirement: Navegar pelos cards da página Início

A página Início SHALL apresentar atalhos de navegação para os módulos administrativos existentes: Pacientes, Profissionais, Especialidades e Consultas. Cada atalho SHALL levar à página correspondente e indicar claramente quando um módulo estiver indisponível, sem simular suas operações.

#### Scenario: Usar os atalhos dos módulos

- **WHEN** a pessoa seleciona o atalho de um módulo existente
- **THEN** a aplicação abre a página correspondente e mantém a navegação lateral disponível

#### Scenario: Usar os cards de navegação

- **WHEN** a pessoa seleciona um card de Pacientes, Profissionais, Especialidades ou Consultas na página Início
- **THEN** a aplicação abre a página existente correspondente

#### Scenario: Visualizar o módulo futuro

- **WHEN** a pessoa abre a página Início
- **THEN** Consultas é apresentada como módulo existente e seu atalho navega para a página correspondente, sem números fictícios

#### Scenario: Identificar módulo indisponível

- **WHEN** um módulo ainda não está implementado ou integrado
- **THEN** seu atalho ou estado é identificado como pendente ou indisponível e não oferece uma operação simulada

### Requirement: Preservar o escopo funcional da interface

A interface SHALL oferecer a página Início como dashboard administrativo e manter a navegação para Pacientes, Profissionais, Especialidades e Consultas existentes. Esta mudança SHALL NOT implementar prontuários, autenticação ou autorização fictícias, nem SHALL habilitar publicação ou alteração de dados no Xano. A apresentação de indicadores SHALL respeitar os requisitos de origem e indisponibilidade definidos para o dashboard administrativo.

#### Scenario: Acessar a aplicação sem autenticação

- **WHEN** a pessoa inicia a aplicação sem autenticação configurada
- **THEN** a interface não afirma que há autenticação ou controle de acesso e não apresenta nomes ou observações clínicas das próximas consultas no dashboard

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** a pessoa inicia a aplicação e navega sem login e sem integração Xano configurada
- **THEN** a página inicial e os módulos existentes ficam acessíveis sem chamadas HTTP ao Xano, e os dados locais são identificados como tais

#### Scenario: Conferir o escopo do dashboard

- **WHEN** a pessoa utiliza o dashboard
- **THEN** pode consultar os indicadores locais identificados e navegar pelos módulos existentes, sem acessar um prontuário ou operação remota não autorizada

#### Scenario: Conferir o escopo das páginas

- **WHEN** a pessoa utiliza a navegação da aplicação
- **THEN** Início, Pacientes, Profissionais, Especialidades e Consultas estão disponíveis sem prontuário, autenticação improvisada ou operações Xano não autorizadas

### Requirement: Preservar limites funcionais e arquiteturais

A interface SHALL NOT implementar login ou autenticação, apresentar dados fictícios, adicionar dependências, nem alterar backend, tabelas ou arquivos XanoScript. O dashboard SHALL realizar somente requisições GET às APIs Xano existentes de Pacientes e Profissionais sob as condições de configuração e autorização definidas para seus indicadores, e SHALL manter Consultas como dados SQLite locais. O frontend SHALL NOT acessar diretamente o banco de dados do Xano.

#### Scenario: Verificar ausência de integrações e operações

- **WHEN** a pessoa navega pelas páginas disponíveis
- **THEN** a aplicação não exige autenticação improvisada, não exibe dados inventados nem oferece operações remotas habilitadas sem autorização; sem configuração Xano suficiente, o dashboard não realiza requisições HTTP
