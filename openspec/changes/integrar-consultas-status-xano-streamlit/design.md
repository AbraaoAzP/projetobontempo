## Context

Consulte [proposal.md](./proposal.md) para a motivação e o escopo. A página Consultas e o catálogo de status ainda usam SQLite. O Dashboard também lê consultas e status locais. Os arquivos versionados de Xano não contêm definições de APIs ou tabelas para Consultas e Status da Consulta; esta ausência não contradiz contratos confirmados fora do repositório, mas seus detalhes não devem ser inferidos a partir do modelo SQLite.

Esta integração ocorre numa aplicação Streamlit sem autenticação própria. O cliente HTTP Xano existente e os padrões de configuração e testes do projeto devem ser reutilizados. Nenhuma escrita remota será executada como parte da elaboração ou validação desta Change.

## Contratos identificados no painel

Os endpoints abaixo foram informados e inspecionados pelo grupo no painel do Xano. Os endpoints inspecionados estão marcados como públicos. Essa indicação não comprova as garantias de autorização ou integridade dos dados.

| Operação | Contrato confirmado | Limites ainda não confirmados |
|---|---|---|
| `GET /consulta` | HTTP 200, `application/json`, lista de registros da tabela `consulta` | O tratamento de dados legados com referências `0` continua dependente de catálogos e validação no frontend |
| `GET /consulta/{consulta_id}` | `consulta_id` (integer); retorna o registro correspondente ao ID | Campos adicionais da resposta não usados pela interface |
| `POST /consulta` | Inputs `paciente_id`, `profissional_id`, `especialidade_id` e `status_consulta_id` (referências integer, não nulas, padrão `0`); `data_e_hora_do_agendamento` (timestamp Unix em milissegundos, não nulo, sem padrão); `observacoes` (text, aceita `null`); `created_at` é definido automaticamente; resposta configurada com a variável `consulta` | Não foram confirmadas regras de existência das referências, associação Profissional–Especialidade ou conflito de agenda |
| `PATCH /consulta/{consulta_id}` | `consulta_id` (integer); os mesmos campos editáveis; stack usa `Get All Raw Input` e `Patch Record In consulta`, selecionando as chaves recebidas; resposta configurada com a variável `consulta` | A semântica dos filtros de valores nulos/vazios e as regras de validação de referências e conflito continuam pendentes |
| `DELETE /consulta/{consulta_id}` | `consulta_id` (integer); stack exclui pelo campo `id`; sem resposta personalizada | Corpo e códigos HTTP de sucesso/erro |
| `GET /status_consulta` | HTTP 200, `application/json`, lista de objetos com `id` (integer), `nome` (string) e `created_at` (integer), conforme o painel e a leitura controlada | Valores do catálogo; campos adicionais; rotas de leitura individual ou de escrita |

O cliente valida nos registros de Consulta o ID, as quatro referências, o timestamp e, quando presente, `observacoes`; a ausência de `observacoes` permanece distinta de `null`. O timestamp é convertido entre o horário local `America/Sao_Paulo` e Unix em milissegundos. A atualização de status usa `status_consulta_id` no PATCH de Consulta; não há endpoint separado de escrita para Status.

As operações de escrita remota permanecem desabilitadas na página até a validação final. O cliente exige referências positivas e timestamp inteiro para POST, permite PATCH parcial e preserva a distinção entre campo omitido e `observacoes: null`. Isso não afirma que o Xano valide a existência das referências, o vínculo Profissional–Especialidade, transições de status ou conflitos de agenda. O formulário remoto aceita um instante, sem término/duração confirmados.

## Fontes dos catálogos e limite da relação

Os scripts Xano presentes no repositório documentam estas respostas de leitura:

| Catálogo | Fonte no repositório | Campos projetados |
|---|---|---|
| Pacientes | `xano/api/pacientes/pacientes_GET.xs` | `id`, `nome`, `telefone`, `email` |
| Profissionais | `xano/api/profissionais/profissionais_GET.xs` | `id`, `nome`, `telefone`, `email`, `especialidade` |
| Especialidades | `xano/api/especialidades/especialidades_GET.xs` | `id`, `nome` |
| Status da Consulta | Contrato GET inspecionado pelo grupo no painel; não há script correspondente no snapshot `xano/api/` | `id`, `nome`, `created_at` |

O campo `profissional.especialidade` está declarado como texto opcional e também é retornado como texto. O snapshot não contém campo `especialidade_id` na tabela Profissional, tabela de associação Profissional–Especialidade ou endpoint que retorne essa associação. Isso confirma a ausência de fonte relacional **no repositório**, não a inexistência de uma configuração remota fora dele. O texto não será convertido nem comparado com nomes do catálogo para criar uma associação. A página carrega os catálogos confirmados, mas mantém sem opções e desabilitado o seletor de Especialidade até a relação ser confirmada por contrato.

## Goals / Non-Goals

**Goals:**

- Integrar a página de Consultas e o catálogo de Status usando exclusivamente os contratos Xano existentes e confirmados.
- Manter separadas as fontes remota da página e local do Dashboard, com estados de erro explícitos e sem fallback silencioso.
- Preservar o banco, os dados e a inicialização SQLite enquanto o Dashboard ou outra dependência local ainda os utilizar.

**Non-Goals:**

- Criar ou alterar endpoints, tabelas, permissões, scripts ou dados no Xano.
- Migrar, sincronizar, excluir ou gravar dados locais nesta Change.
- Alterar o Dashboard, autenticação ou o controle de acesso do backend.
- Presumir validações ou garantias de integridade do Xano que não constem de seus contratos.

## Decisions

### Usar contratos Xano como única fonte para operações remotas

