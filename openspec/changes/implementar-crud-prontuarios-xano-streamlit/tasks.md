## 1. Configuração e contrato do cliente

- [x] 1.1 Adicionar ao `XanoSettings` a base URL e os caminhos confirmados de
  Prontuários para coleção e item; verificar configuração externa e modo
  dos arquivos sem alteração de modo.
- [x] 1.2 Adicionar flags externas `XANO_PRONTUARIOS_API_ENABLED` e
  `XANO_PRONTUARIOS_WRITE_ENABLED`, ambas desabilitadas por padrão; verificar
  que nenhuma requisição ocorre sem habilitação explícita.
- [x] 1.3 Implementar no `XanoClient` GET da coleção e GET por ID de Prontuário;
  validar tipos dos campos confirmados e retornar lista vazia somente para
  coleção vazia compatível.
- [x] 1.4 Implementar no `XanoClient` POST, PATCH e DELETE de Prontuário usando
  os cinco endpoints confirmados; verificar payloads, respostas e erros HTTP
  com transporte simulado.

## 2. Validação e referências

- [x] 2.1 Validar `prontuario_id`, `paciente_id` e `profissional_id` como
  inteiros positivos; verificar rejeição de booleanos, zero e negativos.
- [x] 2.2 Aceitar `numero_prontuario` e `observacoes` conforme texto opcional
  confirmado pelo contrato, sem declarar unicidade ou obrigatoriedade física;
  verificar trim de espaços externos e preservação de `null`.
- [x] 2.3 Carregar Pacientes e Profissionais pelas APIs existentes e oferecer
  somente IDs presentes nos catálogos; verificar referência inexistente bloqueada
  sem consulta SQLite.

## 3. Página Streamlit

- [x] 3.1 Criar `frontend/pages/5_Prontuarios.py` com cabeçalho, estados vazios,
  configuração desabilitada e falhas HTTP; verificar que não importa ou consulta
  SQLite.
- [x] 3.2 Implementar formulário de cadastro com Paciente, Profissional,
  `numero_prontuario` e `observacoes`; verificar que POST usa somente campos
  confirmados e escrita habilitada.
- [x] 3.3 Implementar consulta individual por ID e preenchimento seguro do
  formulário de edição; verificar que PATCH envia somente campos alterados.
- [x] 3.4 Implementar exclusão com seleção e confirmação explícita; verificar
  cancelamento, sucesso e falha HTTP sem mensagem de sucesso fictícia.
- [x] 3.5 Integrar a página à navegação em `frontend/app.py` sem alterar
  desnecessariamente layout, Dashboard ou páginas existentes.

## 4. Cache e consistência

- [x] 4.1 Adicionar cache de listagem e consulta individual de Prontuários,
  preservando tratamento explícito de HTTP 429 e incompatibilidade.
- [x] 4.2 Invalidar os caches de Prontuários após POST, PATCH ou DELETE
  bem-sucedido; verificar que falhas não invalidam o cache como sucesso.

## 5. Testes simulados

- [x] 5.1 Adicionar testes HTTP simulados para GET coleção, GET por ID, POST,
  PATCH, DELETE, IDs inválidos, coleção vazia e respostas incompatíveis.
- [x] 5.2 Adicionar testes Streamlit simulados para integração desabilitada,
  cadastro, consulta individual, edição, exclusão confirmada/cancelada,
  referência inexistente e falha HTTP.
- [x] 5.3 Adicionar teste de cache após mutação bem-sucedida e após falha;
  verificar que nenhum teste envia POST/PATCH/DELETE real ao Xano.
- [x] 5.4 Executar os testes específicos e toda a suíte local com o ambiente
  virtual existente; registrar contagem final e nenhum erro de sintaxe.

## 6. Documentação e validação

- [x] 6.1 Atualizar `frontend/README.md` com a URL de Prontuários, os cinco
  endpoints confirmados, as novas flags e a exclusão de Registro de Atendimento.
- [x] 6.2 Atualizar [tasks.md] somente após tarefas efetivamente verificadas
  e revisar `git diff`/`git status` sem alterar alterações anteriores ou stash.
- [x] 6.3 Executar `openspec validate implementar-crud-prontuarios-xano-streamlit --strict --no-interactive`
  e corrigir somente pendências desta Change.
- [x] 6.4 Revisar o diff final e listar somente arquivos elegíveis para futuro
  staging seletivo; não executar staging, commit, push ou archive nesta etapa
  de implementação.
