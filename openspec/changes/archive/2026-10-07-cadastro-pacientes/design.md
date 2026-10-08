# Design

## Context

Ver [proposal.md - Why](proposal.md#why) para a motivação e [specs/pacientes/spec.md](specs/pacientes/spec.md) para o contrato de comportamento.

O Xano é o backend previsto no projeto. As validações de dados e as regras de integridade deverão ser aplicadas no backend.

Esta change está limitada ao cadastro e gerenciamento de pacientes e não cria relações com profissionais, disponibilidades ou agendamentos.

## Goals / Non-Goals

**Goals:**

- Persistir os dados mínimos necessários para identificar e contatar um paciente.
- Manter as validações e regras de integridade no backend.
- Disponibilizar operações de criação, consulta, edição e remoção de pacientes.
- Manter as respostas da API limitadas aos dados básicos previstos na spec.
- Manter a implementação preparada para futuras relações com outras entidades sem criá-las nesta change.

**Non-Goals:**

- Definir cadastro de profissionais, disponibilidades ou agendamentos.
- Criar relacionamentos entre pacientes e outras entidades.
- Coletar documentos de identificação, dados clínicos ou outros dados além de nome, telefone e e-mail.
- Criar autenticação, papéis, permissões ou novos fluxos de interface.
- Definir regras de histórico de atendimentos.

## Decisions

### 1. Modelo mínimo de paciente

Cada paciente terá um identificador próprio gerado pelo sistema.

O modelo inicial deverá possuir:

- identificador próprio;
- nome obrigatório;
- telefone opcional;
- e-mail opcional.

No cadastro inicial, o nome não poderá estar vazio nem conter somente espaços.

Telefone e e-mail, quando fornecidos, deverão atender aos critérios de validação definidos nesta change.

CPF e outros identificadores pessoais ficam fora desta change por não serem necessários ao escopo atualmente definido.

**Alternativa considerada:** exigir um identificador civil ou tornar todos os dados de contato obrigatórios.

Essa alternativa aumentaria a coleta de informações sem existir requisito de negócio que a justifique neste momento.

### 2. Sem deduplicação por dados de contato

Nome, telefone e e-mail não serão tratados como chaves únicas.

Pacientes diferentes poderão possuir dados coincidentes, como telefone compartilhado ou e-mail compartilhado.

Cada registro será identificado pelo identificador próprio gerado pelo sistema.

A API não rejeitará um cadastro somente porque nome, telefone ou e-mail também aparecem em outro registro.

**Alternativa considerada:** impor unicidade de e-mail ou telefone.

Essa alternativa poderia impedir cadastros legítimos e não existe regra de negócio aprovada que exija essa restrição.

### 3. Validações no backend

As validações de campos, existência do paciente e integridade das operações deverão ser executadas no backend Xano.

O frontend não deverá ser considerado responsável por garantir a integridade dos dados.

Para telefone, quando informado, serão permitidos:

- dígitos;
- espaços;
- parênteses;
- hífen;
- sinal `+` somente no início.

Após remover os caracteres de formatação, o telefone deverá possuir entre 8 e 15 dígitos.

O e-mail utilizará o tipo nativo de e-mail do Xano.

As respostas da API deverão expor somente:

- identificador;
- nome;
- telefone;
- e-mail.

Campos internos da persistência que não sejam necessários ao consumidor da API não deverão ser expostos.

### 4. Edição parcial de pacientes

O PATCH deverá preservar campos não enviados.

Durante os testes reais no Xano, foi identificado que a API tipada pode normalizar um nome vazio da mesma forma que um campo ausente, impossibilitando distinguir esses dois casos de maneira confiável no XanoScript com o contrato atual.

Por isso, nesta change:

- nome ausente ou vazio no PATCH preservará o valor atual;
- nome válido atualizará o paciente;
- telefone e e-mail ausentes preservarão os valores existentes;
- telefone e e-mail enviados vazios poderão ser removidos;
- o identificador do paciente permanecerá imutável.

Essa decisão mantém o contrato simples e evita adicionar campos auxiliares apenas para indicar presença de propriedades.

### 5. Autorização fora do escopo desta change

Esta change não implementará autenticação, papéis ou permissões.

Quando o projeto possuir um mecanismo de autenticação e autorização definido, as operações relacionadas a pacientes deverão respeitar as políticas de acesso correspondentes no backend.

A ausência de autenticação nesta change não deverá ser interpretada como definição permanente de acesso público aos dados dos pacientes.

### 6. Remoção física no escopo atual

Nesta change, a remoção de um paciente excluirá o registro persistido.

Após a remoção, consultas utilizando aquele identificador deverão retornar paciente não encontrado.

Essa decisão é válida para o escopo atual porque ainda não existem relações com agendamentos, atendimentos ou outros registros históricos.

Antes da criação de funcionalidades que dependam do histórico do paciente, a estratégia de remoção deverá ser reavaliada.

**Alternativa considerada:** utilizar inativação lógica desde o início.

Essa alternativa adicionaria estado e regras de consulta sem existir requisito correspondente nesta etapa do projeto.

## Risks / Trade-offs

- **Contato compartilhado ou repetido:** a ausência de deduplicação pode permitir cadastros redundantes. O identificador próprio deverá ser utilizado como referência e uma política de deduplicação somente deverá ser criada caso surja uma regra de negócio que a justifique.

- **Exclusão irreversível:** a remoção física não preserva histórico. Como ainda não existem relacionamentos nesta change, a decisão é aceitável no escopo atual. Antes de relacionar pacientes a agendamentos ou atendimentos, a estratégia de retenção deverá ser reavaliada.

- **Dados pessoais:** pacientes possuem informações pessoais de identificação e contato. As respostas da API deverão ficar limitadas aos campos necessários e futuras regras de acesso deverão ser aplicadas no backend.

- **Normalização de inputs no PATCH:** o comportamento tipado do Xano pode normalizar um nome vazio da mesma forma que um campo omitido. Nesta change, ambos os casos serão tratados como preservação do nome atual.

- **Validação de telefone:** a implementação depende da interpretação correta de regex no XanoScript. Durante os testes, foi necessário ajustar a expressão utilizada para aceitar corretamente números com sinal `+` e formatação.

## Migration Plan

A implementação deverá criar a estrutura de persistência necessária para pacientes e as respectivas operações de API.

A tabela e as APIs existentes de `user` não deverão ser modificadas por esta change.

Não existe migração de pacientes existentes prevista, pois o projeto ainda não possui estrutura anterior para essa entidade.

Caso seja necessário desfazer esta change antes de existirem funcionalidades dependentes, as novas operações poderão ser removidas e a estrutura de pacientes poderá ser descontinuada de acordo com a situação dos dados existentes no ambiente.