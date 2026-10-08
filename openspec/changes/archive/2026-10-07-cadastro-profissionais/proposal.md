# Proposal

## Why

O sistema já permite manter pacientes, mas ainda não possui um cadastro próprio para os profissionais que realizam atendimentos. Esse cadastro é uma dependência para disponibilidades e agendamentos futuros, que precisam referenciar uma entidade profissional estável.

## What Changes

- Criar uma capability independente para cadastro e gerenciamento básico de profissionais.
- Persistir identificador próprio gerado pelo sistema, nome obrigatório, telefone opcional, e-mail opcional e especialidade opcional.
- Disponibilizar criação, listagem, consulta individual, edição parcial e remoção de profissionais.
- Validar os dados no backend e limitar as respostas aos campos destinados ao consumidor da API.
- Permitir contatos compartilhados entre profissionais; o identificador próprio será a referência do registro.
- Manter a entidade profissional independente da tabela `user`; não criar autenticação ou vínculo com contas nesta Change.
- Manter disponibilidades, agendamentos e relacionamentos com pacientes fora do escopo.

## Capabilities

### New Capabilities

- `profissionais`: cadastro e gerenciamento básico de profissionais, com identificação, contato e especialidade.

### Modified Capabilities

Nenhuma.

## Impact

- Backend Xano/XanoScript: nova tabela e operações de API para profissionais.
- Contrato da API: novas entradas, respostas e erros de validação e de não encontrado.
- Dados existentes: a tabela e as APIs de `user` e `paciente` não serão modificadas.
- Dependências futuras: disponibilidades e agendamentos poderão referenciar profissionais em Changes posteriores; nenhum relacionamento será criado agora.
- Remoção: a exclusão física é aceitável enquanto não houver registros dependentes; a estratégia deverá ser reavaliada antes de criar disponibilidades ou agendamentos vinculados.