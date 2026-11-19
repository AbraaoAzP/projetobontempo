## 1. Contrato do cliente Xano

- [x] 1.1 Adicionar ao XanoSettings os caminhos do recurso
  `profissional_especialidade` para POST em
  `profissional_especialidade` e DELETE em
  `profissional_especialidade/{profissional_especialidade_id}`, verificando
  que a configuração de base e os identificadores continuam preservados.
- [x] 1.2 Implementar no XanoClient criação de vínculo com payload
  `profissional_id` e `especialidade_id`, validando inteiros positivos e
  confirmando resposta compatível com `id`, `profissional_id` e
  `especialidade_id`.
- [x] 1.3 Implementar no XanoClient exclusão pelo identificador inteiro do
  vínculo, formatando o DELETE confirmado e tratando resposta 2xx sem corpo
  como sucesso sem simular persistência.
- [x] 1.4 Adicionar flag externa
  `XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED`, com padrão seguro `false`,
  e impedir POST/DELETE antes da habilitação explícita; verificar ausência de
  chamadas com a configuração desabilitada.

## 2. Gerenciamento na página de Profissionais

- [x] 2.1 Carregar profissionais, especialidades e vínculos existentes na página
  de Profissionais sem usar o campo textual legado como fonte relacional;
  verificar estados vazio, indisponível e carregado.
- [x] 2.2 Exibir os vínculos do profissional selecionado e oferecer somente
  especialidades ainda não vinculadas para criação; verificar que nenhuma
  opção duplicada é apresentada.
- [x] 2.3 Validar profissional, especialidade e par selecionado antes do POST,
  bloqueando IDs inválidos, referências inexistentes e duplicidades; verificar
  que nenhuma requisição é enviada nesses casos.
- [x] 2.4 Adicionar confirmação explícita para exclusão de vínculo e enviar
  DELETE somente após confirmação e habilitação da escrita; verificar
  cancelamento, sucesso e falha HTTP.
- [x] 2.5 Preservar o campo textual legado no CRUD atual e impedir conversão,
  migração ou inferência automática para os vínculos relacionais.

## 3. Cache e consistência

- [x] 3.1 Invalidação de cache após criação ou exclusão bem-sucedida e recarga
  da coleção de vínculos; verificar que falhas não invalidam dados por engano.
- [x] 3.2 Revisar o uso do cache e da coleção na página de Consultas; verificar
  que a especialidade só fica disponível ao profissional quando o par estiver
  presente no GET confirmado.
- [x] 3.3 Tratar respostas vazias, incompatíveis, HTTP 429 e outros erros sem
  converter a resposta em sucesso ou lista vazia; verificar mensagens explícitas.

## 4. Testes unitários simulados

- [x] 4.1 Adicionar testes de transporte para POST de vínculo válido e para
  rejeição de IDs inválidos, garantindo que nenhuma mutação é enviada quando
  a entrada é inválida.
- [x] 4.2 Adicionar testes de transporte para DELETE por identificador válido,
  resposta 2xx sem corpo, resposta HTTP incompatível e falha de transporte.
- [x] 4.3 Adicionar testes da página de Profissionais para criação, exclusão
  confirmada/cancelada, duplicidade, referência inexistente e escritas
  desabilitadas.
- [x] 4.4 Adicionar teste de invalidação de cache após mutação bem-sucedida e
  ausência de invalidação após falha.
- [x] 4.5 Executar a suíte relevante do frontend com transporte e Streamlit
  simulados e confirmar que não há requisições remotas reais nem alteração
  de arquivos locais não relacionados.

## 5. Documentação e validação

- [x] 5.1 Atualizar `frontend/README.md` com a nova flag de escrita, os contratos
  POST/DELETE confirmados e a regra de que unicidade composta e integridade
  referencial ainda não foram confirmadas.
- [x] 5.2 Revisar `git diff` e `git status` antes da conclusão para confirmar que
  somente os arquivos planejados da Change foram modificados.
- [x] 5.3 Executar `openspec validate gerenciar-vinculos-profissional-especialidade --strict --no-interactive`
  e corrigir somente pendências desta Change.
- [x] 5.4 Verificar que a página de Consultas continua funcionando sem
  migração automática, sem uso do campo textual como vínculo e sem alteração
  remota além das operações autorizadas.
