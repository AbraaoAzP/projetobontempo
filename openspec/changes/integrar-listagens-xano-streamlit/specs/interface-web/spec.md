## MODIFIED Requirements

### Requirement: Manter a primeira entrega sem integração HTTP

A entrega inicial sem HTTP é o comportamento-base anterior a esta Change; esta Change acrescenta somente as listagens GET posteriores. A navegação entre Início, Pacientes e Profissionais SHALL permanecer disponível independentemente da disponibilidade do Xano. As chamadas reais SHALL permanecer desabilitadas por padrão. Quando a URL de uma listagem não estiver configurada, ou quando a integração não estiver explicitamente habilitada, a interface SHALL apresentar o estado apropriado sem fazer a requisição correspondente. Somente depois de configurada e explicitamente habilitada, as páginas poderão realizar seus GETs de listagem conforme esta Change.

#### Scenario: Acessar as páginas sem integração com o Xano

- **WHEN** uma pessoa inicia a aplicação e navega entre Início, Pacientes e Profissionais sem integração explicitamente habilitada
- **THEN** as três páginas são apresentadas e a navegação funciona sem realizar requisições HTTP ao Xano, com indicação clara de configuração pendente nos módulos de listagem

### Requirement: Apresentar páginas informativas dos módulos

As páginas Pacientes e Profissionais SHALL manter seus títulos, descrições e identidade visual, e exibir nas tabelas os registros retornados pelos respectivos endpoints GET de listagem quando a integração estiver configurada e disponível.

#### Scenario: Abrir Pacientes

- **WHEN** a pessoa seleciona Pacientes na navegação e o GET de listagem retorna registros válidos
- **THEN** vê o título e a descrição do módulo e os registros reais retornados pela API nas colunas previstas

#### Scenario: Abrir Profissionais

- **WHEN** a pessoa seleciona Profissionais na navegação e o GET de listagem retorna registros válidos
- **THEN** vê o título e a descrição do módulo e os registros reais retornados pela API nas colunas previstas, incluindo `especialidade` como texto

#### Scenario: Abrir módulos clínicos ainda não implementados

- **WHEN** uma pessoa consulta a navegação durante esta Change
- **THEN** Especialidades, Consultas e Prontuários não são adicionados ou apresentados como funcionalidades implementadas

### Requirement: Preservar o escopo funcional da interface

A interface SHALL manter somente as páginas Início, Pacientes e Profissionais, não exigir login nem apresentar dados fictícios de pacientes ou profissionais. Esta Change SHALL permitir somente requisições HTTP GET para as duas listagens confirmadas e SHALL NOT habilitar cadastro, edição, exclusão, operações de escrita, agendamentos, disponibilidades ou acesso a dados clínicos.

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** uma pessoa inicia a aplicação e navega pelas páginas disponíveis sem login e sem configuração ou disponibilidade do Xano
- **THEN** as três páginas são apresentadas sem exigir autenticação; sem configuração não são feitas requisições e a interface informa a pendência, e com configuração indisponível informa a falha sem inventar dados

#### Scenario: Conferir o escopo das páginas

- **WHEN** a pessoa utiliza a navegação da aplicação
- **THEN** somente Início, Pacientes e Profissionais estão disponíveis; as páginas de módulo podem listar dados reais via GET, mas não oferecem operações de cadastro, edição, exclusão, agendamento ou disponibilidade

### Requirement: Apresentar estrutura vazia do módulo Pacientes

A página Pacientes SHALL manter cabeçalho, descrição, busca desabilitada e botão “Novo paciente” desabilitado, e apresentar os campos ID, Nome, Telefone e E-mail em tabela. Com integração configurada, a tabela SHALL exibir somente registros recebidos do GET de listagem; se a resposta for uma lista vazia, SHALL apresentar uma mensagem apropriada de nenhum paciente cadastrado. A página SHALL NOT simular registros.

#### Scenario: Abrir Pacientes sem integração

- **WHEN** a pessoa abre Pacientes sem integração com o Xano
- **THEN** vê o cabeçalho, os controles desabilitados, a estrutura de tabela com as colunas especificadas e uma indicação de configuração ausente ou de falha, sem registros inventados

#### Scenario: Tentar usar controles do módulo Pacientes

- **WHEN** a pessoa visualiza o campo de busca e o botão “Novo paciente”
- **THEN** ambos estão desabilitados e não iniciam busca, cadastro ou qualquer operação persistida

#### Scenario: Listar pacientes existentes

- **WHEN** o GET de pacientes retorna uma coleção JSON válida de registros
- **THEN** cada linha da tabela corresponde a um registro retornado e apresenta somente ID, Nome, Telefone e E-mail

#### Scenario: Listar sem pacientes

- **WHEN** o GET de pacientes retorna uma coleção JSON vazia
- **THEN** a tabela não apresenta linhas fictícias e a página informa que não há pacientes cadastrados

### Requirement: Apresentar estrutura vazia do módulo Profissionais

A página Profissionais SHALL manter cabeçalho, descrição, busca desabilitada e botão “Novo profissional” desabilitado, e apresentar os campos ID, Nome e Especialidade em tabela. Com integração configurada, a tabela SHALL exibir somente registros recebidos do GET de listagem; `especialidade` SHALL permanecer o campo textual retornado pelo endpoint, sem exigir catálogo ou relação. Se a resposta for uma lista vazia, SHALL apresentar uma mensagem apropriada de nenhum profissional cadastrado. A página SHALL NOT simular registros.

#### Scenario: Abrir Profissionais sem integração

