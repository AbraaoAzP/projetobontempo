## Context

A página de Profissionais já integra cadastro, consulta, edição e exclusão de
profissionais ao Xano. O campo textual `profissional.especialidade` permanece
como contrato legado.

A página de Consultas já consulta o GET da coleção
`/profissional_especialidade` e usa os pares `profissional_id` e
`especialidade_id` para limitar as Especialidades disponíveis. Os contratos
visualmente confirmados no painel Xano acrescentam:

- `POST /profissional_especialidade`, recebendo `profissional_id` e
  `especialidade_id` como inteiros e retornando o registro criado;
- `DELETE /profissional_especialidade/{profissional_especialidade_id}`,
  recebendo o identificador inteiro do vínculo e excluindo pelo campo `id`,
  sem corpo configurado na resposta.

A unicidade composta no banco, chaves estrangeiras e comportamento de integridade
referencial ainda não foram confirmados no ambiente Xano.

## Goals / Non-Goals

**Goals:**

- Implementar POST e DELETE para vínculos no cliente Xano existente.
- Permitir gerenciar os vínculos na página de Profissionais.
- Bloquear IDs inválidos e pares duplicados no frontend.
- Atualizar o cache de vínculos após mutações bem-sucedidas.
- Cobrir os contratos com transporte HTTP e componentes Streamlit simulados.
- Preservar o campo textual legado e o consumo atual da página de Consultas.

**Non-Goals:**

- Migrar automaticamente valores textuais para o catálogo;
- Alterar o campo ou os contratos atuais de Profissionais;
- Implementar autenticação, perfis ou autorização;
- Alterar o ambiente Xano live;
- Remover o SQLite ou executar mutações remotas reais;
- Confirmar ou implementar regras físicas ainda não verificadas no Xano.

## Decisions

### Adicionar operações específicas ao XanoClient

O cliente deverá oferecer operações para criar e excluir vínculos, reutilizando
os transportes, tratamento de HTTP e validação já usados pelos demais recursos.

O POST deverá validar antes da chamada que os dois IDs sejam inteiros positivos.
O DELETE deverá validar o ID inteiro positivo do vínculo e formatar
`profissional_especialidade/{profissional_especialidade_id}`.

A resposta do POST deverá ser compatível com `id`, `profissional_id` e
`especialidade_id`. O DELETE deverá aceitar uma resposta 2xx compatível com a
ausência de corpo configurado.

Alternativa considerada: passar a mutação diretamente pela página. Foi rejeitada
porque duplicaria configuração HTTP e validações já centralizadas no cliente.

### Exigir habilitação explícita da escrita

A implementação deverá usar uma flag separada
`XANO_PROFISSIONAL_ESPECIALIDADES_WRITE_ENABLED`, com estado seguro padrão
`false`. A leitura continuará controlada pela flag já existente
`XANO_PROFISSIONAL_ESPECIALIDADES_API_ENABLED=true`.

A interface não deverá enviar POST ou DELETE quando a escrita estiver
desabilitada ou a configuração necessária estiver ausente.

Alternativa considerada: reutilizar a flag geral de escrita de Profissionais.
Foi rejeitada porque leitura e escrita de vínculos têm contratos separados e
devem poder ser habilitados independentemente.

### Gerenciar vínculos na página de Profissionais

Para o profissional selecionado, a página deverá carregar o catálogo de
Especialidades e os vínculos já existentes. Cada especialidade já vinculada
deverá ser exibida como vínculo atual e poderá ser removida após confirmação
explícita.

A criação deverá oferecer somente Especialidades existentes que ainda não estejam
vinculadas ao profissional selecionado. O frontend deverá recarregar os dados
após sucesso.

O campo textual legado poderá continuar sendo exibido e editado pelo CRUD atual,
mas não será usado para criar vínculos relacionais nem inferir especialidades.

### Prevenir duplicidades no frontend

Antes do POST, o cliente ou a página deverá impedir:

- IDs booleanos, zerados ou negativos;
- profissional inexistente no catálogo carregado;
- especialidade inexistente no catálogo carregado;
- par já existente na coleção de vínculos.

Essa validação melhora o feedback, mas não substitui unicidade ou integridade
do backend. A resposta HTTP do Xano deverá continuar prevalecendo como resultado
da operação.

Alternativa considerada: confiar integralmente no backend. Foi rejeitada porque
a interface precisa bloquear pares visivelmente duplicados e apresentar
validação clara antes da chamada.

### Invalidar cache após mutação

Após POST ou DELETE bem-sucedido, a implementação deverá limpar o cache da
consulta de vínculos. As leituras subsequentes deverão obter a coleção atualizada
no Xano. O cache não deverá ser invalidado por falha HTTP ou validação local.

### Mantener compatibilidade com Consultas

O GET continuará sendo a fonte autoritativa dos vínculos. Os identificadores
de Consultas continuarão sendo validados contra os catálogos e os pares existentes.
Criar ou remover vínculos não deverá alterar o campo textual legado nem migrar
dados automaticamente.

## Risks / Trade-offs

- [Uniquidade composta não confirmada] → validar duplicidade no frontend e
  tratar erro do backend; confirmar índice composto antes de afirmar garantia.
- [Integridade referencial não confirmada] → não presumir bloqueio de IDs
  inexistentes ou efeito de exclusões em outros registros; validar referências
  nos catálogos carregados e exigir validação backend aprovada.
- [DELETE não ter corpo configurado] → considerar 2xx compatível como sucesso
  e não exigir JSON.
- [Cache desatualizado] → invalidar explicitamente após sucesso e continuar
  mantendo TTL curto para leituras.
- [Remover vínculo usado por consultas existentes] → bloquear removals sem
  política aprovada ou validar com o backend antes da operação; não executar
  remoções reais nesta etapa.
- [Campo legado divergir do catálogo] → manter os dois conceitos separados e
  nunca derivar vínculos por comparação de nomes.

## Migration Plan

1. Implementar somente cliente e interface após a Change ser aprovada.
2. Executar testes locais com transporte HTTP simulado.
3. Desabilitar escritas por configuração no ambiente padrão.
4. Validar POST e DELETE com registros sintéticos somente em ambiente Xano
   não-live autorizado.
5. Confirmar e registrar unicidade composta e integridade referencial antes da
   habilitação da escrita.
6. Em caso de falha, desabilitar a flag de escrita e manter o GET e a página de
   Consultas operando conforme os contratos já confirmados.

## Open Questions

- A tabela Xano aplica unicidade composta para o par
  `(profissional_id, especialidade_id)`?
- Existem chaves estrangeiras ou restrições de integridade referencial para
  os dois IDs?
- A exclusão é permitida quando houver consultas dependentes?
