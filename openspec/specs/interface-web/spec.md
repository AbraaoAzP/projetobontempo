# interface-web Specification

## Purpose

Define o comportamento inicial da interface web do consultório, incluindo sua navegação principal e os limites seguros de comunicação com as APIs HTTP do Xano.

## Requirements

### Requirement: Disponibilizar a navegação principal

A aplicação web SHALL disponibilizar páginas acessíveis para Início, Pacientes e Profissionais por meio da navegação do Streamlit.

#### Scenario: Abrir a aplicação

- **WHEN** uma pessoa acessa a aplicação web
- **THEN** a página Início é apresentada e a navegação para Pacientes e Profissionais está disponível

#### Scenario: Navegar entre as páginas

- **WHEN** uma pessoa seleciona Pacientes ou Profissionais na navegação
- **THEN** a aplicação apresenta a página selecionada e mantém as demais opções de navegação disponíveis

### Requirement: Manter a primeira entrega sem integração HTTP

A aplicação SHALL manter Início, Pacientes, Profissionais, Especialidades e Consultas acessíveis sem depender da disponibilidade do Xano. A página Início SHALL consultar somente as APIs Xano existentes de Pacientes e Profissionais quando a integração estiver explicitamente habilitada, a URL base correspondente estiver configurada e uma credencial de autorização estiver configurada. Quando essas condições não forem satisfeitas, a navegação SHALL continuar disponível e os indicadores correspondentes SHALL ser apresentados como indisponíveis. Esta exceção aplica-se somente aos indicadores do dashboard e não amplia as operações remotas das páginas dos módulos.

#### Scenario: Acessar as páginas sem integração com o Xano

- **WHEN** uma pessoa inicia a aplicação e navega sem URL base ou credencial de autorização configurada, ou com a integração desabilitada
- **THEN** as páginas existentes são apresentadas, o dashboard marca indisponíveis os indicadores remotos sem configuração e não realiza requisições HTTP ao Xano

### Requirement: Respeitar a integração frontend-backend

O frontend SHALL obter dados do sistema por meio das APIs HTTP existentes do Xano e SHALL NOT acessar diretamente o banco de dados do Xano.

O frontend SHALL utilizar somente endpoints confirmados e correspondentes às capacidades existentes de pacientes e profissionais. Esta Change não SHALL introduzir operações de agendamento ou disponibilidade.

#### Scenario: Consultar dados de uma capacidade existente

- **WHEN** uma página do frontend precisar consultar dados de pacientes ou profissionais
- **THEN** a consulta é realizada por uma API HTTP existente do Xano, sem conexão direta ao banco de dados

#### Scenario: Não há endpoint confirmado para uma operação

- **WHEN** uma operação solicitada não possui endpoint Xano existente e confirmado
- **THEN** o frontend não inventa nem chama uma rota presumida para essa operação

### Requirement: Manter configuração e credenciais fora do código versionado

O frontend SHALL obter a URL base das APIs e quaisquer credenciais necessárias por configuração externa ao código-fonte versionado.

O frontend SHALL NOT conter tokens, senhas ou URLs sensíveis fixados no código ou em arquivos versionados.

#### Scenario: Executar com configuração externa

- **WHEN** a aplicação precisa se conectar às APIs do Xano
- **THEN** os valores de URL e autenticação são lidos de configuração externa, e não de valores sensíveis embutidos no código

#### Scenario: Configuração obrigatória ausente

- **WHEN** a aplicação precisa fazer uma chamada à API e a configuração necessária não está disponível
- **THEN** a aplicação informa claramente que a configuração está pendente ou ausente e não simula uma resposta bem-sucedida

### Requirement: Apresentar identidade visual consistente

A interface SHALL apresentar Início, Pacientes e Profissionais com uma identidade visual profissional e consistente, usando uma paleta predominantemente azul e verde-água, fundo claro e navegação lateral.

#### Scenario: Navegar entre páginas com identidade consistente

- **WHEN** a pessoa abre Início, Pacientes ou Profissionais
- **THEN** cada página mantém a identidade visual comum e a navegação lateral permanece disponível

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