- **WHEN** a pessoa abre Profissionais sem integração com o Xano
- **THEN** vê o cabeçalho, os controles desabilitados, a estrutura de tabela com as colunas especificadas e uma indicação de configuração ausente ou de falha, sem registros inventados

#### Scenario: Tentar usar controles do módulo Profissionais

- **WHEN** a pessoa visualiza o campo de busca e o botão “Novo profissional”
- **THEN** ambos estão desabilitados e não iniciam busca, cadastro ou qualquer operação persistida

#### Scenario: Listar profissionais existentes

- **WHEN** o GET de profissionais retorna uma coleção JSON válida de registros
- **THEN** cada linha da tabela corresponde a um registro retornado e apresenta somente ID, Nome e Especialidade textual

#### Scenario: Listar sem profissionais

- **WHEN** o GET de profissionais retorna uma coleção JSON vazia
- **THEN** a tabela não apresenta linhas fictícias e a página informa que não há profissionais cadastrados

### Requirement: Preservar limites funcionais e arquiteturais

A interface SHALL NOT implementar login ou gerenciamento de usuários, dados fictícios, CRUD, agendamentos, disponibilidades, novas páginas ou dependências de acesso direto ao banco. Nenhuma tabela, endpoint ou configuração de segurança do Xano SHALL ser alterada por esta Change. As leituras SHALL ocorrer exclusivamente por APIs HTTP GET confirmadas; nenhuma credencial ou segredo SHALL ser armazenado no código versionado.

#### Scenario: Verificar ausência de integrações e operações

- **WHEN** a pessoa navega pelas três páginas
- **THEN** a aplicação não exige autenticação, não exibe registros inventados e não oferece operações habilitadas de busca ou gravação; somente as listagens GET previstas podem consultar o Xano

## ADDED Requirements

### Requirement: Configurar os endpoints de listagem externamente

O frontend SHALL obter, por configuração externa, as URLs completas das listagens GET de pacientes e profissionais. As URLs SHALL NOT ser fixadas no código versionado, e credenciais ou tokens não SHALL ser adicionados para esta integração.

#### Scenario: Executar com URLs configuradas e integração habilitada

- **WHEN** as URLs das listagens estão configuradas e a integração foi explicitamente habilitada após as verificações de segurança
- **THEN** cada página consulta somente a URL GET correspondente ao seu módulo

#### Scenario: Executar sem URL configurada

- **WHEN** a página precisa listar registros mas sua URL não está configurada
- **THEN** a interface informa claramente qual configuração está ausente, não envia requisição e não apresenta uma resposta de sucesso simulada

#### Scenario: Iniciar com integração desabilitada

- **WHEN** as URLs estão configuradas, mas `XANO_LISTAGENS_ENABLED` está ausente ou não está definido como `true`
- **THEN** as páginas informam que a integração está desabilitada e não enviam requisições HTTP

### Requirement: Tratar falhas e respostas inesperadas das listagens

O frontend SHALL tratar erro HTTP, timeout, falha de conexão, JSON inválido e JSON com estrutura incompatível com uma coleção de registros. Em qualquer falha, SHALL informar que os dados não puderam ser carregados e SHALL NOT substituir o resultado por uma coleção vazia ou por registros fictícios.

#### Scenario: O endpoint responde com erro HTTP

- **WHEN** um GET de listagem recebe status HTTP de erro
- **THEN** a página apresenta uma mensagem de falha de carregamento sem declarar lista vazia ou sucesso

#### Scenario: O endpoint excede o timeout ou não pode ser alcançado

- **WHEN** o GET excede o timeout definido ou falha por conexão
- **THEN** a página apresenta uma mensagem de indisponibilidade sem bloquear indefinidamente a interface

#### Scenario: O endpoint retorna JSON inválido ou inesperado

- **WHEN** a resposta não pode ser interpretada como uma coleção JSON com os campos previstos para o módulo
- **THEN** a página apresenta uma mensagem de resposta inesperada e não renderiza dados inventados nem trata a falha como lista vazia

### Requirement: Evitar requisições redundantes e permitir atualização

As respostas das listagens SHALL ser reutilizadas durante reruns da interface por um período de cache limitado a 60 segundos. A pessoa SHALL poder solicitar atualização explícita, invalidando o cache correspondente e buscando novamente a listagem.

#### Scenario: Reexecutar a página dentro do período de cache

- **WHEN** a página é reexecutada por uma interação da interface antes de expirarem 60 segundos e não foi solicitada atualização explícita
- **THEN** a resposta em cache é reutilizada sem um novo GET

#### Scenario: Atualizar listagem explicitamente

- **WHEN** a pessoa solicita atualização da lista de um módulo
- **THEN** o cache daquele módulo é invalidado e a página realiza um novo GET para sua listagem

### Requirement: Proteger a demonstração antes de exibir registros

Antes de habilitar a integração em um ambiente de demonstração, SHALL ser confirmado que os registros acessíveis são exclusivamente fictícios, que o ambiente e os endpoints possuem acesso adequadamente restrito e que existe autorização explícita do grupo. A ausência de credenciais em um GET bem-sucedido SHALL NOT ser considerada comprovação de segurança. O frontend SHALL manter as chamadas desabilitadas por padrão até que essa pré-condição seja atendida.

#### Scenario: Habilitar a integração em demonstração

- **WHEN** a integração é preparada para uso no ambiente de demonstração
- **THEN** a confirmação de dados fictícios e restrição adequada de acesso é registrada antes da exposição dos registros

#### Scenario: Segurança do endpoint não foi confirmada

- **WHEN** a segurança do ambiente ou a natureza fictícia dos registros não foi confirmada
- **THEN** `XANO_LISTAGENS_ENABLED` permanece ausente ou falso e nenhuma chamada real é realizada
