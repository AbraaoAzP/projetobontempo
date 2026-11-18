# consultas Specification

## Purpose

Define o comportamento observado da integracao de Consultas e Status da Consulta com APIs Xano confirmadas, mantendo explicitas as fontes de dados e preservando a persistencia local ainda necessaria.

## Requirements

### Requirement: Usar somente contratos Xano confirmados

A pagina SHALL executar operacoes de Consulta e Status somente por APIs Xano existentes cujo metodo, rota, parametros, campos e formato de resposta estejam confirmados no contrato vigente. O frontend SHALL NOT inventar ou deduzir detalhes da API a partir do SQLite, do modelo conceitual ou de outra entidade. Uma operacao sem contrato confirmado SHALL permanecer indisponivel e ser identificada como pendente.

#### Scenario: Executar operacao com contrato confirmado

- **WHEN** a operacao solicitada possui contrato Xano vigente e confirmado
- **THEN** a interface usa esse contrato sem conexao direta ao banco de dados do Xano

#### Scenario: Operacao sem contrato confirmado

- **WHEN** uma operacao, campo, relacao ou resposta nao esta definido pelo contrato confirmado
- **THEN** a interface nao presume nem chama uma rota ou formato e informa que a operacao esta pendente

### Requirement: Carregar opcoes relacionadas de fontes confirmadas

A interface SHALL carregar Pacientes, Profissionais, Especialidades e Status exclusivamente por operacoes Xano existentes e confirmadas. SHALL oferecer apenas associacoes Profissional-Especialidade confirmadas por uma fonte autoritativa prevista em contrato; nao SHALL inferir vinculos de campos textuais nem converter identificadores locais. Um catalogo remoto vazio SHALL ser apresentado como vazio, nao substituido pelo catalogo SQLite.

#### Scenario: Selecionar entidades relacionadas disponiveis

- **WHEN** as APIs confirmadas retornam opcoes validas e uma relacao Profissional-Especialidade verificavel
- **THEN** a interface oferece as opcoes remotas compativeis com a relacao confirmada

#### Scenario: Relacao ou catalogo indisponivel

- **WHEN** o contrato nao fornece uma fonte confirmada para o catalogo ou para a relacao necessaria
- **THEN** a acao que depende dessa informacao nao e habilitada e a pendencia e informada sem inferencia local

#### Scenario: Catalogo remoto vazio

- **WHEN** uma API de catalogo confirmada retorna uma colecao vazia
- **THEN** a interface apresenta o estado vazio correspondente sem usar registros SQLite como substituicao

### Requirement: Gerenciar Consultas e seus status conforme o contrato

A pagina SHALL oferecer cadastro, consulta individual, edicao e exclusao de Consulta pelas operacoes Xano confirmadas. SHALL carregar Pacientes, Profissionais, Especialidades e Status somente de APIs remotas validas e SHALL permitir uma referencia somente quando sua entidade existir e o vinculo Profissional-Especialidade estiver confirmado. SHALL validar campos obrigatorios, data, horario e sobreposicao antes da escrita e SHALL considerar todas as garantias definitivas de integridade dependentes do backend ate serem comprovadas por contrato. Erros retornados pela API SHALL ser apresentados como falha; a interface SHALL NOT declarar sucesso, integridade ou persistencia sem resposta compativel.

#### Scenario: Listar e apresentar consultas remotas

- **WHEN** a operacao confirmada de listagem retorna consultas em formato compativel com seu contrato
- **THEN** a interface apresenta os registros retornados, sem consultar ou combinar registros locais

#### Scenario: Cadastrar ou alterar consulta

- **WHEN** a pessoa envia uma operacao CRUD habilitada com os dados exigidos pelo contrato confirmado
- **THEN** a interface envia somente os campos e valores previstos no contrato e comunica o resultado efetivamente recebido

#### Scenario: Atualizar status de consulta

- **WHEN** a pessoa escolhe uma consulta e um status oferecido pelo catalogo remoto confirmado
- **THEN** a interface executa somente a operacao de atualizacao de status definida no contrato e apresenta seu resultado ou erro

