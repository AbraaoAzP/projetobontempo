## Context

Consulte [proposal.md](./proposal.md) para a motivação e o escopo. A implementação atual já oferece GET da coleção, GET por ID, catálogos e formulários preparatórios, mas mantém cadastro, edição e exclusão desabilitados. A página também possui um ramo legado SQLite que deve ser removido.

Os contratos conhecidos confirmam POST, PATCH e DELETE de Consulta, mas o frontend ainda não pode declarar a integridade final do backend sobre conflito, duração ou autorização. O POST usa referências positivas e timestamp Unix em milissegundos; PATCH aceita campos parciais; DELETE usa o identificador da consulta. Até confirmação prática do ambiente, as escritas permanecem desabilitadas.

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

### Validação remota controlada em 2026-11-18

Após autorização explícita, um registro sintético foi criado e removido pelo CRUD real do Xano. POST e GET confirmaram criação e leitura; PATCH e GET confirmaram atualização; DELETE recebeu resposta 2xx aceita pelo cliente; um GET posterior recebeu HTTP 404 real, confirmando a remoção. O registro temporário ID 1 foi excluído ao final. Nenhum registro preexistente foi alterado e a flag persistida de escrita permaneceu `false`. Os resultados não comprovam autorização por perfil, garantia backend de referência, disponibilidade, duração ou conflito de agenda.

## Fontes dos catálogos e relação confirmada

Os scripts Xano presentes no repositório documentam estas respostas de leitura:

| Catálogo | Fonte no repositório | Campos projetados |
|---|---|---|
| Pacientes | `xano/api/pacientes/pacientes_GET.xs` | `id`, `nome`, `telefone`, `email` |
| Profissionais | `xano/api/profissionais/profissionais_GET.xs` | `id`, `nome`, `telefone`, `email`, `especialidade` |
| Especialidades | `xano/api/especialidades/especialidades_GET.xs` | `id`, `nome` |
| Status da Consulta | Contrato GET inspecionado pelo grupo no painel; não há script correspondente no snapshot `xano/api/` | `id`, `nome`, `created_at` |

| Profissional–Especialidade | Grupo `Profissional Especialidades`, GET `/profissional_especialidade` | `id`, `profissional_id`, `especialidade_id` |

O campo `profissional.especialidade` continua sendo texto legado e não será
convertido ou comparado com nomes do catálogo. A associação confirmada usa a
tabela intermediária `profissional_especialidade`; o cliente exige inteiros
positivos nos três identificadores, rejeita pares duplicados e a interface
bloqueia associações cujas referências não estejam nos catálogos carregados.
`XANO_PROFISSIONAL_ESPECIALIDADES_BASE_URL` e
`XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED=true` são obrigatórios para a
leitura; sem eles, o seletor permanece desabilitado.

## Leituras repetidas e consistência do Dashboard

As leituras de catálogos e vínculos usados pela página Consultas devem ser
armazenadas em cache curto no frontend para evitar reruns do Streamlit e reduzir
chamadas redundantes ao Xano. Uma resposta HTTP 429 não deve ser convertida em
lista vazia nem repetida automaticamente; permanece visível como erro.

O Dashboard não deve exigir `XANO_AUTHORIZATION` para endpoints públicos
confirmados pelo mesmo contrato usado pelas páginas Pacientes e
Profissionais. Ele continua com indicadores locais para Consultas e Status,
identificados como SQLite, sem sincronização com a página remota de Consultas.

## Goals / Non-Goals

**Goals:**

- Entregar um CRUD completo da página Consultas usando exclusivamente APIs Xano.
- Usar somente pacientes, profissionais, especialidades, status e vínculos retornados pelo Xano.
- Validar referências, campos obrigatórios, data, horário e conflito no frontend até que uma garantia funcional equivalente exista no backend.
- Preservar o banco SQLite enquanto houver dependências reais fora da página Consultas.

**Non-Goals:**

- Criar ou alterar endpoints, tabelas, permissões, scripts ou dados no Xano.
- Executar operações remotas sem autorização explícita.
- Implementar autenticação, prontuários ou remover SQLite globalmente.
- Presumir conflito, disponibilidade ou duração não confirmados pelo backend.

## Decisions

### Usar contratos Xano como única fonte para operações remotas

Reutilizar `frontend/services/xano.py`. POST, PATCH e DELETE só serão habilitados depois da confirmação dos detalhes reais da API e da autorização remota. Operação sem contrato verificável permanece indisponível.

Alternativa considerada: derivar a API dos campos e regras da página SQLite ou da Change de modelagem. Foi rejeitada porque o modelo local e a especificação conceitual não comprovam o contrato remoto.

### Carregar catálogos e relações somente por fonte autoritativa

Pacientes, Profissionais, Especialidades, Status e a relação
Profissional–Especialidade usados nos formulários devem vir de APIs existentes
confirmadas. Um campo textual legado não será interpretado como identificador,
e valores de status locais não serão tratados como catálogo remoto.

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
- [A resposta da relação conter referências inválidas ou duplicadas] → rejeitar a resposta ou bloquear as opções inválidas; não inferir vínculos pelo campo textual legado.
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
