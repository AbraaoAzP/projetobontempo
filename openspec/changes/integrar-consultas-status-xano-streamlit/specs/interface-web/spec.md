## MODIFIED Requirements

### Requirement: Manter a primeira entrega sem integração HTTP

A aplicação SHALL manter Início, Pacientes, Profissionais, Especialidades e Consultas acessíveis sem depender da disponibilidade do Xano. A página Início SHALL consultar somente as APIs Xano existentes de Pacientes e Profissionais quando a integração estiver explicitamente habilitada, a URL base correspondente estiver configurada e uma credencial de autorização estiver configurada. Quando essas condições não forem satisfeitas, a navegação SHALL continuar disponível e os indicadores correspondentes SHALL ser apresentados como indisponíveis. Esta exceção aplica-se somente aos indicadores do Dashboard e não amplia as operações remotas dos demais módulos. A página Consultas SHALL usar somente operações Xano confirmadas, quando sua configuração e habilitação estiverem presentes; sua indisponibilidade não SHALL impedir a navegação nem provocar fallback silencioso para SQLite.

#### Scenario: Acessar as páginas sem integração com o Xano

- **WHEN** uma pessoa inicia a aplicação e navega sem configuração ou habilitação para uma integração Xano
- **THEN** as páginas existentes permanecem acessíveis, os indicadores remotos sem configuração são marcados como indisponíveis e nenhuma requisição correspondente é enviada

#### Scenario: Xano indisponível na página Consultas

- **WHEN** a pessoa abre Consultas sem configuração, com integração desabilitada ou durante falha do Xano
- **THEN** a navegação continua disponível e a página informa o estado remoto sem tratar a condição como lista vazia ou recorrer silenciosamente aos dados SQLite

### Requirement: Respeitar a integração frontend-backend

O frontend SHALL obter dados do sistema por meio das APIs HTTP existentes do Xano e SHALL NOT acessar diretamente o banco de dados do Xano. Para Pacientes e Profissionais, SHALL usar somente endpoints confirmados. Para Especialidades, SHALL usar somente as rotas informadas e autorizadas pelo usuário: GET/POST `/especialidade` e GET/PATCH/DELETE `/especialidade/{especialidade_id}`. Para Consultas e Status da Consulta, SHALL usar somente as operações, rotas, campos e formatos estabelecidos pelos contratos confirmados, sem inferi-los do SQLite ou de outras entidades.

Esta Change não SHALL criar operações Xano de agendamento ou disponibilidade, nem introduzir tabelas, endpoints ou scripts remotos.

#### Scenario: Consultar dados de uma capacidade existente

- **WHEN** uma página do frontend precisar consultar dados de pacientes ou profissionais
- **THEN** a consulta é realizada por uma API HTTP existente do Xano, sem conexão direta ao banco de dados

#### Scenario: Não há endpoint confirmado para uma operação

- **WHEN** uma operação solicitada não possui endpoint Xano existente e confirmado
- **THEN** o frontend não inventa nem chama uma rota presumida para essa operação

#### Scenario: Consultar ou alterar Especialidades

- **WHEN** a página de Especialidades executa uma operação habilitada
- **THEN** ela usa uma API HTTP Xano confirmada, sem conexão direta ao banco de dados e sem recorrer ao SQLite como fallback

#### Scenario: Consultar ou alterar Consultas e Status

- **WHEN** a página Consultas executa uma operação habilitada
- **THEN** ela usa somente o contrato Xano confirmado para essa operação, sem conexão direta ao banco de dados e sem fallback SQLite

#### Scenario: Não há contrato confirmado para uma operação

- **WHEN** uma operação de Especialidades, Consulta ou Status não possui contrato confirmado
- **THEN** o frontend não presume nem chama uma rota e informa que a integração está pendente

### Requirement: Preservar o escopo funcional da interface

A interface SHALL oferecer a página Início como Dashboard administrativo e manter a navegação para Pacientes, Profissionais, Especialidades e Consultas existentes. As páginas Especialidades e Consultas SHALL oferecer somente as operações definidas pelas respectivas capabilities em APIs existentes e autorizadas. Esta mudança SHALL NOT implementar prontuários, login, autenticação ou separação de perfis Admin/Médico, migrar ou excluir dados SQLite, remover SQLite globalmente, alterar contratos de Pacientes ou Profissionais, alterar segurança do Xano ou publicar scripts. A apresentação de indicadores SHALL respeitar os requisitos de origem e indisponibilidade definidos para o Dashboard.

