## Purpose

Define o comportamento observável da integração de Consultas e Status da Consulta com APIs Xano confirmadas, mantendo explícitas as fontes de dados e preservando a persistência local ainda necessária.

## ADDED Requirements

### Requirement: Usar somente contratos Xano confirmados

A página SHALL executar operações de Consulta e Status somente por APIs Xano existentes cujo método, rota, parâmetros, campos e formato de resposta estejam confirmados no contrato vigente. O frontend SHALL NOT inventar ou deduzir detalhes da API a partir do SQLite, do modelo conceitual ou de outra entidade. Uma operação sem contrato confirmado SHALL permanecer indisponível e ser identificada como pendente.

#### Scenario: Executar operação com contrato confirmado

- **WHEN** a operação solicitada possui contrato Xano vigente e confirmado
- **THEN** a interface usa esse contrato sem conexão direta ao banco de dados do Xano

#### Scenario: Operação sem contrato confirmado

- **WHEN** uma operação, campo, relação ou resposta não está definido pelo contrato confirmado
- **THEN** a interface não presume nem chama uma rota ou formato e informa que a operação está pendente

### Requirement: Carregar opções relacionadas de fontes confirmadas

A interface SHALL carregar Pacientes, Profissionais, Especialidades e Status exclusivamente por operações Xano existentes e confirmadas. SHALL oferecer apenas associações Profissional–Especialidade confirmadas por uma fonte autoritativa prevista em contrato; não SHALL inferir vínculos de campos textuais nem converter identificadores locais. Um catálogo remoto vazio SHALL ser apresentado como vazio, não substituído pelo catálogo SQLite.

#### Scenario: Selecionar entidades relacionadas disponíveis

- **WHEN** as APIs confirmadas retornam opções válidas e uma relação Profissional–Especialidade verificável
- **THEN** a interface oferece as opções remotas compatíveis com a relação confirmada

#### Scenario: Relação ou catálogo indisponível

- **WHEN** o contrato não fornece uma fonte confirmada para o catálogo ou para a relação necessária
- **THEN** a ação que depende dessa informação não é habilitada e a pendência é informada sem inferência local

#### Scenario: Catálogo remoto vazio

- **WHEN** uma API de catálogo confirmada retorna uma coleção vazia
- **THEN** a interface apresenta o estado vazio correspondente sem usar registros SQLite como substituição

### Requirement: Gerenciar Consultas e seus status conforme o contrato

A página SHALL oferecer as operações CRUD de Consulta e atualização de Status que estejam definidas pelos contratos Xano confirmados para esta integração. A interface SHALL usar os valores e campos efetivamente retornados ou aceitos por esses contratos, sem fixar campos, formatos ou valores de status presumidos. Erros retornados pela API SHALL ser apresentados como falha; a interface SHALL NOT declarar que uma regra de integridade, transição, conflito ou persistência é garantida pelo Xano sem evidência contratual.

#### Scenario: Listar e apresentar consultas remotas

- **WHEN** a operação confirmada de listagem retorna consultas em formato compatível com seu contrato
- **THEN** a interface apresenta os registros retornados, sem consultar ou combinar registros locais

#### Scenario: Cadastrar ou alterar consulta

- **WHEN** a pessoa envia uma operação CRUD habilitada com os dados exigidos pelo contrato confirmado
- **THEN** a interface envia somente os campos e valores previstos no contrato e comunica o resultado efetivamente recebido

#### Scenario: Atualizar status de consulta

- **WHEN** a pessoa escolhe uma consulta e um status oferecido pelo catálogo remoto confirmado
- **THEN** a interface executa somente a operação de atualização de status definida no contrato e apresenta seu resultado ou erro

#### Scenario: Backend rejeita operação ou regra

- **WHEN** a API rejeita uma operação, inclusive por referência, conflito ou transição
- **THEN** a interface apresenta a falha sem declarar sucesso nem afirmar garantias além das documentadas pelo backend

### Requirement: Apresentar falhas e estados sem mascarar a origem

A interface SHALL distinguir configuração ou habilitação ausente, lista vazia, falha HTTP/transporte e resposta incompatível com o contrato. Em caso de falha, SHALL informar que os dados remotos não puderam ser carregados ou alterados; SHALL NOT apresentar a falha como lista vazia, sucesso ou dados locais.

#### Scenario: Integração sem configuração ou desabilitada

- **WHEN** falta configuração necessária ou a integração está desabilitada
- **THEN** a interface informa a condição e não envia a requisição correspondente

#### Scenario: Erro HTTP ou de transporte

- **WHEN** a API retorna erro HTTP ou ocorre falha de transporte
- **THEN** a interface apresenta o erro sem sucesso simulado nem fallback SQLite

#### Scenario: Resposta incompatível com o contrato

- **WHEN** a resposta não corresponde ao formato confirmado da operação
- **THEN** a interface informa a incompatibilidade e não renderiza dados como se fossem válidos

### Requirement: Preservar dados locais e a fonte do Dashboard

A integração SHALL NOT migrar, sincronizar, sobrescrever ou excluir registros SQLite. A página Consultas SHALL usar somente a fonte Xano quando a operação remota estiver habilitada, sem fallback silencioso ao SQLite. Enquanto o Dashboard depender dos dados locais, SHALL continuar consultando o SQLite e identificando esses indicadores e listagens como locais. Esta mudança SHALL NOT remover o arquivo, schema, serviço ou inicialização necessários ao Dashboard.

#### Scenario: Consultar a página após habilitar Xano

- **WHEN** a página Consultas usa uma API Xano confirmada e habilitada
- **THEN** as operações da página não combinam resultados Xano com consultas ou status SQLite

#### Scenario: Preservar dados e dependência do Dashboard

- **WHEN** a integração de Consultas é habilitada
- **THEN** os registros e a infraestrutura SQLite permanecem intactos e o Dashboard continua apresentando sua fonte local identificada

### Requirement: Isolar testes de chamadas remotas reais

Os testes automatizados SHALL usar dados sintéticos e transporte HTTP simulado para operações de Consulta e Status. SHALL NOT enviar escritas reais ao Xano durante testes automatizados.

#### Scenario: Testar operações sem rede

- **WHEN** os testes automatizados verificam operações válidas, estados vazios e falhas
- **THEN** todas as respostas vêm do transporte simulado e nenhuma mutação remota é enviada