Reutilizar o cliente HTTP existente em `frontend/services/xano.py`. Antes de habilitar cada operação, registrar sua rota, método, parâmetros, campos e forma de resposta conforme a fonte contratual confirmada pelo grupo. Os artefatos desta Change não enumeram esses detalhes, pois não constam nos arquivos versionados. Operação sem contrato verificável permanece indisponível; não se presume rota, payload, resposta, relação, autenticação ou garantia do backend.

Alternativa considerada: derivar a API dos campos e regras da página SQLite ou da Change de modelagem. Foi rejeitada porque o modelo local e a especificação conceitual não comprovam o contrato remoto.

### Carregar catálogos e relações somente por fonte autoritativa

Pacientes, Profissionais, Especialidades e Status usados nos formulários devem vir de APIs existentes confirmadas. A relação Profissional–Especialidade só pode ser aplicada se o contrato fornecer uma relação identificável ou uma operação autorizada que a confirme. Um campo textual legado não será interpretado como identificador, e valores de status locais não serão tratados como catálogo remoto.

Alternativa considerada: reutilizar ou converter automaticamente os catálogos SQLite. Foi rejeitada para evitar misturar registros e identificadores de fontes diferentes.

### Não usar SQLite como fallback nem fazer dupla gravação

Com a integração habilitada, a página Consultas opera sobre a fonte Xano conforme os contratos confirmados. Ausência de configuração, resposta incompatível ou falha remota é apresentada como indisponibilidade/erro; a página não declara que a operação remota teve sucesso usando dados locais. Não haverá gravação dupla nem cópia automática. O Dashboard continua a obter seus indicadores, distribuição e agenda do SQLite local, identificados como locais, sem ser alterado por esta Change.

Alternativa considerada: fallback automático para SQLite quando o Xano falhar. Foi rejeitada porque produziria uma tela de origem ambígua e poderia ocultar falhas de persistência remota.

### Habilitar chamadas apenas com configuração externa e controles explícitos

Usar variáveis externas e controles próprios da integração, sem URLs sensíveis, tokens ou credenciais versionados. A configuração deve respeitar os requisitos de autorização descritos no contrato. A integração não implementará login nem tratará uma flag do frontend como controle de acesso. Não habilitar a operação remota em ambientes sem a configuração e a autorização exigidas.

Alternativa considerada: habilitar chamadas automaticamente pela presença de uma URL ou pelo estado do endpoint. Foi rejeitada porque isso não comprova que o acesso aos dados está autorizado ou adequado.

### Testar contratos sem tráfego ou mutações reais

Cobrir parsing, entradas e erros com transporte HTTP simulado e dados sintéticos. Testes automatizados não enviarão requisições ao Xano. Qualquer validação real de escrita permanece sujeita a autorização específica, fora desta Change de planejamento.

Alternativa considerada: testes automatizados contra ambiente publicado. Foi rejeitada por depender de rede e poder ler ou alterar dados reais.

### Migrar em etapas e manter SQLite enquanto houver dependências

Esta Change não migra nem remove o arquivo SQLite, os registros, o schema, o serviço ou a inicialização. A página pode passar a operar no Xano sem converter o acervo local. O Dashboard continua a usar o acervo local enquanto depender dele. A remoção de SQLite exige uma etapa futura separada, depois de migrar e verificar todas as dependências locais e decidir explicitamente o destino dos dados.

Alternativa considerada: remover SQLite na mesma etapa em que Consultas passa a usar o Xano. Foi rejeitada porque deixaria o Dashboard e seus dados locais sem sua fonte atual.

## Risks / Trade-offs

- [O contrato citado pelo grupo não estar disponível à implementação ou divergir do ambiente] → registrar a fonte e os detalhes verificados antes de habilitar cada operação; bloquear chamadas não comprovadas.
- [A resposta real divergir do contrato esperado] → validar a resposta e informar incompatibilidade, sem sucesso simulado nem fallback SQLite.
- [A relação de especialidade ou o catálogo de status não ser exposto por contrato confirmado] → não inferir a relação nem hardcodear o catálogo local como remoto; manter a ação dependente indisponível até existir uma fonte autorizada.
- [A tela remota e o Dashboard mostrarem acervos diferentes durante a transição] → identificar claramente o Dashboard como local e não sincronizar dados implicitamente.
- [A aplicação sem autenticação expor dados remotos] → não habilitar chamadas sem confirmação de autorização e dos requisitos do ambiente; nenhuma proteção dependerá somente da interface.
- [Remoção prematura do banco interromper o Dashboard ou perder dados] → manter schema, arquivo, dados e inicialização até Change posterior verificar todas as dependências e aprovar a migração.

## Migration Plan

1. Identificar e documentar os contratos vigentes de Consultas, Status e catálogos relacionados, incluindo a fonte oficial e requisitos de autorização; nenhum detalhe será deduzido do SQLite.
2. Implementar os mapeamentos em cima do cliente HTTP existente, com configuração externa e habilitação explícita, mantendo a integração inativa enquanto faltar contrato ou autorização.
3. Validar operações e estados com transporte simulado; não executar escritas remotas como parte dos testes.
4. Habilitar o fluxo somente após a confirmação dos contratos, configuração e autorização apropriadas. Qualquer teste remoto de escrita exige autorização específica e plano separado.
5. Para rollback, desabilitar a integração remota ou reverter a versão da aplicação sem alterar o banco local. Não usar os dados locais como fallback silencioso da tela remota.
6. Manter SQLite para o Dashboard e demais dependências; planejar sua remoção, se aprovada, em Change posterior, após migração e verificação próprias.

## Open Questions

Não há decisões de domínio remotas inferidas por este design. A identificação dos contratos e de sua fonte é uma tarefa prévia à implementação, não autorização para criar operações ausentes.
