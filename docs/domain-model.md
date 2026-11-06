# Domain Model — Sistema de Gestão de Consultório

## 1. Visão geral do domínio

O sistema tem como objetivo organizar a administração do consultório e apoiar os atendimentos médicos, com controle de acesso por perfil.

Os conceitos-alvo aprovados são:

- Paciente
- Médico (Profissional)
- Conta de usuário e perfil de acesso
- Especialidade
- Disponibilidade
- Consulta
- Prontuário
- Registro de Atendimento
- Status da Consulta

Esse modelo descreve o escopo aprovado, não a implementação atual. As regras e cardinalidades identificadas como pendentes precisam de decisão antes de alterações de schema.

---

## 2. Paciente

Representa a pessoa que receberá atendimento no consultório.

### Principais informações

- nome;
- dados de identificação;
- dados de contato;
- informações necessárias para realização do atendimento;
- prontuário longitudinal, quando criado.

### Responsabilidade

O paciente deve possuir um cadastro no sistema para poder ser relacionado a um agendamento.

### Relacionamentos

- um paciente pode possuir várias consultas;
- cada consulta pertence a um único paciente;
- um paciente pode possuir zero ou um prontuário, conforme a decisão já registrada na Change de modelo clínico.

---

## 3. Profissional

Representa exclusivamente um médico, responsável por realizar atendimentos no consultório.

### Principais informações

- nome;
- dados de identificação;
- dados de contato;
- uma ou mais especialidades do catálogo;
- conta de usuário com perfil Médico vinculada ao respectivo registro profissional.

### Responsabilidade

O médico representa quem executará o atendimento agendado. A associação com especialidades é N:N; durante a transição, um médico pode não ter especialidade vinculada. Uma consulta só pode usar uma especialidade efetivamente vinculada ao médico.

### Relacionamentos

- um médico pode possuir várias consultas;
- cada consulta deverá estar relacionada a um único médico;
- cada conta Médico deverá estar vinculada ao respectivo médico; cardinalidade e unicidade ainda precisam de decisão.

---

## 4. Conta de usuário e perfil

Representa a identidade autenticada de uma pessoa que acessa o sistema. Os perfis aprovados são Admin e Médico. A tabela Xano `user` existente poderá ser reutilizada se a revisão técnica confirmar que suporta autenticação, perfil e controles necessários.

O perfil Médico deve estar relacionado ao registro Profissional correspondente. O mecanismo de autenticação, o armazenamento seguro de credenciais, o provisionamento de contas, a unicidade e o ciclo de vida do vínculo ainda precisam ser especificados.

Autenticação e autorização devem ser verificadas pelo Xano em cada endpoint protegido. Ocultar opções no Streamlit não concede nem restringe autorização.

---

## 5. Disponibilidade

Representa os dias e horários em que um médico poderá realizar atendimentos, caso essa regra seja mantida no escopo detalhado.

### Principais informações

- profissional relacionado;
- dia ou data de atendimento;
- horário inicial;
- horário final ou horários disponíveis;
- situação da disponibilidade.

### Responsabilidade

A disponibilidade deverá informar quando um determinado profissional poderá receber agendamentos.

Embora conste no modelo anterior, a disponibilidade não está entre os módulos funcionais aprovados nesta revisão. Seu uso e representação ainda precisam de confirmação; não se deve inferir que já exista no backend.

### Relacionamentos

- uma disponibilidade pertence a um profissional;
- um profissional pode possuir várias disponibilidades;
- seu papel na validação de consultas ainda precisa ser confirmado.

---

## 6. Especialidade

Representa uma especialidade médica catalogada e reutilizável. Médicos e especialidades se relacionam em cardinalidade N:N, com possibilidade de zero vínculos por médico durante a transição. O mesmo par médico–especialidade não pode ser duplicado. Uma consulta exige vínculo entre o médico e a especialidade selecionada.

O campo textual legado de especialidade em Profissional deve ser preservado até que a reconciliação com o catálogo seja especificada e aprovada.

---

## 7. Consulta

Representa o agendamento e o estado de uma reserva de horário para atendimento de um paciente por um médico.

### Principais informações

- paciente;
- médico;
- especialidade vinculada ao médico;
- data e horário do atendimento;
- status controlado.

Uma consulta relaciona um paciente, um médico e uma especialidade válida em determinada data e horário. Cada consulta pertence a um paciente e a um médico. Uma consulta agendada pode existir sem registro clínico.