#### Scenario: Acessar a aplicação sem autenticação

- **WHEN** a pessoa inicia a aplicação sem autenticação configurada
- **THEN** a interface não afirma que há autenticação ou controle de acesso e não apresenta nomes ou observações clínicas das próximas consultas no Dashboard

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** a pessoa inicia a aplicação sem login e uma integração Xano está desabilitada ou sem configuração válida
- **THEN** a navegação permanece disponível, a página afetada informa indisponibilidade e nenhuma chamada sem configuração é enviada

#### Scenario: Conferir o escopo do dashboard

- **WHEN** a pessoa utiliza o Dashboard
- **THEN** pode consultar os indicadores locais identificados e navegar pelos módulos existentes, sem acessar um prontuário ou operação remota não autorizada

#### Scenario: Conferir o escopo das páginas

- **WHEN** a pessoa utiliza a navegação da aplicação
- **THEN** Início, Pacientes, Profissionais, Especialidades e Consultas estão disponíveis; Especialidades e Consultas oferecem somente as operações especificadas por suas APIs autorizadas, sem prontuário, autenticação improvisada ou operações remotas não autorizadas

#### Scenario: Acessar o módulo de Especialidades

- **WHEN** a pessoa seleciona Especialidades na navegação
- **THEN** a aplicação apresenta a página do módulo e oferece as operações definidas pela capability `especialidades`, respeitando configuração e disponibilidade do contrato Xano

#### Scenario: Preservar limites de escopo

- **WHEN** a página Consultas é integrada ao Xano
- **THEN** a aplicação não exige login, não separa perfis Admin/Médico, não migra nem exclui o acervo SQLite e mantém a infraestrutura local ainda necessária ao Dashboard

### Requirement: Preservar limites funcionais e arquiteturais

A interface SHALL NOT implementar login, autenticação ou separação Admin/Médico, apresentar dados fictícios, adicionar dependências não previstas, nem alterar backend, tabelas, arquivos XanoScript ou configurações de segurança. O Dashboard SHALL realizar somente as requisições GET já especificadas para seus indicadores remotos de Pacientes e Profissionais e SHALL continuar obtendo Consultas e Status do SQLite local, com sua origem identificada. A página Especialidades SHALL usar somente o CRUD definido por suas APIs existentes e autorizadas, sem acesso direto ao banco e sem fallback SQLite. A página Consultas SHALL usar somente operações Xano confirmadas e habilitadas por configuração externa, sem acesso direto ao banco nem fallback SQLite. A integração SHALL NOT migrar nem excluir dados locais ou remover infraestrutura SQLite enquanto houver dependências. Nenhum segredo SHALL ser versionado e o frontend SHALL NOT acessar diretamente o banco de dados do Xano.

#### Scenario: Verificar ausência de integrações e operações

- **WHEN** a pessoa navega pelas páginas disponíveis
- **THEN** a aplicação não exige autenticação improvisada, não exibe dados inventados nem oferece operações remotas fora das capabilities autorizadas; sem configuração suficiente, não envia as requisições correspondentes

#### Scenario: Verificar limites da integração

- **WHEN** a pessoa navega ou executa operações em Especialidades ou Consultas
- **THEN** as chamadas usam somente contratos confirmados, falhas não são simuladas como sucesso e nenhuma garantia de integridade não confirmada é atribuída ao Xano

#### Scenario: Preservar a dependência SQLite do Dashboard

- **WHEN** a página Consultas passa a usar o Xano
- **THEN** o Dashboard continua lendo os dados locais de Consultas e Status, e a infraestrutura, o arquivo e os registros SQLite permanecem sem remoção ou migração nesta mudança

#### Scenario: Preservar a dependência SQLite de Consultas

- **WHEN** a página Consultas passa a usar o Xano
- **THEN** a infraestrutura SQLite usada pelo Dashboard permanece sem remoção ou migração nesta mudança
