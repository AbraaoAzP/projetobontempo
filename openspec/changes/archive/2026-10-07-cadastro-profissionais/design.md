# Design

## Context

Ver [proposal.md - Why](proposal.md#why) e [specs/profissionais/spec.md](specs/profissionais/spec.md) para motivação e contrato observável.

O Xano é o backend e a tabela `paciente` já estabelece o padrão local de identificador próprio, campos básicos e APIs por grupo. A tabela `user` existe para outro propósito e não será usada como cadastro de profissionais.

## Goals / Non-Goals

**Goals:**

- Persistir profissionais em entidade própria, com campos mínimos e sem chave única baseada em dados pessoais.
- Aplicar validações e regras de integridade no backend.
- Expor operações CRUD com respostas limitadas aos campos da capability.
- Implementar PATCH parcial com preservação de campos omitidos e sem alteração do ID.

**Non-Goals:**

- Vincular profissional a `user`, conta, credencial ou mecanismo de autenticação.
- Criar disponibilidades, agendamentos, pacientes-profissionais ou regras de conflito de agenda.
- Definir catálogo controlado de especialidades, documentos civis ou histórico profissional.
- Alterar as APIs/tabela de `user` ou a capability `pacientes`.

## Decisions

### 1. Entidade e identificador independentes

Criar tabela própria `profissional`, com ID gerado pelo Xano como chave primária. Nome, telefone, e-mail e especialidade não serão únicos. Reutilizar `user` foi rejeitado porque conta de acesso e profissional são conceitos diferentes e autenticação está fora do escopo.

### 2. Campos e normalização

Usar nome obrigatório com trim; telefone e e-mail opcionais; especialidade como texto opcional. O e-mail usa o tipo nativo `email` do Xano. Não introduzir limites de tamanho ou formatos além dos definidos na spec.

### 3. Validação de telefone

Manter o contrato já usado em pacientes: dígitos, espaços, parênteses e hífen; `+` apenas no início; de 8 a 15 dígitos reais após remover formatação. A reutilização da função existente `validar_telefone_paciente` é uma decisão consciente nesta Change: mantém a regra de validação já estabelecida, com `inputerror` local nos endpoints antes de gravar. O acoplamento da capability `profissionais` a uma função com nome centrado em pacientes é conhecido; nenhuma nova abstração será criada nesta Change. Se outras entidades também precisarem dessa regra, uma refatoração futura poderá torná-la compartilhada e neutra.

### 4. APIs e PATCH parcial

Organizar endpoints no grupo `Profissionais`, com operações de cadastro, listagem, consulta por ID, PATCH e DELETE seguindo os padrões atuais de XanoScript. Respostas terão ID, nome, telefone, e-mail e especialidade.

PATCH usará sentinelas para distinguir campo omitido de campo enviado. Nome ausente ou vazio preserva o valor atual; telefone, e-mail e especialidade omitidos preservam os valores, e enviados vazios removem o valor conforme a spec. Validar todos os valores enviados antes de executar `db.patch`; nunca incluir o ID do corpo nos campos persistidos.

### 5. Remoção nesta fase

Usar remoção física, com verificação de existência e `notfound` antes da exclusão. Essa escolha é compatível enquanto não houver disponibilidades ou agendamentos dependentes; a estratégia deve ser revista antes de criar essas relações.

### 6. Erros e gravações

Aplicar preconditions `inputerror` nos endpoints para validações de nome e resultado inválido do telefone, e tratar inexistência como `notfound`. Fazer validação antes de `db.add`/`db.patch` para evitar gravações parciais. Não implementar autenticação nesta Change; isso não define acesso público permanente.

## Risks / Trade-offs

- **Reutilização de função com nome paciente-específico** → evita duplicar regras agora; registrar a limitação e não renomear a função arquivada nesta Change.
- **Contatos não únicos** → compartilhamento legítimo é permitido; usar somente o ID como referência.
- **Remoção física** → não há histórico/relacionamentos nesta fase; reavaliar antes de dependências futuras.
- **Dados pessoais sem autorização** → manter respostas mínimas e definir autorização backend antes de disponibilizar o sistema para uso real.

## Migration Plan

Não há migração prevista: a capability é nova e não haverá conversão de registros de `user`. Implementar e validar os artefatos no Xano após revisão da Change. Se a implantação precisar ser revertida antes de dependências futuras, remover somente os novos endpoints e a tabela `profissional`, preservando `user` e `paciente`.