#### Scenario: Backend rejeita operacao ou regra

- **WHEN** a API rejeita uma operacao, inclusive por referencia, conflito ou transicao
- **THEN** a interface apresenta a falha sem declarar sucesso nem afirmar garantias alem das documentadas pelo backend

#### Scenario: Cadastro completo confirmado

- **WHEN** a pessoa envia uma consulta com paciente, profissional, especialidade vinculada, status, data e horario validos
- **THEN** a interface envia POST ao Xano somente quando a escrita estiver habilitada e apresenta o resultado efetivamente recebido

#### Scenario: Consulta individual por identificador

- **WHEN** a pessoa solicita uma consulta por ID
- **THEN** a interface executa GET por ID e apresenta ou rejeita o registro sem combinar fontes locais

#### Scenario: Editar consulta existente

- **WHEN** a pessoa altera uma consulta e envia campos validos
- **THEN** a interface executa PATCH com a representacao confirmada pelo contrato e comunica a resposta ou o erro

#### Scenario: Excluir consulta com confirmacao

- **WHEN** a pessoa cancela ou nao confirma a exclusao
- **THEN** nenhuma operacao DELETE e enviada

- **WHEN** a pessoa confirma a exclusao e a escrita esta habilitada
- **THEN** a interface envia DELETE somente para o ID selecionado e informa sucesso ou falha conforme a resposta

### Requirement: Apresentar falhas e estados sem mascarar a origem

A interface SHALL distinguir configuracao ou habilitacao ausente, lista vazia, falha HTTP/transporte e resposta incompativel com o contrato. Em caso de falha, SHALL informar que os dados remotos nao puderam ser carregados ou alterados; SHALL NOT apresentar a falha como lista vazia, sucesso ou dados locais.

#### Scenario: Integracao sem configuracao ou desabilitada

- **WHEN** falta configuracao necessaria ou a integracao esta desabilitada
- **THEN** a interface informa a condicao e nao envia a requisicao correspondente

#### Scenario: Erro HTTP ou de transporte

- **WHEN** a API retorna erro HTTP ou ocorre falha de transporte
- **THEN** a interface apresenta o erro sem sucesso simulado nem fallback SQLite

#### Scenario: Resposta incompativel com o contrato

- **WHEN** a resposta nao corresponde ao formato confirmado da operacao
- **THEN** a interface informa a incompatibilidade e nao renderiza dados como se fossem validos

### Requirement: Preservar dados locais e a fonte do Dashboard

A integracao SHALL NOT migrar, sincronizar, sobrescrever ou excluir registros SQLite. A pagina Consultas SHALL NOT consultar ou usar SQLite como fallback em nenhum estado de configuracao ou falha. Enquanto o Dashboard depender dos dados locais, SHALL continuar consultando o SQLite e identificando esses indicadores e listagens como locais. Esta mudanca SHALL NOT remover o arquivo, schema, servico ou inicializacao necessarios ao Dashboard.

#### Scenario: Consultar a pagina apos habilitar Xano

- **WHEN** a pagina Consultas usa uma API Xano confirmada e habilitada
- **THEN** as operacoes da pagina nao combinam resultados Xano com consultas ou status SQLite

#### Scenario: Preservar dados e dependencia do Dashboard

- **WHEN** a integracao de Consultas e habilitada
- **THEN** os registros e a infraestrutura SQLite permanecem intactos e o Dashboard continua apresentando sua fonte local identificada

### Requirement: Isolar testes de chamadas remotas reais

Os testes automatizados SHALL usar dados sinteticos e transporte HTTP simulado para operacoes de Consulta e Status. SHALL NOT enviar escritas reais ao Xano durante testes automatizados.

#### Scenario: Testar operacoes sem rede

- **WHEN** os testes automatizados verificam operacoes validas, estados vazios e falhas
- **THEN** todas as respostas vem do transporte simulado e nenhuma mutacao remota e enviada
