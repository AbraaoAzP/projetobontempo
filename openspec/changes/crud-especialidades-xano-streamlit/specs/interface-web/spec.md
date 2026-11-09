## MODIFIED Requirements

### Requirement: Respeitar a integração frontend-backend

O frontend SHALL obter dados do sistema por meio de APIs HTTP confirmadas do Xano e SHALL NOT acessar diretamente o banco de dados do Xano. Para Especialidades, a interface SHALL chamar somente operações cujos métodos, rotas, parâmetros, campos, respostas e requisitos de autorização tenham sido confirmados; a existência de campos ou rotas nos arquivos locais não comprova publicação no ambiente remoto.

#### Scenario: Consultar dados de uma capacidade existente

- **WHEN** uma página do frontend precisar consultar dados de pacientes ou profissionais
- **THEN** a consulta é realizada por uma API HTTP confirmada do Xano, sem conexão direta ao banco de dados

#### Scenario: Não há endpoint confirmado para uma operação

- **WHEN** uma operação solicitada não possui endpoint Xano existente e confirmado
- **THEN** o frontend não inventa nem chama uma rota presumida para essa operação

#### Scenario: Consultar ou alterar Especialidades

- **WHEN** a página de Especialidades executa uma operação habilitada
- **THEN** ela usa uma API HTTP Xano confirmada, sem conexão direta ao banco de dados e sem recorrer ao SQLite como fallback

#### Scenario: Não há contrato confirmado para uma operação

- **WHEN** uma operação de Especialidades não possui contrato confirmado
- **THEN** o frontend não presume nem chama uma rota e informa que a integração está pendente

### Requirement: Preservar o escopo funcional da interface

A aplicação SHALL manter a navegação existente e disponibilizar o módulo de Especialidades para listar, consultar, cadastrar, editar e excluir registros conforme a capability `especialidades`. Esta mudança SHALL NOT implementar login, autenticação ou separação Admin/Médico, migrar Consultas, remover o SQLite globalmente, nem alterar os contratos das páginas de Pacientes e Profissionais.

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** a pessoa inicia a aplicação e navega sem login e sem configuração ou habilitação da integração de Especialidades
- **THEN** a navegação permanece disponível e a página de Especialidades informa a pendência sem enviar chamadas ou depender de respostas simuladas

#### Scenario: Acessar a aplicação sem autenticação

- **WHEN** a pessoa inicia a aplicação sem autenticação configurada
- **THEN** a interface não afirma que há autenticação ou controle de acesso e não apresenta nomes ou observações clínicas das próximas consultas no dashboard

#### Scenario: Conferir o escopo do dashboard

- **WHEN** a pessoa utiliza o dashboard
- **THEN** pode consultar os indicadores locais identificados e navegar pelos módulos existentes, sem acessar um prontuário ou operação remota não autorizada

#### Scenario: Conferir o escopo das páginas

- **WHEN** a pessoa utiliza a navegação da aplicação
- **THEN** as páginas preexistentes permanecem disponíveis, Especialidades oferece somente as operações desta capability e esta mudança não adiciona login, separação de perfis nem migração de Consultas

#### Scenario: Acessar o módulo de Especialidades

- **WHEN** a pessoa seleciona Especialidades na navegação
- **THEN** a aplicação apresenta a página do módulo e oferece as operações definidas pela capability `especialidades`, respeitando configuração e disponibilidade do contrato Xano

#### Scenario: Preservar limites de escopo

- **WHEN** a funcionalidade de Especialidades é integrada
- **THEN** a aplicação não exige login, não separa perfis Admin/Médico, não migra Consultas e mantém a infraestrutura SQLite ainda necessária a esse módulo

### Requirement: Apresentar identidade visual Bontempo consistente

A aplicação SHALL apresentar as páginas Início, Pacientes, Profissionais e Especialidades com cabeçalhos, ícones, hierarquia tipográfica e espaçamentos consistentes, adequados à visualização em notebook e navegador, sem remover a navegação preexistente.

#### Scenario: Navegar até Especialidades

- **WHEN** a pessoa abre a página Especialidades
- **THEN** ela mantém a identidade visual comum da aplicação e as opções de navegação preexistentes continuam disponíveis

#### Scenario: Navegar pelas páginas existentes

- **WHEN** a pessoa abre Início, Pacientes, Profissionais ou Especialidades
- **THEN** cada página mantém a identidade visual comum e a navegação preexistente continua disponível

### Requirement: Preservar limites funcionais e arquiteturais

A interface SHALL NOT implementar login, autenticação ou separação Admin/Médico nesta mudança. O módulo Especialidades SHALL usar somente APIs Xano confirmadas, sem acesso direto ao banco e sem fallback SQLite. A mudança SHALL NOT migrar Consultas nem remover o serviço, a inicialização ou o arquivo SQLite enquanto esse módulo depender deles. A integração real SHALL permanecer condicionada à configuração e habilitação externas; nenhum segredo SHALL ser versionado.

#### Scenario: Verificar ausência de integrações e operações

- **WHEN** a pessoa navega pelas páginas disponíveis nesta etapa
- **THEN** a aplicação não exige autenticação, Especialidades não oferece operações além do CRUD por contrato confirmado e a infraestrutura SQLite usada por Consultas permanece sem remoção

#### Scenario: Verificar limites da integração

- **WHEN** a pessoa navega ou executa operações no módulo Especialidades
- **THEN** não há login ou perfil de acesso implementado, as chamadas usam somente contrato confirmado e falhas não são simuladas como sucesso

#### Scenario: Preservar a dependência SQLite de Consultas

- **WHEN** a página Especialidades passa a usar o Xano
- **THEN** a infraestrutura SQLite usada por Consultas permanece sem remoção ou migração nesta mudança
