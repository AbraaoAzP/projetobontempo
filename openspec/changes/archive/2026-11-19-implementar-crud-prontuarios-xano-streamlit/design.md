## Context

O grupo confirmou o contrato remoto do grupo Xano `Prontuarios`:

- base `https://x8ki-letl-twmt.n7.xano.io/api:MKXobaym`;
- GET/POST em `/prontuario`;
- GET/PATCH/DELETE em `/prontuario/{prontuario_id}`;
- campos `id`, `created_at`, `paciente_id`, `profissional_id`,
  `numero_prontuario`, `observacoes` e `data_da_atualizacao`;
- Swagger declara que a autenticação não é exigida nesta API.

GET `/prontuario` já respondeu HTTP 200 com coleção vazia; `/prontuario/1`
retornou HTTP 404 em ausência de registro. Não foram confirmados endpoints ou
campos de Registro de Atendimento, obrigatoriedade física dos campos,
unicidade, relacionamento físico ou autorização por perfil.

O frontend já utiliza `XanoSettings`, `XanoClient`, cache Streamlit e validação
de respostas em módulos semelhantes. Pacientes e Profissionais possuem operações
GET existentes que podem fornecer as referências da interface.

## Goals / Non-Goals

**Goals:**

- Implementar cliente HTTP para os cinco endpoints confirmados de Prontuários.
- Disponibilizar listagem, consulta, criação, edição e exclusão no Streamlit.
- Usar somente referências positivas de Pacientes e Profissionais carregadas
  por suas APIs existentes.
- Tratar lista vazia, transporte, HTTP, resposta incompatível e erro de
  exclusão sem sucesso fictício.
- Manter escritas desabilitadas por padrão e invalidar cache após mutação
  bem-sucedida.
- Testar todas as operações com transporte HTTP e componentes simulados.

**Non-Goals:**

- Implementar Registro de Atendimento ou campos clínicos não confirmados.
- Presumir autenticação, perfis, autoria ou autorização no backend.
- Implementar fallback SQLite.
- Migrar dados locais ou publicar scripts Xano.
- Definir unicidade de número de prontuário, cardinalidade clínica,
  retenção ou regras de exclusão não confirmadas.

## Decisions

### Representar Prontuários como recurso independente

Adicionar `prontuarios` ao modelo interno do `XanoClient`, com base externa
separada, coleção `/prontuario` e item
`/prontuario/{prontuario_id}`.

Cada resposta deverá ser validada como objeto compatível com pelo menos os
campos confirmados utilizados pelo frontend. Campos internos ou não confirmados
pela validação não serão considerados inventados pela interface.

Alternativa considerada: reutilizar métodos genéricos para recursos existentes.
Foi rejeitada apenas como implementação de baixo controle; o cliente poderá
reutilizar o transporte HTTP comum, mas a validação do recurso será específica.

### Campos editáveis do MVP

O formulário aceitará referências existentes de Paciente e Profissional,
`numero_prontuario` e `observacoes`.

`paciente_id` e `profissional_id` serão enviados somente como inteiros positivos.
`numero_prontuario` será removido de espaços externos e poderá ser vazio somente
se o backend aceitar; não será declarada unicidade física.
`observacoes` será tratada como texto opcional.

`created_at` e `data_da_atualizacao` serão exibidos como metadados quando
presentes, mas não serão usados como campos obrigatórios de criação pelo
frontend. PATCH enviará somente campos efetivamente alterados, sem inventar
valores para os metadados.

Alternativa considerada: exigir todos os campos de resposta no POST. Foi
rejeitada porque o OpenAPI não confirmou obrigatoriedade física nem os
timestamps como inputs obrigatórios.

### Especificar habilitação separada

Adicionar `XANO_PRONTUARIOS_API_ENABLED` e
`XANO_PRONTUARIOS_WRITE_ENABLED`, ambas desabilitadas por padrão.

GET só será executado com API habilitada e URL configurada. POST/PATCH/DELETE
exigem API e escrita habilitadas.

Alternativa considerada: reutilizar `XANO_API_ENABLED`. Foi rejeitada porque
leitura e escrita de Prontuários precisam de gate próprio e não devem ser
iniciadas pela habilitação geral de outros módulos.

### Usar Pacientes e Profissionais confirmados como opções

O frontend carregará Pacientes e Profissionais pelas APIs já existentes.
Somente IDs presentes nas respostas serão oferecidos. O campo não será
preenchido com dados SQLite.

Alternativa considerada: aceitar nomes textuais ou IDs digitados. Foi rejeitada
porque isso poderia esconder referências inexistentes e não usa uma fonte
autoritativa.

### Cache e exclusão

Após POST, PATCH ou DELETE bem-sucedido, limpar o cache da coleção e da consulta
individual de Prontuários.

A exclusão exigirá confirmação explícita e enviará somente o
`prontuario_id` selecionado. O frontend não presumirá sucesso sem resposta
compatível.

## Risks / Trade-offs

- [Obrigatoriedade não confirmada no contrato] → aceitar somente validação
  mínima do frontend e confirmar erro do backend; não declarar garantia física.
- [Faltarem FKs ou unicidade no backend] → não afirmar integridade além das
  referências presentes nos catálogos; bloquear referências inválidas no cliente.
- [PATCH alterar metadados automaticamente] → enviar somente campos modificados
  e não criar payload com timestamps inventados.
- [API pública sem login] → manter dados sintéticos neste MVP e não afirmar
  controle de acesso; não disponibilizar dados reais ou clínicos.
- [DELETE afetar registros dependentes] → mostrar erro HTTP e não declarar
  comportamento retentivo não confirmado.
- [Resposta divergente do OpenAPI] → validar tipos e formatos mínimos e
  informar incompatibilidade sem sucesso fictício.

## Migration Plan

1. Implementar configuração, validação e métodos HTTP no cliente.
2. Cobrir os métodos com transporte simulado.
3. Implementar a página usando Pacientes e Profissionais Xano.
4. Executar testes localmente sem POST/PATCH/DELETE remotos.
5. Antes de habilitar escritas, apresentar o plano e obter autorização.
6. Em caso de falha, desabilitar a escrita e manter leitura inexistente como
   estado explícito, sem fallback SQLite.

## Open Questions

- Quais campos são obrigatórios fisicamente no POST e no PATCH?
- O mesmo Paciente pode possuir vários Prontuários ou exatamente um?
- Existe unicidade para `numero_prontuario`?
- Quais regras existem para exclusão com dependentes?