### Requirement: Apresentar páginas informativas dos módulos

As páginas Pacientes e Profissionais SHALL apresentar o título correspondente ao módulo e informar que suas funcionalidades serão implementadas futuramente.

#### Scenario: Abrir Pacientes

- **WHEN** a pessoa seleciona Pacientes na navegação
- **THEN** vê o título do módulo Pacientes e uma indicação de que suas funcionalidades serão implementadas futuramente

#### Scenario: Abrir Profissionais

- **WHEN** a pessoa seleciona Profissionais na navegação
- **THEN** vê o título do módulo Profissionais e uma indicação de que suas funcionalidades serão implementadas futuramente

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

### Requirement: Apresentar identidade visual Bontempo consistente

A aplicação SHALL apresentar as páginas Início, Pacientes e Profissionais com cabeçalhos, ícones, hierarquia tipográfica e espaçamentos consistentes, adequados à visualização em notebook e navegador, sem alterar a navegação existente.

#### Scenario: Navegar pelas páginas existentes

- **WHEN** a pessoa abre Início, Pacientes ou Profissionais
- **THEN** cada página mantém a identidade visual comum e a navegação continua oferecendo somente essas três páginas

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

### Requirement: Apresentar estrutura vazia do módulo Pacientes

A página Pacientes SHALL exibir cabeçalho com título e descrição, um campo de busca desabilitado, um botão “Novo paciente” desabilitado, uma tabela vazia com as colunas ID, Nome, Telefone e E-mail e a mensagem “Integração com Xano ainda não disponível”.

A página SHALL NOT apresentar registros de pacientes nem realizar chamadas HTTP ou simular operações.

#### Scenario: Abrir Pacientes sem integração

- **WHEN** a pessoa abre Pacientes sem integração com o Xano
- **THEN** vê o cabeçalho, os controles desabilitados, a tabela sem linhas com as colunas especificadas e a mensagem de integração indisponível, sem chamadas HTTP

#### Scenario: Tentar usar controles do módulo Pacientes

- **WHEN** a pessoa visualiza o campo de busca e o botão “Novo paciente”
- **THEN** ambos estão desabilitados e não iniciam busca, cadastro ou qualquer operação persistida

### Requirement: Apresentar estrutura vazia do módulo Profissionais

A página Profissionais SHALL exibir cabeçalho com título e descrição, um campo de busca desabilitado, um botão “Novo profissional” desabilitado, uma tabela vazia com as colunas ID, Nome e Especialidade e uma mensagem explícita de que a integração futura com Xano ainda não está disponível.

A página SHALL NOT apresentar registros de profissionais nem realizar chamadas HTTP ou simular operações.

#### Scenario: Abrir Profissionais sem integração

- **WHEN** a pessoa abre Profissionais sem integração com o Xano
- **THEN** vê o cabeçalho, os controles desabilitados, a tabela sem linhas com as colunas especificadas e a indicação de integração futura, sem chamadas HTTP

#### Scenario: Tentar usar controles do módulo Profissionais

- **WHEN** a pessoa visualiza o campo de busca e o botão “Novo profissional”
- **THEN** ambos estão desabilitados e não iniciam busca, cadastro ou qualquer operação persistida

### Requirement: Preservar limites funcionais e arquiteturais

A interface SHALL NOT implementar login ou autenticação, apresentar dados fictícios, adicionar dependências, nem alterar backend, tabelas ou arquivos XanoScript. O dashboard SHALL realizar somente requisições GET às APIs Xano existentes de Pacientes e Profissionais sob as condições de configuração e autorização definidas para seus indicadores, e SHALL manter Consultas como dados SQLite locais. O frontend SHALL NOT acessar diretamente o banco de dados do Xano.

#### Scenario: Verificar ausência de integrações e operações

- **WHEN** a pessoa navega pelas páginas disponíveis
- **THEN** a aplicação não exige autenticação improvisada, não exibe dados inventados nem oferece operações remotas habilitadas sem autorização; sem configuração Xano suficiente, o dashboard não realiza requisições HTTP