Regras de duração, conflitos, fuso horário, catálogo de status e transições ainda precisam ser aprovadas antes da implementação.

---

## 8. Status da Consulta

Representa o estado atual controlado da consulta. O conjunto de valores, status inicial, transições, necessidade de histórico e quais status ocupam um horário precisam de decisão antes da implementação no Xano. A definição das métricas “agendadas”, “realizadas” e “não realizadas” também depende dessa política.

---

## 9. Prontuário e Registro de Atendimento

O Prontuário organiza o histórico longitudinal de um paciente e está vinculado a ele. O paciente pode existir sem prontuário; a cardinalidade de prontuário–registros deve ser confirmada antes de criar restrições físicas.

Registro de Atendimento contém diagnóstico, anotações clínicas e conduta; esses dados não devem ser duplicados na Consulta. Uma consulta realizada pode gerar no máximo um registro clínico associado à consulta e ao prontuário do paciente, conforme decisão já registrada na Change. O registro deve preservar autoria do médico que realizou o atendimento. O backend deve confirmar que o médico autenticado está vinculado à consulta realizada antes de aceitar o registro.

Admin pode listar, cadastrar, editar e excluir prontuários conforme política de retenção e integridade aprovada. O Médico só pode consultar dados necessários aos próprios atendimentos e registrar atendimento de paciente efetivamente atendido por ele; não recebe funções administrativas de prontuário. Campos clínicos, alteração/exclusão, auditoria e retenção precisam de definição de acesso e proteção antes de disponibilizar dados.

---

## 10. Dashboards por perfil

- Admin: quantidades de pacientes e médicos, consultas agendadas, consultas do dia, realizadas e não realizadas.
- Médico: quantidade e horários das próprias consultas do dia e os dados de paciente necessários aos atendimentos.

Período, fuso horário, definição das categorias de status e tratamento de cancelamentos/faltas são pendências de domínio e não devem ser inferidos no frontend.

---

## 11. Relacionamentos principais

Paciente 1 --- 0..1 Prontuário
Prontuário --- [cardinalidade pendente] --- Registro de Atendimento
Paciente 1 --- 0..N Consulta N..1 Médico
Médico N --- N Especialidade
Conta Médico --- Médico (cardinalidade/unicidade pendentes)
Consulta 1 --- 0..1 Registro de Atendimento (quando realizada)
Consulta N --- 1 Status da Consulta (regra candidata; confirmar catálogo e integridade)

- Paciente possui consultas e, opcionalmente, um prontuário;
- Médico possui consultas e vínculos com especialidades;
- Consulta relaciona paciente, médico e especialidade;
- Registro de Atendimento preserva paciente, consulta e médico autor;
- Conta Médico é vinculada ao registro profissional correspondente;
- permissões por perfil são impostas pelo backend.

---

## 12. Regras estruturais importantes

- toda consulta deverá referenciar paciente, médico, especialidade vinculada, data/hora e status válido;
- o backend deverá impedir conflitos de agenda conforme política de status aprovada;
- Admin pode gerenciar os módulos administrativos;
- Médico acessa somente sua agenda e dados necessários aos atendimentos autorizados;
- somente o médico autenticado que efetivamente realizou a consulta pode registrar sua autoria no atendimento;
- nenhuma autorização dependerá somente da interface Streamlit;
- os ambientes de demonstração devem utilizar dados exclusivamente fictícios;
- políticas de exclusão e retenção não podem causar perda ou orfandade de histórico clínico.

---

## 13. Observação sobre implementação

Este documento representa o modelo-alvo conceitual e suas pendências, não o schema atualmente implementado.

O estado observado no Xano contém `user`, `paciente` e `profissional`; não foram identificadas entidades remotas de especialidade, consulta, status, prontuário ou atendimento. No frontend, Especialidades e Consultas ainda dependem do SQLite temporário. A existência de tabela `user` não comprova autenticação nem autorização por perfil.

A arquitetura definitiva utiliza Xano/XanoScript e APIs HTTP; SQLite deve ser removido somente após a migração e validação dos módulos que ainda dependem dele. Cardinalidades, status, regra “não realizada”, janela dos dashboards, associação de conta Médico, retenção e políticas detalhadas de acesso devem ser decididas antes da implementação correspondente.