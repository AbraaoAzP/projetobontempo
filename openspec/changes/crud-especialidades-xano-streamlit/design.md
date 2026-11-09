## Context

Consulte [proposal.md](./proposal.md) e as deltas em `specs/`. A página `frontend/pages/3_Especialidades.py` chama somente `create_specialty` e `list_specialties` em `frontend/services/database.py`. O schema SQLite local contém `especialidades(id, nome, nome_normalizado)`, com unicidade em `nome_normalizado`; `consultas.especialidade_id` e `profissional_especialidade.especialidade_id` têm referências restritivas a esse catálogo. A página Consultas continua lendo Especialidades do SQLite.

O cliente `frontend/services/xano.py` oferece CRUD tipado para Pacientes e Profissionais, mas não contém recurso, configuração ou endpoint de Especialidades. Os arquivos `xano/table/` e `xano/api/` não incluem schema nem rotas de Especialidades. A Change `modelar-especialidades-consultas-xano` propõe o catálogo e vínculos como modelo conceitual, não confirma contratos Xano implementados ou publicados. A Change CRUD existente registra um diagnóstico anterior, em 2026-11-06, de `v1` como live e `allow_push: false`; o destino e as condições atuais devem ser verificados antes de qualquer escrita ou publicação.

## Goals / Non-Goals

**Goals:**

- Migrar as operações da página Especialidades para APIs Xano confirmadas, reutilizando o padrão de cliente, configuração externa, validação, erros e testes simulados já existente.
- Fazer da confirmação do contrato real e dos controles de acesso uma pré-condição para integrar ou habilitar chamadas reais.
- Preservar o SQLite e a inicialização usados por Consultas, sem cópia de registros; o descompasso temporário do catálogo é aceito e explícito.

**Non-Goals:**

- Definir rotas, métodos, payloads, nomes de variáveis, campos remotos ou políticas de autorização sem evidência do contrato.
- Alterar `frontend/app.py`, migrar Consultas ou seus dados, sincronizar/duplicar Especialidades no SQLite, remover a dependência SQLite ou apagar o banco local.
- Implementar login, perfis Admin/Médico, escrita remota, alteração da branch `v1` live ou publicação de XanoScript sem autorização explícita.

## Decisions

### Definir um contrato local explícito sem afirmar que está publicado

O inventário somente de leitura não encontrou schema nem endpoints Xano para Especialidades. Para permitir preparar os arquivos locais, esta Change define o contrato pretendido seguindo a organização de API já usada pelos módulos existentes, sem afirmar que o contrato está publicado:

| Operação | Método e rota locais propostos | Entrada | Resposta de sucesso |
|---|---|---|---|
| Listar | `GET /especialidades` | Nenhuma | Lista de `{id, nome}` |
| Consultar | `GET /especialidade/{especialidade_id}` | `especialidade_id` inteiro positivo | `{id, nome}` |
| Cadastrar | `POST /especialidades` | `{nome}` | `{id, nome}` |
| Atualizar | `PATCH /especialidade/{especialidade_id}` | `{nome}` opcional; ausente preserva o nome | `{id, nome}` |
| Excluir | `DELETE /especialidade/{especialidade_id}` | `especialidade_id` inteiro positivo | Atualmente bloqueado: erro HTTP de conflito, sem alteração. Só poderá excluir após as relações e as garantias referenciais estarem implementadas e verificadas. |

O grupo local será `Especialidades`; o nome do recurso e as rotas seguem o padrão plural para coleção e singular para item dos endpoints existentes. O schema terá `id int`, `nome text` obrigatório com trim, e `nome_normalizado text` derivado por trim e conversão para minúsculas, com índice único. A resposta pública omite `nome_normalizado`. Entradas vazias serão rejeitadas e duplicidades normalizadas serão rejeitadas; a unicidade do índice protege também contra concorrência. O PATCH aceitará apenas `nome` e não permitirá nome vazio.

Esse contrato é uma definição para os scripts locais e futura integração Streamlit. O Xano remoto continua sem tabela/API correspondente e a única branch verificada é live com `allow_push: false`. Nenhuma URL de grupo, credencial ou política de autorização é declarada como confirmada. Não executar `workspace push` nem chamadas de escrita para validar os scripts.

Alternativa considerada: assumir que os endpoints análogos de Pacientes/Profissionais já existem para Especialidades. Rejeitada porque o inventário remoto e os arquivos locais não os contêm.

### Estender o serviço HTTP existente sem acoplar a página às rotas

Após confirmar o contrato, adicionar Especialidades ao cliente tipado e reutilizar seu transporte, timeout, configuração externa, validação de resposta e exceções explícitas. A página deverá chamar operações do serviço, sem construir URLs ou acessar SQLite. Configuração ausente, API desabilitada, erro HTTP, resposta malformada e falha de transporte não podem parecer lista vazia ou sucesso.

