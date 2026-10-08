# profissionais Specification

## Purpose

Definir o comportamento observável para cadastrar e gerenciar profissionais do consultório, com identificação própria e dados básicos de contato, preparando referências futuras sem criar vínculos com usuários, disponibilidades ou agendamentos.

## Requirements

### Requirement: Cadastrar profissional

O sistema SHALL permitir cadastrar um profissional com nome e dados básicos opcionais de contato e especialidade.

O nome SHALL ser obrigatório e não poderá estar vazio nem conter somente espaços.

Telefone, e-mail e especialidade poderão ser informados. Quando presentes, telefone e e-mail deverão respeitar os critérios de validação definidos nesta capability.

O sistema SHALL atribuir ao profissional um identificador próprio, sem utilizar dados pessoais como identificador.

#### Scenario: Cadastro válido

- **WHEN** uma solicitação de cadastro contém nome válido e dados opcionais ausentes ou válidos
- **THEN** o sistema persiste o profissional e retorna seu identificador e os dados básicos cadastrados

#### Scenario: Cadastro com nome ausente ou inválido

- **WHEN** uma solicitação de cadastro não contém nome ou contém nome vazio ou somente espaços
- **THEN** o sistema rejeita a solicitação com erro de validação e não persiste o profissional

#### Scenario: Cadastro com contato inválido

- **WHEN** uma solicitação contém telefone ou e-mail que não atende aos critérios de validação definidos
- **THEN** o sistema rejeita a solicitação com erro de validação e não persiste o profissional

### Requirement: Consultar profissionais

O sistema SHALL permitir listar profissionais cadastrados e consultar um profissional individualmente pelo identificador.

As respostas SHALL incluir somente os campos destinados ao consumidor da API: identificador, nome, telefone, e-mail e especialidade.

Campos internos ou não destinados ao consumidor SHALL ser omitidos.

#### Scenario: Listar profissionais cadastrados

- **WHEN** uma solicitação válida pede a lista de profissionais
- **THEN** o sistema retorna os profissionais cadastrados com os campos permitidos, incluindo uma lista vazia quando não houver registros

#### Scenario: Consultar profissional existente

- **WHEN** uma solicitação válida informa o identificador de um profissional existente
- **THEN** o sistema retorna os dados permitidos daquele profissional

#### Scenario: Consultar profissional inexistente

- **WHEN** uma solicitação informa um identificador sem profissional correspondente
- **THEN** o sistema retorna erro de não encontrado sem expor dados de outros profissionais

### Requirement: Editar profissional

O sistema SHALL permitir editar nome, telefone, e-mail e especialidade de um profissional existente.

Campos não enviados SHALL preservar seus valores atuais.

Um nome válido enviado SHALL atualizar o nome. Nome ausente ou vazio no PATCH SHALL preservar o nome atual.

Telefone, e-mail e especialidade enviados com valores válidos SHALL atualizar os respectivos campos. Telefone, e-mail ou especialidade enviados vazios SHALL permitir remover o valor correspondente.

A edição não poderá alterar o identificador do profissional.

#### Scenario: Editar dados válidos

- **WHEN** uma solicitação válida atualiza um ou mais campos de um profissional existente
- **THEN** o sistema persiste as alterações, preserva os campos não enviados e retorna os dados permitidos atualizados

#### Scenario: Preservar nome ausente ou vazio

- **WHEN** uma solicitação de edição não envia o nome ou envia nome vazio
- **THEN** o sistema preserva o nome atual do profissional

#### Scenario: Remover dados opcionais

- **WHEN** uma solicitação de edição envia telefone, e-mail ou especialidade como valor vazio
- **THEN** o sistema remove o valor correspondente sem alterar os demais campos

#### Scenario: Editar profissional inexistente

- **WHEN** uma solicitação de edição informa um identificador sem profissional correspondente
- **THEN** o sistema retorna erro de não encontrado e não cria um profissional

### Requirement: Remover profissional

O sistema SHALL permitir remover fisicamente um profissional existente pelo identificador enquanto não houver registros dependentes nesta capability.

O sistema não poderá remover outro registro quando o identificador informado não existir.

#### Scenario: Remover profissional existente

- **WHEN** uma solicitação válida remove um profissional existente
- **THEN** o sistema confirma a remoção e o profissional deixa de aparecer nas consultas posteriores

#### Scenario: Remover profissional inexistente

- **WHEN** uma solicitação de remoção informa um identificador sem profissional correspondente
- **THEN** o sistema retorna erro de não encontrado

### Requirement: Validar dados de profissionais no backend

O sistema SHALL validar no backend os campos e a existência do profissional nas operações por identificador.

Falhas SHALL retornar erros consistentes e não poderão persistir dados inválidos nem deixar alterações parciais.

Para telefone, quando informado, serão aceitos dígitos, espaços, parênteses e hífen, além de um sinal `+` somente no início. Após remover a formatação, o telefone deverá possuir entre 8 e 15 dígitos reais.

O e-mail SHALL utilizar a validação de tipo de e-mail disponibilizada pelo Xano.

Especialidade será texto opcional; esta capability não define catálogo controlado de especialidades.

#### Scenario: Rejeitar entrada inválida sem persistência parcial

- **WHEN** uma operação de criação ou edição contém nome, telefone ou e-mail inválido
- **THEN** o sistema retorna erro de validação e mantém os dados persistidos sem alterações parciais

### Requirement: Não deduplicar profissionais por dados compartilháveis

O sistema SHALL permitir o cadastro de profissionais com nome, telefone, e-mail ou especialidade coincidentes, mantendo IDs distintos.

#### Scenario: Permitir dados coincidentes

- **WHEN** um novo profissional informa nome, telefone, e-mail ou especialidade coincidentes com outro cadastro
- **THEN** o sistema aceita o novo cadastro e atribui identificador próprio distinto