Manter a separação entre habilitar integração e configurar URL/credenciais: nenhum token ou URL sensível será versionado, e a chamada real só poderá ser habilitada depois de aprovar as condições de acesso e a natureza dos dados do ambiente. Não adicionar dependência de transporte; `requests` já está declarado.

Alternativa considerada: duplicar `requests` na página ou manter CRUD SQLite como fallback. Rejeitada porque duplica configuração/tratamento de erros e pode apresentar como atual um catálogo diferente do Xano.

### Migrar a tela, não os registros, nesta Change

Não copiar nem apagar dados SQLite. A mudança tira as operações de Especialidades da página administrativa, mas mantém `frontend/services/database.py`, o schema local e sua inicialização enquanto Consultas depender deles. Conforme decisão do solicitante, Consultas continua consultando seu catálogo SQLite; Especialidades criadas ou alteradas no Xano não aparecem nessa tela local até uma Change de migração de Consultas. Essa diferença é temporária e não será ocultada por sincronização implícita.

Alternativa considerada: sincronizar ou duplicar gravações no SQLite para manter os dois catálogos alinhados. Rejeitada por criar dois caminhos de escrita e exigir política de reconciliação/identificadores ainda inexistente.

### Preservar validação e integridade do catálogo

Manter o comportamento local já observado para o nome: obrigatório, trim e unicidade sem distinção de caixa, com acentos preservados. O backend deverá impor a validação e unicidade para evitar duplicidade concorrente; a interface apenas valida antecipadamente para orientar a pessoa. Não acrescentar limite de tamanho não documentado. Antes de implementar essa regra no Xano, confirmar a forma suportada pelo contrato e pelo ambiente.

Exigir confirmação explícita na interface para exclusão. Como as relações `profissional_especialidade` e `consulta` ainda não existem no Xano, o endpoint DELETE local falhará fechado: responderá conflito e não apagará qualquer registro até que as relações e a integridade restritiva possam ser verificadas. Quando a proteção for implementada em etapa posterior, referências existentes deverão bloquear a exclusão, sem cascata destrutiva. A interface futura deverá apresentar o resultado real do endpoint.

### Testar localmente sem operações remotas

Usar respostas e transporte simulados para testar listagem vazia e preenchida, consulta por ID, cadastro, edição, duplicidade, exclusão confirmada/cancelada, conflito por referência, configuração ausente, erro HTTP, timeout e resposta inválida. Usar `AppTest` para os fluxos Streamlit e manter dados fictícios. Nenhum teste automatizado desta Change deverá chamar Xano ou escrever/apagar registros remotos.

## Risks / Trade-offs

- [O Xano publicado não contém o catálogo ou todas as operações necessárias] → tratar inventário autorizado como pré-condição; não inventar rotas nem habilitar chamada real; solicitar uma decisão/Change própria se for preciso criar recursos.
- [A única branch reportada anteriormente é live e `allow_push` está desabilitado] → confirmar destino e autorização antes de qualquer ação; não escrever em `v1`, não usar push amplo e não publicar XanoScript sem autorização explícita.
- [O contrato local de rotas ainda não existe no Xano remoto] → documentá-lo como proposto, manter a integração Streamlit bloqueada e não apresentar scripts locais como APIs disponíveis.
- [O endpoint DELETE não tem tabelas de referência para provar que uma especialidade está sem uso] → retornar conflito sem mutação até que as relações e a proteção de exclusão estejam implementadas e verificadas.
- [Consultas apresenta Especialidades locais desatualizadas em relação ao Xano] → manter o descompasso conhecido, sem sincronização implícita, e incluir a migração de Consultas em Change posterior.
- [Uma especialidade referenciada não pode ser removida] → backend deve preservar referências e responder com falha explícita; interface confirma a ação e informa a restrição.
- [A ausência de login não comprova autorização das APIs] → não habilitar chamadas reais até a política de acesso efetiva ser verificada e aprovada no ambiente de destino.

## Migration Plan

1. Fazer o inventário Xano autorizado e somente de leitura; documentar contrato, validações, controles de acesso e destino não-live disponível. Interromper a habilitação se qualquer pré-condição não for confirmada.
2. Com o contrato confirmado, preparar serviço tipado e página Streamlit; manter chamadas reais desabilitadas, sem editar `frontend/app.py`, o schema/inicialização SQLite ou os dados locais.
3. Executar testes automatizados somente com mocks e dados fictícios; verificar operações, validações, erros, confirmação de exclusão e preservação do fluxo SQLite de Consultas.
4. Habilitar ou validar qualquer chamada de escrita somente após autorização explícita, usando o destino e os registros de teste aprovados; nenhuma publicação Xano faz parte automática desta Change.
5. Migrar Consultas e decidir a destinação dos dados SQLite em Change posterior. Até lá, manter visível e documentado que as duas telas consultam catálogos distintos.
